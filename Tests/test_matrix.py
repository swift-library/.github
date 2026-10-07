# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Exercise the reusable workflow's package-owned execution budgets."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest

ROOT = Path(__file__).resolve().parent.parent


class MatrixTests(unittest.TestCase):
    def setUp(self):
        fixtures = ROOT / '.build/test-fixtures'
        fixtures.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(dir=fixtures)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        workflow = (ROOT / '.github/workflows/swift-package-ci.yml').read_text()
        configure = workflow.split('- id: configuration', 1)[1]
        self.program = textwrap.dedent(configure.split("python3 - <<'PY'\n", 1)[1].split('          PY\n', 1)[0])

    def configure(self, entries):
        configuration = self.root / 'release.json'
        output = self.root / 'output'
        output.write_text('')
        configuration.write_text(json.dumps({'check_command': 'Scripts/check', 'ci': {'include': entries}}))
        result = subprocess.run(
            [sys.executable, '-c', self.program], cwd=ROOT, text=True,
            capture_output=True,
            env={**os.environ, 'CONFIGURATION': str(configuration), 'GITHUB_OUTPUT': str(output)},
        )
        values = dict(line.split('=', 1) for line in output.read_text().splitlines())
        return result, values

    def test_omitted_budget_and_per_entry_overrides(self):
        entries = [
            {'name': 'default', 'runner': 'ubuntu-24.04'},
            {'name': 'long', 'runner': 'macos-26', 'timeout_minutes': 180},
            {'name': 'short', 'runner': 'ubuntu-24.04', 'timeout_minutes': 1},
            {'name': 'maximum', 'runner': 'ubuntu-24.04', 'timeout_minutes': 360},
        ]
        result, values = self.configure(entries)
        self.assertEqual(result.returncode, 0, result.stderr)
        matrix = json.loads(values['matrix'])['include']
        self.assertEqual([entry['timeout_minutes'] for entry in matrix], [45, 180, 1, 360])
        self.assertEqual([entry['name'] for entry in matrix], [entry['name'] for entry in entries])
        self.assertEqual(values['command'], 'Scripts/check')

    def test_invalid_budget_fails_before_emitting_runnable_matrix(self):
        for timeout in (0, -1, 361, 1.5, '180', True, None):
            with self.subTest(timeout=timeout):
                result, values = self.configure([{'name': 'invalid', 'timeout_minutes': timeout}])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('timeout_minutes must be an integer from 1 to 360', result.stderr)
                self.assertNotIn('matrix', values)


if __name__ == '__main__':
    unittest.main()
