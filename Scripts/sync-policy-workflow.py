#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Embed the policy checker in its trusted reusable workflow; --check detects drift."""

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIX = """# Generated from Scripts/check-policy.py by Scripts/sync-policy-workflow.py.
name: Source policy

on:
  workflow_call:
    inputs:
      allow-terms:
        description: Newline-separated product names required by this repository
        type: string
        default: ''
      allow-bots:
        description: Newline-separated GitHub bot logins permitted for commit identities
        type: string
        default: ''

permissions:
  contents: read

jobs:
  policy:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          ref: ${{ github.event.pull_request.head.sha || github.sha }}
          fetch-depth: 0
          persist-credentials: false
      - name: Check source identity, content and version
        env:
          GH_TOKEN: ${{ github.token }}
          ALLOW_TERMS: ${{ inputs.allow-terms }}
          ALLOW_BOTS: ${{ inputs.allow-bots }}
        run: |
          python3 - <<'PY'
"""


def rendered():
    script = (ROOT / "Scripts/check-policy.py").read_text()
    return PREFIX + "".join(("          " + line if line else "") + "\n" for line in script.splitlines()) + "          PY\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = ROOT / ".github/workflows/policy.yml"
    expected = rendered()
    if args.check:
        if not target.is_file() or target.read_text() != expected:
            raise SystemExit("Policy workflow differs from its checker; run Scripts/sync-policy-workflow.py")
        print("policy workflow in sync")
    else:
        target.write_text(expected)


if __name__ == "__main__":
    main()
