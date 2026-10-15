# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
from copy import deepcopy
import base64
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("settings", ROOT / "Scripts/check-settings.py")
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.declared, self.checks = settings.declaration((ROOT / "MAINTENANCE.md").read_text())

    def test_declaration_owns_required_checks_and_bypass(self):
        self.assertTrue(self.checks["swift-gyb"])
        branch, tag = settings.expected_rulesets(self.declared, ["policy / policy", "validate / result"])
        self.assertEqual(branch["bypass_actors"], [])
        self.assertEqual(tag["bypass_actors"], [])
        self.assertEqual(self.declared["merge"]["squash_merge_commit_message"], "BLANK")
        status = next(x for x in branch["rules"] if x["type"] == "required_status_checks")
        self.assertEqual([x["context"] for x in status["parameters"]["required_status_checks"]],
                         ["policy / policy", "validate / result"])

    def test_missing_or_ambiguous_declaration_fails(self):
        for text in ("# empty", "## GitHub Settings\nNo declaration"):
            with self.assertRaises(ValueError):
                settings.declaration(text)

    def test_metadata_drift_does_not_print_variable_values(self):
        findings = settings.compare("example.variable", "private-value", "declared-value")
        self.assertEqual(findings, ["example.variable: differs from declaration"])

    def test_ruleset_order_is_irrelevant_but_parameters_are_not(self):
        expected = settings.expected_rulesets(self.declared, ["a", "b"])[0]
        actual = deepcopy(expected)
        actual["rules"].reverse()
        self.assertEqual(settings.canonical_ruleset(actual), settings.canonical_ruleset(expected))
        actual["bypass_actors"] = [{"actor_type": "OrganizationAdmin", "bypass_mode": "always"}]
        self.assertNotEqual(settings.canonical_ruleset(actual), settings.canonical_ruleset(expected))

    def test_live_repository_contract_rejects_missing_checks(self):
        repository = {"name": "swift-gyb", "default_branch": "master"}
        with patch.object(settings, "gh", return_value=self.declared["merge"] | self.declared["workflow_token"]), \
                patch.object(settings, "check_actions", return_value=[]):
            findings = settings.check_repository(repository, self.declared, {})
        self.assertEqual(findings, ["repos/swift-library/swift-gyb: missing required-check declaration"])

    def test_only_explicit_unprotected_branch_response_means_absence(self):
        response = {"status": "404", "message": "Branch not protected"}
        failure = subprocess.CalledProcessError(1, ["gh"], output=json.dumps(response))
        with patch.object(settings, "gh", side_effect=failure):
            self.assertIsNone(settings.legacy_protection("repos/example/package", "master"))
        for response in ({"status": "404", "message": "Not Found"},
                         {"status": "403", "message": "Resource not accessible"}):
            failure = subprocess.CalledProcessError(1, ["gh"], output=json.dumps(response))
            with patch.object(settings, "gh", side_effect=failure):
                with self.assertRaises(subprocess.CalledProcessError):
                    settings.legacy_protection("repos/example/package", "master")

    def test_overlapping_legacy_rule_is_reported_despite_matching_rulesets(self):
        repository = {"name": "swift-gyb", "default_branch": "master"}
        branch, tag = settings.expected_rulesets(self.declared, self.checks["swift-gyb"])
        path = "repos/swift-library/swift-gyb"
        responses = {path: self.declared["merge"],
                     path + "/actions/permissions/workflow": self.declared["workflow_token"],
                     path + "/rulesets/1": branch, path + "/rulesets/2": tag}
        with patch.object(settings, "gh", side_effect=lambda url: responses[url]), \
                patch.object(settings, "check_actions", return_value=[]), \
                patch.object(settings, "collection", return_value=[{"id": 1}, {"id": 2}]), \
                patch.object(settings, "legacy_protection", return_value={"lock_branch": {"enabled": True}}):
            findings = settings.check_repository(repository, self.declared, self.checks)
        self.assertEqual(findings, [path + ".legacy_branch_protection: differs from declaration"])

    def test_pin_report_lists_content_drift_and_excludes_forks(self):
        target = 'a' * 40
        repositories = [{'name': name, 'fork': fork, 'default_branch': 'master'}
                        for name, fork in [('current', False), ('outdated', False), ('fork', True), ('local', False)]]
        callers = {'current': [{'workflow': '.github/workflows/ci.yml', 'ref': target}],
                   'outdated': [{'workflow': '.github/workflows/ci.yml', 'ref': 'b' * 40},
                                {'workflow': '.github/workflows/source-policy.yml', 'ref': target}],
                   'local': []}
        with patch.object(settings, 'gh', return_value={'sha': target}), \
                patch.object(settings, 'collection', return_value=repositories), \
                patch.object(settings, 'shared_callers', side_effect=lambda org, repository: callers[repository['name']]), \
                patch.object(settings, 'shared_surface', side_effect=lambda org, ref: {
                    '.github/workflows/policy.yml': ('100644', 'blob', ref)}):
            report = settings.pin_drift(self.declared)
        self.assertEqual(report['target'], target)
        self.assertEqual(report['repositories_with_callers'], 2)
        self.assertEqual(report['caller_count'], 3)
        self.assertEqual(report['drift'], [{'repository': 'outdated', 'callers': [
            {**callers['outdated'][0], 'files': ['.github/workflows/policy.yml']}]}])
        self.assertIn('report only', settings.pin_summary(report))

    def pin_report(self, master_tree, pinned_tree):
        target, pin = 'a' * 40, 'b' * 40
        prefix = 'repos/swift-library/.github'
        responses = {prefix + '/commits/master': {'sha': target},
                     prefix + '/git/trees/' + target + '?recursive=1': master_tree,
                     prefix + '/git/trees/' + pin + '?recursive=1': pinned_tree}

        def query(path):
            response = responses[path]
            if isinstance(response, Exception):
                raise response
            return response

        with patch.object(settings, 'gh', side_effect=query), \
                patch.object(settings, 'collection', return_value=[{'name': 'package', 'fork': False}]), \
                patch.object(settings, 'shared_callers', return_value=[
                    {'workflow': '.github/workflows/ci.yml', 'ref': pin}]):
            return settings.pin_drift(self.declared)

    def tree(self, **files):
        return {'truncated': False, 'tree': [
            {'path': path, 'mode': '100644', 'type': 'blob', 'sha': digest}
            for path, digest in files.items()]}

    def test_docs_and_settings_checker_changes_do_not_report_pin_drift(self):
        shared = {'.github/workflows/swift-package-ci.yml': '1' * 40,
                  'Scripts/api-evidence.py': '2' * 40}
        master = self.tree(**shared, **{'profile/README.md': '3' * 40,
                                       'Scripts/check-settings.py': '4' * 40})
        pinned = self.tree(**shared, **{'profile/README.md': '5' * 40,
                                       'Scripts/check-settings.py': '6' * 40})
        report = self.pin_report(master, pinned)
        self.assertEqual(report['drift'], [])
        self.assertEqual(report['errors'], [])
        self.assertIn('shared pin drift: none (1 repositories, 1 callers)', settings.pin_summary(report))

    def test_workflow_change_reports_the_shared_file(self):
        path = '.github/workflows/swift-package-ci.yml'
        report = self.pin_report(self.tree(**{path: '1' * 40}), self.tree(**{path: '2' * 40}))
        self.assertEqual(report['drift'][0]['callers'][0]['files'], [path])
        self.assertIn('shared files differ: ' + path, settings.pin_summary(report))
        self.assertEqual(report['errors'], [])

    def test_shared_script_changes_and_removal_report_the_files(self):
        master = self.tree(**{'Scripts/api-evidence.py': '1' * 40})
        pinned = self.tree(**{'Scripts/api-evidence.py': '2' * 40, 'Scripts/validate-version': '3' * 40})
        report = self.pin_report(master, pinned)
        self.assertEqual(report['drift'][0]['callers'][0]['files'],
                         ['Scripts/api-evidence.py', 'Scripts/validate-version'])

    def test_unknown_and_unreachable_pins_are_errors(self):
        for failure in [subprocess.CalledProcessError(1, ['gh'], output='{"status":"404"}'),
                        ConnectionError('unreachable')]:
            with self.subTest(failure=type(failure).__name__):
                report = self.pin_report(self.tree(), failure)
                self.assertEqual(report['drift'], [])
                self.assertEqual(report['errors'], [{'repository': 'package',
                    'workflow': '.github/workflows/ci.yml', 'ref': 'b' * 40,
                    'reason': type(failure).__name__}])
                self.assertIn('shared pin error: package:', settings.pin_summary(report))
                self.assertIn('shared pin drift: none observed', settings.pin_summary(report))

    def test_truncated_pin_tree_is_an_error(self):
        report = self.pin_report(self.tree(), {'truncated': True, 'tree': []})
        self.assertEqual(report['errors'][0]['reason'], 'ValueError')
        self.assertEqual(report['drift'], [])

    def test_shared_surface_covers_reusable_workflows_and_existing_sources(self):
        reusable = {path.relative_to(ROOT).as_posix() for path in (ROOT / '.github/workflows').iterdir()
                    if path.suffix in ('.yml', '.yaml')
                    and re.search(r'^  workflow_call:', path.read_text(), re.M)}
        self.assertEqual(reusable, {path for path in settings.SHARED_SURFACE
                                    if path.startswith('.github/workflows/')})
        self.assertTrue(all((ROOT / path).is_file() for path in settings.SHARED_SURFACE))

    def test_pin_report_reads_workflow_calls_including_quoted_refs(self):
        entries = [{'type': 'file', 'name': 'ci.yml', 'path': '.github/workflows/ci.yml', 'url': 'blob'},
                   {'type': 'file', 'name': 'notes.txt', 'path': '.github/workflows/notes.txt', 'url': 'ignored'}]
        source = '''jobs:
  validate:
    uses: swift-library/.github/.github/workflows/swift-package-ci.yml@old
  policy:
    uses: "swift-library/.github/.github/workflows/policy.yml@new"
  local:
    uses: ./.github/workflows/local.yml
'''
        responses = {'repos/swift-library/package/contents/.github/workflows?ref=master': entries,
                     'blob': {'content': base64.b64encode(source.encode()).decode()}}
        with patch.object(settings, 'gh', side_effect=lambda path: responses[path]):
            callers = settings.shared_callers('swift-library', {'name': 'package', 'default_branch': 'master'})
        self.assertEqual([caller['ref'] for caller in callers], ['old', 'new'])

    def test_pin_drift_and_unavailable_observations_do_not_change_settings_exit(self):
        for report in [{'target': 'a' * 40, 'repositories_with_callers': 1, 'caller_count': 1,
                        'drift': [{'repository': 'package', 'callers': [
                            {'workflow': 'ci.yml', 'ref': 'old', 'files': ['.github/workflows/policy.yml']}]}],
                        'errors': [],
                        'unavailable': []},
                       {'target': None, 'repositories_with_callers': 0, 'caller_count': 0,
                        'drift': [], 'errors': [],
                        'unavailable': [{'repository': 'swift-library', 'reason': 'CalledProcessError'}]},
                       {'target': 'a' * 40, 'repositories_with_callers': 1, 'caller_count': 1,
                        'drift': [], 'errors': [{'repository': 'package', 'workflow': 'ci.yml',
                                                'ref': 'unknown', 'reason': 'CalledProcessError'}],
                        'unavailable': []}]:
            with self.subTest(report=report), patch.object(settings.sys, 'argv', ['check-settings.py']), \
                    patch.object(settings, 'check', return_value=[]), \
                    patch.object(settings, 'pin_drift', return_value=report), redirect_stdout(io.StringIO()):
                self.assertEqual(settings.main(), 0)
            with patch.object(settings.sys, 'argv', ['check-settings.py']), \
                    patch.object(settings, 'check', return_value=['enforced mismatch']), \
                    patch.object(settings, 'pin_drift', return_value=report), redirect_stdout(io.StringIO()):
                self.assertEqual(settings.main(), 1)

    def test_unavailable_repository_observation_is_explicit(self):
        with patch.object(settings, 'gh', return_value={'sha': 'a' * 40}), \
                patch.object(settings, 'shared_surface', return_value={}), \
                patch.object(settings, 'collection', return_value=[{'name': 'private', 'fork': False}]), \
                patch.object(settings, 'shared_callers', side_effect=ValueError):
            report = settings.pin_drift(self.declared)
        self.assertEqual(report['unavailable'], [{'repository': 'private', 'reason': 'ValueError'}])
        self.assertIn('observation unavailable', settings.pin_summary(report))


if __name__ == "__main__":
    unittest.main()
