#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Embed the shared version validator in the package workflows."""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = '      # Begin generated version validator.\n'
END = '      # End generated version validator.\n'


def rendered(context):
    prefix = START + '      - name: Validate version and compiler declarations\n'
    if context == 'policy':
        prefix += "        if: hashFiles('.github/release.json') != ''\n"
    if context == 'ci':
        prefix += '        env:\n          CONFIGURATION: ${{ inputs.configuration }}\n'
    if context == 'release':
        prefix += '''        env:
          GH_TOKEN: ${{ github.token }}
          RELEASE_TAG: ${{ inputs.tag }}
          ACCEPTED_COMMIT: ${{ inputs.accepted_commit }}
'''
    prefix += '''        run: |
          set -euo pipefail
          mkdir -p .build/shared .build/release-validation
          cat > .build/shared/validate-version <<'PY'
'''
    script = (ROOT / 'Scripts/validate-version').read_text()
    body = ''.join(('          ' + line if line else '') + '\n' for line in script.splitlines())
    suffix = '          PY\n'
    command = 'python3 .build/shared/validate-version --require-clean --json'
    if context == 'ci':
        command += ' --configuration "$CONFIGURATION"'
    if context == 'release':
        suffix += '''          test "$(git rev-parse HEAD)" = "$ACCEPTED_COMMIT"
          gh api users/showxu/ssh_signing_keys --jq '.[] | "10173746+showxu@users.noreply.github.com " + .key' > .build/shared/allowed-signers
          git config gpg.ssh.allowedSignersFile .build/shared/allowed-signers
'''
        command += ' --tag "$RELEASE_TAG" --notes .build/release-validation/release-notes.md'
    suffix += '          ' + command + ' > .build/release-validation/version.json\n'
    return prefix + body + suffix + END


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for context, name in [('ci', 'swift-package-ci.yml'), ('release', 'swift-package-release.yml')]:
        target = ROOT / '.github/workflows' / name
        text = target.read_text()
        start, end = text.index(START), text.index(END) + len(END)
        expected = text[:start] + rendered(context) + text[end:]
        if args.check:
            if text != expected:
                raise SystemExit('Version workflow differs from its checker; run Scripts/sync-version-workflows.py')
        else:
            target.write_text(expected)
    if args.check:
        print('version workflows in sync')


if __name__ == '__main__':
    main()
