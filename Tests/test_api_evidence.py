# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Exercise baseline trust, reporting and release evidence identity."""

import importlib.util
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
            'assets': [{'name': api.ASSET, 'id': 2}] if assets is None else assets, **fields}


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
        for value in (complete(OTHER), {**complete(), 'repository': 'another/package'},
                      {**complete(), 'schema_version': 2}, {**complete(), 'evidence': None}):
            with self.subTest(value=value), self.assertRaises(api.Unavailable):
                api.baseline(Release(published(), value))

    def test_drafts_prereleases_and_ambiguous_assets_are_rejected(self):
        for value in (published(draft=True), published(prerelease=True),
                      published(assets=[{'name': api.ASSET}, {'name': api.ASSET}])):
            with self.subTest(value=value), self.assertRaises(api.Unavailable):
                api.baseline(Release(value, complete()))

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


if __name__ == '__main__':
    unittest.main()
