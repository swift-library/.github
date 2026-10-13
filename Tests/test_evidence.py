# SPDX-License-Identifier: Apache-2.0 WITH Swift-exception
"""Verify that publishable evidence retains facts without execution context."""

import importlib.util
import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('check_evidence', ROOT / 'Scripts/check-evidence.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        fixtures = ROOT / '.build/test-fixtures'
        fixtures.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=fixtures)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def test_logs_normalize_paths_but_retain_dependency_source_names(self):
        machine = '/' + 'Users' + '/runner/work/repo'
        (self.root / 'check.log').write_text(f'{machine}/.build\nCompiling Cursor.swift\n29 tests passed\n')
        self.assertEqual(evidence.check(self.root, [(machine, '<package>')]), [])
        self.assertEqual((self.root / 'check.log').read_text(), '<package>/.build\nCompiling Cursor.swift\n29 tests passed\n')

    def test_manifest_root_is_relative_but_other_values_remain_checked(self):
        path = self.root / 'package.json'
        path.write_text(json.dumps({'packageKind': {'root': [str(Path.cwd())]}, 'name': 'Example'}))
        self.assertEqual(evidence.check(self.root, []), [])
        self.assertEqual(json.loads(path.read_text()), {'packageKind': {'root': ['.']}, 'name': 'Example'})
        path.write_text(json.dumps({'dependencies': ['/' + 'home' + '/someone/private']}))
        self.assertEqual(len(evidence.check(self.root, [])), 1)

    def test_all_utf8_files_normalize_known_paths_longest_first(self):
        home = '/' + 'Users' + '/runner'
        checkout = home + '/work/package'
        temporary = checkout + '/.build/temporary'
        replacements = [(home, '<home>'), (checkout, '<package>'), (temporary, '<temporary>')]
        files = {
            'Package.swift': f'.package(path: "{checkout}")\n',
            'consumer.json': json.dumps({'home': home, 'temporary': temporary + '/consumer'}),
            'receipt': f'{checkout}/Sources/Example.swift\nRésumé: passed\n',
        }
        for name, content in files.items():
            (self.root / name).write_text(content)
        self.assertEqual(evidence.check(self.root, replacements), [])
        self.assertEqual((self.root / 'Package.swift').read_text(), '.package(path: "<package>")\n')
        self.assertEqual(json.loads((self.root / 'consumer.json').read_text()),
                         {'home': '<home>', 'temporary': '<temporary>/consumer'})
        self.assertEqual((self.root / 'receipt').read_text(), '<package>/Sources/Example.swift\nRésumé: passed\n')
        before = {path.name: path.read_bytes() for path in self.root.iterdir()}
        self.assertEqual(evidence.check(self.root, replacements), [])
        self.assertEqual({path.name: path.read_bytes() for path in self.root.iterdir()}, before)

    def test_unknown_paths_and_plans_fail_with_location(self):
        (self.root / 'metadata.json').write_text('{"path":"/' + 'home' + '/someone/private"}\n')
        (self.root / 'check.log').write_text('unrelated.' + 'plan.md\n')
        errors = evidence.check(self.root, [])
        self.assertEqual(len(errors), 2)
        self.assertTrue(any('metadata.json:1:' in error for error in errors))
        self.assertTrue(all('someone' not in error for error in errors))

    def bundle(self, name, data, kind=tarfile.REGTYPE, mode='w:gz'):
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode=mode) as archive:
            member = tarfile.TarInfo(name)
            member.type = kind
            member.mode = 0o640
            member.mtime = 42
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
        return output.getvalue()

    def test_docc_and_nested_archives_are_scanned_without_extraction(self):
        text = b'file:///' + b'Users' + b'/private/source.swift'
        nested = self.bundle('data/module.json', text)
        (self.root / 'validation.tar.gz').write_bytes(self.bundle('module.doccarchive.tar.gz', nested))
        errors = evidence.check(self.root, [])
        self.assertEqual(len(errors), 1)
        self.assertIn('validation.tar.gz!module.doccarchive.tar.gz!data/module.json:1:', errors[0])
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_nested_archive_text_is_normalized_and_metadata_retained(self):
        checkout = '/' + 'home' + '/runner/package'
        text = json.dumps({'source': checkout + '/Sources/Example.swift'}).encode()
        nested = self.bundle('data/module.json', text, mode='w')
        path = self.root / 'validation.tgz'
        path.write_bytes(self.bundle('module.doccarchive.tar', nested))
        self.assertEqual(evidence.check(self.root, [(checkout, '<package>')]), [])
        with tarfile.open(path) as outer:
            with tarfile.open(fileobj=io.BytesIO(outer.extractfile('module.doccarchive.tar').read())) as inner:
                member = inner.getmember('data/module.json')
                self.assertEqual((member.mode, member.mtime), (0o640, 42))
                self.assertEqual(json.load(inner.extractfile(member)),
                                 {'source': '<package>/Sources/Example.swift'})
        before = path.read_bytes()
        self.assertEqual(evidence.check(self.root, [(checkout, '<package>')]), [])
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(len(list(self.root.iterdir())), 1)

    def test_archive_binary_and_unchanged_archives_are_preserved(self):
        checkout = '/' + 'home' + '/runner/package'
        data = b'\xff' + checkout.encode()
        path = self.root / 'binary.tar.gz'
        archive = self.bundle('payload.bin', data)
        path.write_bytes(archive)
        self.assertEqual(evidence.check(self.root, [(checkout, '<package>')]), [])
        self.assertEqual(path.read_bytes(), archive)

    def test_unknown_archive_paths_still_fail_after_normalization(self):
        checkout = '/' + 'home' + '/runner/package'
        text = (checkout + '/Source.swift\n/' + 'home' + '/someone/private').encode()
        path = self.root / 'validation.tar.gz'
        archive = self.bundle('receipt.txt', text)
        path.write_bytes(archive)
        errors = evidence.check(self.root, [(checkout, '<package>')])
        self.assertEqual(len(errors), 1)
        self.assertIn('validation.tar.gz!receipt.txt:2:', errors[0])
        self.assertEqual(path.read_bytes(), archive)

    def test_symlinks_and_unsafe_archive_names_fail(self):
        (self.root / 'link.log').symlink_to(self.root / 'missing')
        (self.root / 'bad.tar.gz').write_bytes(self.bundle('../outside', b'content'))
        self.assertEqual(len(evidence.check(self.root, [])), 2)

    def test_binary_artifacts_are_preserved(self):
        path = self.root / 'icon.png'
        data = b'\x89PNG\r\n\x1a\n\xff'
        path.write_bytes(data)
        self.assertEqual(evidence.check(self.root, []), [])
        self.assertEqual(path.read_bytes(), data)

    def test_non_utf8_logs_are_rejected(self):
        path = self.root / 'check.log'
        path.write_bytes(b'\xff')
        self.assertEqual(evidence.check(self.root, []), ['check.log: log is not UTF-8'])


if __name__ == '__main__':
    unittest.main()
