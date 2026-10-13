#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Compare published repository logos with the shared design and pinned generator."""

import argparse
import base64
import json
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generator', type=Path, required=True)
    parser.add_argument('--design', type=Path, default=Path('DESIGN.md'))
    parser.add_argument('--sources', type=Path, default=Path('.github/icon-sources.json'))
    parser.add_argument('--output', type=Path, default=Path('.build/published-icons'))
    args = parser.parse_args()
    command = [sys.executable, '-B', str(args.generator), str(args.design)]
    subprocess.run([*command, '--lint'], check=True)
    names = set(subprocess.check_output([*command, '--list'], text=True).splitlines())
    sources = json.loads(args.sources.read_text())
    if {source['icon'] for source in sources} != names:
        raise ValueError('Published icon sources must cover the complete design family')
    args.output.mkdir(parents=True, exist_ok=True)
    failed = False
    for index, source in enumerate(sources):
        repository, path = source['repository'], source['path']
        result = subprocess.run(['gh', 'api', f'repos/{repository}/contents/{path}?ref=master'],
                                capture_output=True, text=True)
        if result.returncode:
            print(f'missing or unreadable\t{repository}/{path}', flush=True)
            print(result.stderr.strip(), file=sys.stderr)
            failed = True
            continue
        response = json.loads(result.stdout)
        if response.get('encoding') != 'base64':
            raise ValueError(f'Expected a file response for {repository}/{path}')
        target = args.output / f'{index}.svg'
        target.write_bytes(base64.b64decode(response['content']))
        print(f'published\t{repository}/{path}\t{response["sha"]}', flush=True)
        check = subprocess.run([*command, '--check', f'{source["icon"]}={target}'])
        failed = failed or check.returncode != 0
    return 1 if failed else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f'icon check: {error}', file=sys.stderr)
        sys.exit(1)
