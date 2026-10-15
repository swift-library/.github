# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Exercise baseline trust, reporting and release evidence identity."""

import importlib.util
from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('api_evidence', ROOT / 'Scripts/api-evidence.py')
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)
REPOSITORY = 'example/package'
COMMIT = 'a' * 40
OTHER = 'b' * 40


def complete(commit=COMMIT):
    return api.envelope(REPOSITORY, commit, 'complete', 'Collected',
                        {'schemaVersion': '1.0', 'configurations': [{'id': 'configuration',
                         'configuration': {'extractorVersion': api.TOOL['version']}}]})


class Release:
    repository = REPOSITORY

    def __init__(self, value=None, evidence=None):
        self.value = value
        self.evidence = evidence

    def latest(self):
        return self.value

    def commit(self, tag):
        return COMMIT

    def asset(self, asset):
        return self.evidence


def published(assets=None, **fields):
    return {'id': 1, 'tag_name': 'v0.1.0', 'draft': False, 'prerelease': False,
            'assets': [{'name': api.ASSET, 'id': 2, 'digest': 'sha256:' + 'c' * 64}]
            if assets is None else assets, **fields}


class APIEvidenceTests(unittest.TestCase):
    def setUp(self):
        parent = ROOT / '.build/test-fixtures'
        parent.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_missing_baselines_are_unknown_not_equal(self):
        for release in (None, published(assets=[])):
            prior, identity = api.baseline(Release(release))
            self.assertIsNone(prior)
            self.assertEqual(identity['status'], 'missing')
            result = api.compare(complete(), prior, identity, None, self.root, self.root, self.root / 'log')
            self.assertEqual(result['status'], 'unavailable')
            self.assertEqual(result['mode'], 'report-only')
            self.assertNotIn('counts', result)

    def test_release_identity_must_match_asset(self):
        prior, identity = api.baseline(Release(published(), complete()))
        self.assertEqual(prior['commit'], identity['commit'])
        self.assertEqual(identity['tag'], 'v0.1.0')
        self.assertEqual(identity['asset_digest'], 'sha256:' + 'c' * 64)
        for value in (complete(OTHER), {**complete(), 'repository': 'another/package'},
                      {**complete(), 'schema_version': 2}, {**complete(), 'evidence': None}):
            with self.subTest(value=value), self.assertRaises(api.Unavailable):
                api.baseline(Release(published(), value))

    def test_drafts_prereleases_and_ambiguous_assets_are_rejected(self):
        for value in (published(draft=True), published(prerelease=True),
                      published(assets=[{'name': api.ASSET}, {'name': api.ASSET}])):
            with self.subTest(value=value), self.assertRaises(api.Unavailable):
                api.baseline(Release(value, complete()))

    def test_public_api_requests_use_json_without_a_token(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(api, 'read_url', return_value=b'{}') as download:
            self.assertEqual(api.GitHub(REPOSITORY).get('/releases/latest'), {})
            self.assertEqual(download.call_args.kwargs['accept'], 'application/vnd.github+json')

    def test_asset_origin_and_digest_are_verified(self):
        content = b'{"schema_version":1}'
        value = {'browser_download_url': 'https://github.com/example/package/releases/download/v0.1.0/api-evidence.json',
                 'digest': 'sha256:' + api.hashlib.sha256(content).hexdigest()}
        client = api.GitHub(REPOSITORY)
        with patch.object(api, 'read_url', return_value=content):
            self.assertEqual(client.asset(value), {'schema_version': 1})
            for changed in ({**value, 'digest': None}, {**value, 'digest': 'sha256:' + '0' * 64},
                            {**value, 'browser_download_url': 'https://example.invalid/asset'}):
                with self.subTest(changed=changed), self.assertRaises(api.Unavailable):
                    client.asset(changed)

    def test_incomplete_collections_cannot_report_equality(self):
        for status in ('failed', 'incomplete'):
            value = api.envelope(REPOSITORY, COMMIT, status)
            for candidate, prior in ((value, complete()), (complete(), value)):
                result = api.compare(candidate, prior, {}, None, self.root, self.root, self.root / 'log')
                self.assertEqual(result['status'], 'unavailable')
                self.assertNotIn('difference', result)

    def compare_difference(self, difference):
        def execute(arguments, *args, **kwargs):
            api.write(Path(arguments[-1]), difference)
            return 1
        with patch.object(api, 'run', side_effect=execute):
            return api.compare(complete(OTHER), complete(), {'tag': 'v0.1.0'},
                               'collector', self.root, self.root, self.root / 'log')

    def test_field_categories_and_additions_remain_observations(self):
        difference = {'added': ['new'], 'removed': ['old'], 'incomparableConfigurations': [],
                      'changes': [{'category': category, 'path': '/fields/value'}
                                  for category in ('interface', 'documentation', 'availability', 'provenance')]}
        result = self.compare_difference(difference)
        self.assertEqual(result['status'], 'changed')
        self.assertEqual(result['counts'], {'added': 1, 'removed': 1, 'interface': 1,
                                           'documentation': 1, 'availability': 1, 'provenance': 1})
        self.assertEqual(result['difference'], difference)
        self.assertNotIn('version', result)
        self.assertIn('no version or compatibility decision', api.summary(result))

    def test_toolchain_and_scope_changes_are_incomparable(self):
        for difference in (
            {'added': [], 'removed': [], 'changes': [], 'incomparableConfigurations': ['different-toolchain']},
            {'added': [], 'removed': [], 'incomparableConfigurations': [],
             'changes': [{'category': 'provenance', 'path': '/scope'}]},
        ):
            self.assertEqual(self.compare_difference(difference)['status'], 'incomparable')
        self.assertEqual(self.compare_difference({'added': [], 'removed': [], 'changes': [],
                                                 'incomparableConfigurations': []})['status'], 'equal')

    def test_collection_failure_still_writes_a_source_bound_report(self):
        with patch.object(api, 'baseline', return_value=(None, {'status': 'missing'})), \
                patch.object(api, 'tool', side_effect=api.Unavailable('Compiler unavailable')), \
                patch.dict(os.environ, {}, clear=True):
            api.report(self.root, REPOSITORY, COMMIT)
        output = self.root / '.build/api-evidence'
        evidence = json.loads((output / api.ASSET).read_text())
        result = json.loads((output / 'api-report.json').read_text())
        self.assertEqual(evidence['commit'], COMMIT)
        self.assertEqual(evidence['status'], 'failed')
        self.assertIsNone(evidence['evidence'])
        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(result['reason'], 'Compiler unavailable')

    def test_comparison_never_mixes_collector_versions(self):
        old = complete()
        old['collector'] = {**api.TOOL, 'version': '0.0.1'}
        with patch.object(api, 'run') as execute:
            result = api.compare(complete(OTHER), old, {}, 'collector', self.root, self.root, self.root / 'log')
            self.assertEqual(result['status'], 'unavailable')
            execute.assert_not_called()
        old = complete()
        old['evidence']['configurations'][0]['configuration']['extractorVersion'] = '0.0.1'
        self.assertFalse(api.collector_matches(old))

    def test_baseline_recollection_binds_to_verified_release_commit(self):
        prior = complete()
        prior['collector'] = {**api.TOOL, 'version': '0.0.1'}
        identity = {'tag': 'v0.1.0', 'commit': COMMIT, 'asset_id': 2, 'source': 'release-asset'}
        with patch.object(api, 'run') as execute, patch.object(api, 'collect', return_value=complete()) as collect:
            value, provenance = api.recollect(prior, identity, 'collector', self.root, self.root, self.root)
            self.assertEqual(value, complete())
            self.assertEqual(provenance['source'], 'recollected-release-tag')
            self.assertEqual(provenance['attached_collector']['version'], '0.0.1')
            self.assertEqual(execute.call_args_list[1].args[0], ['git', 'checkout', '--detach', COMMIT])
            self.assertEqual(collect.call_args.args[-1], COMMIT)
            self.assertEqual(collect.call_args.args[1], self.root / 'baseline-source')
            self.assertIn('recollected from v0.1.0', api.summary({'status': 'equal', 'baseline': provenance}))
        with patch.object(api, 'run') as execute:
            self.assertEqual(api.recollect(complete(), identity, None, self.root, self.root, self.root),
                             (complete(), identity))
            execute.assert_not_called()

    def test_failed_recollection_keeps_candidate_report_available(self):
        identity = {'tag': 'v0.1.0', 'commit': COMMIT}
        with patch.object(api, 'baseline', return_value=(complete(), identity)), \
                patch.object(api, 'recollect', side_effect=api.Unavailable('Release source cannot build')), \
                patch.object(api, 'collect', return_value=complete(OTHER)), \
                patch.dict(os.environ, {}, clear=True):
            api.report(self.root, REPOSITORY, OTHER, 'collector')
        result = json.loads((self.root / '.build/api-evidence/api-report.json').read_text())
        self.assertEqual(result['collection'], 'complete')
        self.assertEqual(result['status'], 'unavailable')
        self.assertEqual(result['baseline']['reason'], 'Release source cannot build')

    def test_release_preparation_preserves_verified_evidence_or_records_job_gap(self):
        api.prepare(self.root, REPOSITORY, COMMIT)
        output = self.root / '.build/release-validation' / api.ASSET
        self.assertEqual(json.loads(output.read_text())['status'], 'failed')
        source = self.root / '.build/ci-evidence' / ('api-evidence-' + COMMIT) / api.ASSET
        api.write(source, complete())
        api.prepare(self.root, REPOSITORY, COMMIT)
        self.assertEqual(json.loads(output.read_text()), complete())

        api.write(source, complete(OTHER))
        with self.assertRaises(api.Unavailable):
            api.prepare(self.root, REPOSITORY, COMMIT)
        self.assertEqual(json.loads(output.read_text()), complete())

    def cache_context(self, enabled=True):
        prior = complete()
        prior['collector'] = {**api.TOOL, 'version': '0.1.2'}
        identity = {'tag': 'v0.1.0', 'commit': COMMIT, 'asset_digest': 'sha256:' + 'c' * 64,
                    'source': 'release-asset'}
        inputs = {'schema_version': 1, 'repository': REPOSITORY, 'release_commit': COMMIT,
                  'attached_evidence_digest': identity['asset_digest'], 'collector': api.TOOL,
                  'runner_image': {'ImageOS': 'macos26', 'ImageVersion': 'image-1',
                                   'RUNNER_OS': 'macOS', 'RUNNER_ARCH': 'ARM64'},
                  'toolchain': {'xcode': 'Xcode build 1', 'swift': 'Swift build 1', 'sdk': '26.5'}}
        with patch.object(api, 'baseline', return_value=(prior, identity)), \
                patch.object(api, 'baseline_cache_inputs', return_value=inputs):
            api.prepare_baseline(self.root, REPOSITORY, OTHER, enabled)
        return prior, identity, inputs

    def cached_record(self, inputs, value=None):
        value = complete() if value is None else value
        return {'schema_version': 1, 'inputs': inputs, 'baseline': value,
                'baseline_sha256': api.content_digest(value)}

    def test_cache_key_separates_release_evidence_collector_image_and_toolchain(self):
        prior, identity, expected = self.cache_context()
        image = expected['runner_image']
        versions = {('xcodebuild', '-version'): 'Xcode build 1', ('swift', '--version'): 'Swift build 1',
                    ('xcrun', '--sdk', 'macosx', '--show-sdk-version'): '26.5'}
        def inputs(selected_identity=identity, selected_image=image, selected_versions=versions):
            with patch.dict(os.environ, selected_image, clear=True), \
                    patch.object(api.subprocess, 'check_output', side_effect=lambda command, **kwargs: selected_versions[tuple(command)]):
                return api.baseline_cache_inputs(prior, selected_identity)
        original = inputs()
        self.assertEqual(original, expected)
        key = api.baseline_cache_key(original)
        for field in ['commit', 'asset_digest']:
            changed = {**identity, field: OTHER if field == 'commit' else 'sha256:' + 'd' * 64}
            self.assertNotEqual(api.baseline_cache_key(inputs(selected_identity=changed)), key)
        for field in image:
            self.assertNotEqual(api.baseline_cache_key(inputs(selected_image={**image, field: 'another'})), key)
        for command in versions:
            self.assertNotEqual(api.baseline_cache_key(inputs(selected_versions={**versions, command: 'another'})), key)
        for field in ['version', 'commit', 'archive_sha256']:
            with patch.object(api, 'TOOL', {**api.TOOL, field: 'another'}):
                self.assertNotEqual(api.baseline_cache_key(inputs()), key)
        with self.assertRaises(api.Unavailable):
            inputs(selected_identity={**identity, 'asset_digest': None})

    def test_verified_cache_hit_avoids_release_recollection(self):
        prior, identity, inputs = self.cache_context()
        path = self.root / '.build/shared-api/baseline-cache/record.json'
        api.write(path, self.cached_record(inputs))
        with patch.object(api, 'recollect') as recollect:
            api.recollect_baseline(self.root, REPOSITORY, OTHER, Path('collector'))
            recollect.assert_not_called()
        context = api.baseline_context(self.root, REPOSITORY, OTHER)
        self.assertEqual(context['prior'], complete())
        self.assertEqual(context['identity']['attached_collector'], prior['collector'])
        self.assertEqual(context['identity']['source'], 'recollected-release-tag')
        self.assertEqual(context['cache']['status'], 'hit')
        self.assertGreaterEqual(context['cache']['seconds'], 0)

    def test_cache_rejects_changed_inputs_corruption_and_invalid_evidence(self):
        for fault in ['inputs', 'digest', 'commit', 'collector', 'incomplete', 'schema', 'invalid-json']:
            with self.subTest(fault=fault):
                prior, identity, inputs = self.cache_context()
                path = self.root / '.build/shared-api/baseline-cache/record.json'
                record = deepcopy(self.cached_record(inputs))
                if fault == 'inputs':
                    record['inputs']['toolchain']['swift'] = 'another'
                elif fault == 'digest':
                    record['baseline_sha256'] = '0' * 64
                elif fault == 'commit':
                    record['baseline'] = complete(OTHER)
                elif fault == 'collector':
                    record['baseline']['collector']['archive_sha256'] = '0' * 64
                elif fault == 'incomplete':
                    record['baseline']['status'] = 'incomplete'
                elif fault == 'schema':
                    record['schema_version'] = 2
                if fault in ('commit', 'collector', 'incomplete'):
                    record['baseline_sha256'] = api.content_digest(record['baseline'])
                api.write(path, record)
                if fault == 'invalid-json':
                    path.write_text('corrupt')
                with patch.object(api, 'recollect', return_value=(complete(), identity)) as recollect:
                    api.recollect_baseline(self.root, REPOSITORY, OTHER, Path('collector'))
                    self.assertEqual(recollect.call_args.args[:2], (prior, identity))
                self.assertEqual(api.baseline_context(self.root, REPOSITORY, OTHER)['cache']['status'], 'rejected')

    def test_cache_miss_writes_only_complete_release_bound_evidence(self):
        for status in ['complete', 'incomplete']:
            with self.subTest(status=status):
                prior, identity, inputs = self.cache_context()
                path = self.root / '.build/shared-api/baseline-cache/record.json'
                path.unlink(missing_ok=True)
                value = {**complete(), 'status': status}
                with patch.object(api, 'recollect', return_value=(value, identity)):
                    api.recollect_baseline(self.root, REPOSITORY, OTHER, Path('collector'))
                self.assertEqual(path.is_file(), status == 'complete')
                if path.is_file():
                    self.assertEqual(api.read_cached_baseline(path, inputs), value)

    def test_release_validation_never_reads_or_writes_baseline_cache(self):
        prior, identity, inputs = self.cache_context(enabled=False)
        path = self.root / '.build/shared-api/baseline-cache/record.json'
        api.write(path, {'untrusted': True})
        original = path.read_bytes()
        with patch.object(api, 'read_cached_baseline') as read, \
                patch.object(api, 'recollect', return_value=(complete(), identity)) as recollect:
            api.recollect_baseline(self.root, REPOSITORY, OTHER, Path('collector'))
            read.assert_not_called()
            recollect.assert_called_once()
        self.assertEqual(path.read_bytes(), original)
        self.assertEqual(api.baseline_context(self.root, REPOSITORY, OTHER)['cache']['status'], 'disabled')

    def test_candidate_collection_uses_prepared_baseline_and_preserves_cache_receipt(self):
        prior, identity, inputs = self.cache_context()
        with patch.object(api, 'recollect', return_value=(complete(), identity)):
            api.recollect_baseline(self.root, REPOSITORY, OTHER, Path('collector'))
        with patch.object(api, 'baseline') as baseline, patch.object(api, 'recollect') as recollect, \
                patch.object(api, 'collect', return_value=complete(OTHER)) as collect, \
                patch.object(api, 'compare', return_value={'status': 'equal', 'collection': 'complete'}):
            api.report(self.root, REPOSITORY, OTHER, prepared=True)
            baseline.assert_not_called()
            recollect.assert_not_called()
            self.assertEqual(collect.call_args.args[-1], OTHER)
        report = json.loads((self.root / '.build/api-evidence/api-report.json').read_text())
        self.assertEqual(report['baseline_cache']['status'], 'miss')
        with self.assertRaises(api.Unavailable):
            api.baseline_context(self.root, REPOSITORY, COMMIT)

    def test_workflow_saves_release_baseline_before_executing_candidate(self):
        spec = importlib.util.spec_from_file_location('sync_api', ROOT / 'Scripts/sync-api-workflows.py')
        sync = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sync)
        job = sync.job()
        steps = ['      - name: Verify release baseline inputs',
                 '      - name: Restore recollected release baseline',
                 '      - name: Verify or recollect release baseline',
                 '      - name: Cache verified release baseline',
                 '      - name: Collect and compare public interfaces']
        self.assertEqual([job.index(step) for step in steps], sorted(job.index(step) for step in steps))
        self.assertIn("inputs.ref == '' && github.event_name != 'release' && !startsWith(github.ref, 'refs/tags/')", job)
        self.assertNotIn('restore-keys:', job)
        self.assertNotIn('uses: actions/cache', sync.publication())


if __name__ == '__main__':
    unittest.main()
