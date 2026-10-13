#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Embed the shared API evidence collector and report-only job."""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
START = '  # Begin generated API job.\n'
END = '  # End generated API job.\n'
RELEASE_START = '      # Begin generated API publication.\n'
RELEASE_END = '      # End generated API publication.\n'


def embedded(mode):
    source = (ROOT / 'Scripts/api-evidence.py').read_text()
    return ("          mkdir -p .build/shared\n          cat > .build/shared/api-evidence.py <<'PY'\n"
            + ''.join(('          ' + line if line else '') + '\n' for line in source.splitlines())
            + '          PY\n          python3 .build/shared/api-evidence.py ' + mode + '\n')


def job():
    gate = (ROOT / 'Scripts/check-evidence.py').read_text()
    return START + '''  api:
    needs: configure
    runs-on: macos-26
    timeout-minutes: 90
    continue-on-error: true
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          ref: ${{ needs.configure.outputs.commit }}
          fetch-depth: 0
          persist-credentials: false
      - uses: maxim-lobanov/setup-xcode@ed7a3b1fda3918c0306d1b724322adc0b8cc0a90 # v1
        with:
          xcode-version: '26.6'
      - name: Collect and compare public interfaces
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
''' + embedded('collect') + '''      - name: Check API evidence paths
        id: api_evidence
        if: always()
        env:
          EVIDENCE_DIRECTORY: .build/api-evidence
        run: |
          python3 - <<'PY'
''' + ''.join(('          ' + line if line else '') + '\n' for line in gate.splitlines()) + '''          PY
      - name: Preserve API report
        if: always() && steps.api_evidence.outcome == 'success'
        uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
        with:
          name: api-evidence-${{ needs.configure.outputs.commit }}
          path: .build/api-evidence/
          if-no-files-found: error
          retention-days: 30
''' + END


def publication():
    return RELEASE_START + '''      - name: Prepare release API evidence
        env:
          ACCEPTED_COMMIT: ${{ inputs.accepted_commit }}
        run: |
''' + embedded('prepare-release') + RELEASE_END


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for name, start, end, rendered in [
        ('swift-package-ci.yml', START, END, job()),
        ('swift-package-release.yml', RELEASE_START, RELEASE_END, publication()),
    ]:
        target = ROOT / '.github/workflows' / name
        text = target.read_text()
        expected = text[:text.index(start)] + rendered + text[text.index(end) + len(end):]
        if args.check:
            if text != expected:
                raise SystemExit('API workflow differs from its source; run Scripts/sync-api-workflows.py')
        else:
            target.write_text(expected)
    if args.check:
        print('API workflows in sync')


if __name__ == '__main__':
    main()
