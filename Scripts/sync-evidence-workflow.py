#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Derive the trusted upload gate from its testable source checker."""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = '      # Begin generated evidence gate.\n'
END = '      # End generated evidence gate.\n'


def rendered():
    script = (ROOT / 'Scripts/check-evidence.py').read_text()
    return (START + '''      - name: Check validation evidence
        id: evidence
        if: always()
        run: |
          python3 - <<'PY'
''' + ''.join(('          ' + line if line else '') + '\n' for line in script.splitlines()) + '          PY\n' + END)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    target = ROOT / '.github/workflows/swift-package-ci.yml'
    text = target.read_text()
    start, end = text.index(START), text.index(END) + len(END)
    expected = text[:start] + rendered() + text[end:]
    if args.check:
        if text != expected:
            raise SystemExit('Evidence workflow differs from its checker; run Scripts/sync-evidence-workflow.py')
        print('evidence workflow in sync')
    else:
        target.write_text(expected)


if __name__ == '__main__':
    main()
