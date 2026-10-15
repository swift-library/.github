# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
from copy import deepcopy
import base64
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
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

    def test_pin_report_lists_only_outdated_callers_and_excludes_forks(self):
        target = 'a' * 40
        repositories = [{'name': name, 'fork': fork, 'default_branch': 'master'}
                        for name, fork in [('current', False), ('outdated', False), ('fork', True), ('local', False)]]
        callers = {'current': [{'workflow': '.github/workflows/ci.yml', 'ref': target}],
                   'outdated': [{'workflow': '.github/workflows/ci.yml', 'ref': 'b' * 40},
                                {'workflow': '.github/workflows/source-policy.yml', 'ref': target}],
                   'local': []}
        with patch.object(settings, 'gh', return_value={'sha': target}), \
                patch.object(settings, 'collection', return_value=repositories), \
                patch.object(settings, 'shared_callers', side_effect=lambda org, repository: callers[repository['name']]):
            report = settings.pin_drift(self.declared)
        self.assertEqual(report['target'], target)
        self.assertEqual(report['repositories_with_callers'], 2)
        self.assertEqual(report['caller_count'], 3)
        self.assertEqual(report['drift'], [{'repository': 'outdated', 'callers': callers['outdated'][:1]}])
        self.assertIn('report only', settings.pin_summary(report))

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
                        'drift': [{'repository': 'package', 'callers': [{'workflow': 'ci.yml', 'ref': 'old'}]}],
                        'unavailable': []},
                       {'target': None, 'repositories_with_callers': 0, 'caller_count': 0,
                        'drift': [], 'unavailable': [{'repository': 'swift-library', 'reason': 'CalledProcessError'}]}]:
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
                patch.object(settings, 'collection', return_value=[{'name': 'private', 'fork': False}]), \
                patch.object(settings, 'shared_callers', side_effect=ValueError):
            report = settings.pin_drift(self.declared)
        self.assertEqual(report['unavailable'], [{'repository': 'private', 'reason': 'ValueError'}])
        self.assertIn('observation unavailable', settings.pin_summary(report))


if __name__ == "__main__":
    unittest.main()
