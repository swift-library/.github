# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Protect title-only policy runs and the required validation contexts."""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / '.github/workflows'


class CallerTests(unittest.TestCase):
    def test_validation_events_do_not_include_title_edits(self):
        workflow = (WORKFLOWS / 'ci.yml').read_text()
        events = re.search(r'types: \[([^\]]+)\]', workflow)[1]
        self.assertEqual({event.strip() for event in events.split(',')},
                         {'opened', 'synchronize', 'reopened'})
        self.assertNotIn('  policy:', workflow)
        self.assertIn('  result:', workflow)
        self.assertNotIn('  schedule:', workflow)
        self.assertIn('uses: ./.github/workflows/icon-audit.yml', workflow)

    def test_weekly_icon_audit_runs_the_same_check_as_required_validation(self):
        workflow = (WORKFLOWS / 'icon-audit.yml').read_text()
        self.assertIn('  schedule:', workflow)
        self.assertIn('  workflow_call:', workflow)
        self.assertIn('Scripts/check-icons.py --generator', workflow)

    def test_policy_has_its_own_caller_and_preserves_the_context(self):
        workflow = (WORKFLOWS / 'source-policy.yml').read_text()
        events = re.search(r'types: \[([^\]]+)\]', workflow)[1]
        self.assertEqual({event.strip() for event in events.split(',')},
                         {'opened', 'synchronize', 'reopened', 'edited'})
        self.assertIn('branches: [master]', workflow)
        self.assertIn('  policy:\n    uses: ./.github/workflows/policy.yml', workflow)
        self.assertNotIn('  result:', workflow)
        self.assertNotIn('  icons:', workflow)

    def test_callers_cancel_only_their_own_superseded_runs(self):
        for name in ('ci.yml', 'source-policy.yml'):
            with self.subTest(workflow=name):
                workflow = (WORKFLOWS / name).read_text()
                self.assertIn('group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}', workflow)
                self.assertIn('cancel-in-progress: true', workflow)

    def test_reusable_workflows_do_not_cancel_release_validation_or_publication(self):
        for name in ('swift-package-ci.yml', 'policy.yml'):
            with self.subTest(workflow=name):
                self.assertNotIn('concurrency:', (WORKFLOWS / name).read_text())
        publication = (WORKFLOWS / 'swift-package-release.yml').read_text()
        self.assertIn('cancel-in-progress: false', publication)
        self.assertNotIn('cancel-in-progress: true', publication)


if __name__ == '__main__':
    unittest.main()
