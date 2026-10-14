#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Collect release-bound interface evidence and report observations without gating."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

TOOL = {
    'repository': 'swift-library/swift-interface-distiller',
    'version': '0.1.2',
    'commit': '983b7af4052edd018c7d5becd5c91276a24c4fb3',
    'archive_sha256': '1284fe74c84644525840e01e39d068c04a1e3e28275c6304cf84ae92fd3644fc',
}
ASSET = 'api-evidence.json'
LIMIT = 256 * 1024 * 1024


class Unavailable(Exception):
    """An observation could not be made; this never means compatibility."""


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n')
    temporary.replace(path)


def read_url(url, token=None):
    headers = {'Accept': 'application/vnd.github+json' if token else 'application/octet-stream'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    with urlopen(Request(url, headers=headers), timeout=60) as response:
        content = response.read(LIMIT + 1)
    if len(content) > LIMIT:
        raise Unavailable('Download exceeds the evidence size limit')
    return content


class GitHub:
    def __init__(self, repository):
        self.repository = repository

    def get(self, suffix):
        return json.loads(read_url('https://api.github.com/repos/' + self.repository + suffix,
                                  os.environ.get('GH_TOKEN')))

    def latest(self):
        try:
            return self.get('/releases/latest')
        except HTTPError as error:
            if error.code == 404:
                return None
            raise

    def commit(self, tag):
        return self.get('/commits/' + quote(tag, safe=''))['sha']

    def asset(self, asset):
        expected = 'https://github.com/' + self.repository + '/releases/download/'
        url = asset['browser_download_url']
        if not url.startswith(expected):
            raise Unavailable('Release asset has an unexpected download origin')
        content = read_url(url)
        if asset.get('digest') != 'sha256:' + hashlib.sha256(content).hexdigest():
            raise Unavailable('Release asset digest could not be verified')
        return json.loads(content)


def envelope(repository, commit, status='failed', reason='Collection did not finish', evidence=None):
    return {'schema_version': 1, 'repository': repository, 'commit': commit,
            'collector': TOOL, 'status': status, 'reason': reason, 'evidence': evidence}


def validate(value, repository, commit):
    if value.get('schema_version') != 1:
        raise Unavailable('Unsupported API evidence envelope schema')
    if value.get('repository') != repository or value.get('commit') != commit:
        raise Unavailable('API evidence does not match its repository and tag commit')
    if value.get('status') not in ('complete', 'incomplete', 'failed'):
        raise Unavailable('Unknown API collection status')
    if value['status'] == 'complete':
        snapshot = value.get('evidence')
        if not isinstance(snapshot, dict) or not snapshot.get('configurations'):
            raise Unavailable('Complete API evidence has no configurations')
    return value


def baseline(api):
    release = api.latest()
    if release is None:
        return None, {'status': 'missing', 'reason': 'No published stable release'}
    identity = {'tag': release['tag_name'], 'release_id': release['id']}
    if release.get('draft') or release.get('prerelease'):
        raise Unavailable('Latest baseline must be a published stable release')
    assets = [asset for asset in release['assets'] if asset['name'] == ASSET]
    if not assets:
        return None, {**identity, 'status': 'missing', 'reason': 'Latest release has no API evidence asset'}
    if len(assets) != 1:
        raise Unavailable('Latest release must have exactly one API evidence asset')
    commit = api.commit(release['tag_name'])
    value = validate(api.asset(assets[0]), api.repository, commit)
    return value, {**identity, 'commit': commit, 'asset_id': assets[0]['id'],
                   'status': value['status'], 'source': 'release-asset', 'collector': value.get('collector')}


def run(arguments, root, log, timeout=3600, allowed=(0,)):
    environment = {key: value for key, value in os.environ.items()
                   if key not in ('GH_TOKEN', 'GITHUB_TOKEN')}
    with log.open('ab') as output:
        result = subprocess.run([str(argument) for argument in arguments], cwd=root,
                                env=environment, stdout=output, stderr=subprocess.STDOUT,
                                timeout=timeout, check=False)
    if result.returncode not in allowed:
        raise Unavailable(f'Compiler or collector command exited {result.returncode}; see collection log')
    return result.returncode


def tool(root, scratch, log):
    archive = scratch / 'collector.tar.gz'
    archive.write_bytes(read_url('https://github.com/' + TOOL['repository']
                                + '/archive/refs/tags/v' + TOOL['version'] + '.tar.gz'))
    if hashlib.sha256(archive.read_bytes()).hexdigest() != TOOL['archive_sha256']:
        raise Unavailable('Collector source archive does not match its reviewed pin')
    source = scratch / 'collector'
    if source.exists():
        shutil.rmtree(source)
    source.mkdir()
    with tarfile.open(archive) as contents:
        members = contents.getmembers()
        prefix = members[0].name.split('/')[0] + '/'
        for member in members:
            relative = member.name.removeprefix(prefix)
            if member.name == prefix.rstrip('/'):
                continue
            if (not member.name.startswith(prefix) or Path(relative).is_absolute()
                    or '..' in Path(relative).parts or not (member.isdir() or member.isfile())):
                raise Unavailable('Collector archive contains an unsafe member')
            destination = source / relative
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
            else:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(contents.extractfile(member).read())
    run(['swift', 'build', '--build-system', 'native', '-c', 'release', '--product', 'interface-distiller'],
        source, log, timeout=1200)
    return source / '.build/release/interface-distiller'


def collect(executable, root, scratch, output, repository, commit):
    snapshot = scratch / 'snapshot.json'
    snapshot.unlink(missing_ok=True)
    log = output / 'collection.log'
    run([executable, 'collect', 'package', root, '--output', snapshot,
         '--report', scratch / 'run.json', '--timeout', '3600'], root, log)
    evidence = json.loads(snapshot.read_text())
    status = run([executable, 'baseline', 'write', snapshot, scratch / 'validated.json'],
                 root, log, allowed=(0, 4))
    return envelope(repository, commit, 'complete' if status == 0 else 'incomplete',
                    'Collected library-product public/open interfaces' if status == 0
                    else 'Collection has gaps that prevent baseline acceptance', evidence)


def collector_matches(value):
    if value.get('collector') != TOOL:
        return False
    snapshot = value.get('evidence')
    return snapshot is None or all(
        configuration.get('configuration', {}).get('extractorVersion') == TOOL['version']
        for configuration in snapshot.get('configurations', [])
    )


def recollect(prior, identity, executable, root, scratch, output):
    """Rebuild only the verified release commit, before executing candidate sources."""
    if prior is None or collector_matches(prior):
        return prior, identity
    source = scratch / 'baseline-source'
    if source.exists():
        shutil.rmtree(source)
    log = output / 'collection.log'
    run(['git', 'clone', '--no-checkout', '--filter=blob:none',
         'https://github.com/' + prior['repository'] + '.git', source], root, log, timeout=300)
    run(['git', 'checkout', '--detach', identity['commit']], source, log, timeout=300)
    baseline_scratch = scratch / 'baseline-collection'
    baseline_scratch.mkdir(parents=True, exist_ok=True)
    value = collect(executable, source, baseline_scratch, output, prior['repository'], identity['commit'])
    if not collector_matches(value):
        raise Unavailable('Recollected baseline does not match the pinned collector')
    return value, {**identity, 'source': 'recollected-release-tag', 'collector': TOOL,
                   'attached_collector': prior.get('collector'), 'status': value['status']}


def compare(candidate, prior, identity, executable, root, scratch, log):
    report = {'schema_version': 1, 'mode': 'report-only', 'repository': candidate['repository'],
              'commit': candidate['commit'], 'baseline': identity, 'collection': candidate['status']}
    if candidate['status'] != 'complete':
        return {**report, 'status': 'unavailable', 'reason': candidate['reason']}
    if prior is None or prior['status'] != 'complete':
        return {**report, 'status': 'unavailable', 'reason': 'No complete release baseline'}
    if not collector_matches(candidate) or not collector_matches(prior):
        return {**report, 'status': 'unavailable', 'reason': 'Collector versions differ; a release baseline must be recollected'}
    old, new = scratch / 'baseline.json', scratch / 'candidate.json'
    write(old, prior['evidence'])
    write(new, candidate['evidence'])
    difference = scratch / 'difference.json'
    run([executable, 'compare', old, new, '--output', difference], root, log, allowed=(0, 1))
    value = json.loads(difference.read_text())
    scope_changed = any(change['category'] == 'provenance' and change['path'] == '/scope'
                        for change in value['changes'])
    incompatible = bool(value['incomparableConfigurations']) or scope_changed
    categories = {category: sum(change['category'] == category for change in value['changes'])
                  for category in ('interface', 'documentation', 'availability', 'provenance')}
    changed = bool(value['added'] or value['removed'] or value['changes'])
    return {**report, 'status': 'incomparable' if incompatible else 'changed' if changed else 'equal',
            'counts': {'added': len(value['added']), 'removed': len(value['removed']), **categories},
            'difference': value}


def summary(report):
    lines = ['## Public interface evidence', '', '**Report only; no version or compatibility decision.**', '',
             '- Collection: ' + report.get('collection', 'failed'), '- Comparison: ' + report['status']]
    identity = report.get('baseline', {})
    if identity.get('source') == 'recollected-release-tag':
        lines += ['- Baseline: recollected from ' + identity['tag'] + ' (' + identity['commit']
                  + ') with collector ' + identity['collector']['version']]
    if identity.get('reason'):
        lines += ['- Baseline: ' + identity['reason']]
    if report.get('counts'):
        lines += ['- ' + key + ': ' + str(count) for key, count in report['counts'].items()]
    lines += ['', 'See api-evidence.json and api-report.json for source identity, scope, gaps and field-level changes.', '']
    return '\n'.join(lines)


def report(root, repository, commit, executable=None):
    output, scratch = root / '.build/api-evidence', root / '.build/shared-api'
    output.mkdir(parents=True, exist_ok=True)
    scratch.mkdir(parents=True, exist_ok=True)
    (output / 'collection.log').write_bytes(b'')
    candidate = envelope(repository, commit)
    result = {'schema_version': 1, 'mode': 'report-only', 'repository': repository,
              'commit': commit, 'collection': 'failed', 'status': 'unavailable'}
    # Capture the remote baseline before executing the caller's package manifest.
    try:
        prior, identity = baseline(GitHub(repository))
    except Exception as error:
        prior, identity = None, {'status': 'unavailable', 'reason': type(error).__name__}
    try:
        executable = executable or tool(root, scratch, output / 'collection.log')
        try:
            prior, identity = recollect(prior, identity, executable, root, scratch, output)
        except Exception as error:
            prior, identity = None, {**identity, 'status': 'unavailable',
                                    'reason': str(error) if isinstance(error, Unavailable) else type(error).__name__}
        candidate = collect(executable, root, scratch, output, repository, commit)
        result = compare(candidate, prior, identity, executable, root, scratch, output / 'collection.log')
    except Exception as error:
        result.update(collection=candidate['status'], baseline=identity,
                      reason=str(error) if isinstance(error, Unavailable) else type(error).__name__)
        if candidate['status'] == 'failed':
            candidate['reason'] = result['reason']
    write(output / ASSET, candidate)
    write(output / 'api-report.json', result)
    markdown = summary(result)
    (output / 'api-report.md').write_text(markdown)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as stream:
            stream.write(markdown)
    print(markdown)


def prepare(root, repository, commit):
    source = root / '.build/ci-evidence' / ('api-evidence-' + commit) / ASSET
    if source.is_file():
        candidate = validate(json.loads(source.read_text()), repository, commit)
    else:
        candidate = envelope(repository, commit, reason='API job did not upload evidence; inspect the workflow run')
    write(root / '.build/release-validation' / ASSET, candidate)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('collect', 'prepare-release'))
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--executable', type=Path, help='Use an already built collector for local validation')
    args = parser.parse_args()
    root = args.root.resolve()
    repository = os.environ['GITHUB_REPOSITORY']
    commit = os.environ.get('ACCEPTED_COMMIT') or subprocess.check_output(
        ['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository) or not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise SystemExit('Expected a repository identity and a full source commit')
    if args.mode == 'collect':
        report(root, repository, commit, args.executable.resolve() if args.executable else None)
    else:
        prepare(root, repository, commit)


if __name__ == '__main__':
    main()
