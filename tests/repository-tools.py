"""Portable tests for inventory, preparation and non-destructive ZIP packaging."""
from __future__ import annotations

import hashlib
import io
import tarfile
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import source_checksums as checksums
import package as packager
import tcc_source


class RepoToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'repo'
        self.root.mkdir()
        self.write('README.md', '# Test\n[Guide](docs/guide.md)\n')
        self.write('LICENSE', 'Test license\n')
        self.write('THIRD-PARTY.md', '# Notices\n')
        self.write('VERSION', '1.1.0\n')
        self.write('docs/guide.md', '[Home](../README.md)\n')
        self.write('runtime/DINPUT.dll', b'test runtime')
        self.write('runtime/integrity.json', json.dumps({'DINPUT.dll': checksums.digest_bytes(b'test runtime')}))
        self.write('tools/tcc/tcc.exe', b'compiler fixture, never executed')
        self.write('src/nemt.c', '/* source fixture */\n')
        self.write('build/NEMT.exe', b'MZ test frontend, never executed')
        self.write('build/NEMT.exe.manifest', '<assembly/>')
        self.write('build/test.exe', b'not shipped')
        self.write('.github/workflows/verify.yml', 'name: fixture\n')
        self.write('AGENTS.md', '# Contributor notes\n')
        self.refresh()

    def write(self, name, data):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data.encode('utf-8') if isinstance(data, str) else data)
        return p

    def refresh(self):
        (self.root / checksums.MANIFEST).write_bytes(checksums.render(checksums.current(self.root)))

    def snapshot(self):
        return {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def package(self, name='NEMT.zip'):
        path = self.base / name
        packager.package(self.root, self.root / 'build/NEMT.exe', path)
        return path

    def test_clean_inventory(self):
        self.assertGreater(checksums.check(self.root), 0)

    def test_generated_files_excluded_but_compiler_retained(self):
        data = checksums.current(self.root)
        self.assertIn('tools/tcc/tcc.exe', data)
        self.assertNotIn('build/NEMT.exe', data)
        self.write('NEMT.exe.manifest', '<old generated sidecar/>')
        self.assertNotIn('NEMT.exe.manifest', checksums.current(self.root))
        self.write('src/NEMT.exe.manifest', '<source sidecar/>')
        self.assertIn('src/NEMT.exe.manifest', checksums.current(self.root))

    def test_new_source_is_detected(self):
        self.write('src/new.c', 'new')
        with self.assertRaisesRegex(ValueError, 'Unlisted source'):
            checksums.check(self.root)

    def test_deleted_source_is_detected(self):
        (self.root / 'src/nemt.c').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing source'):
            checksums.check(self.root)

    def test_modified_source_is_detected(self):
        self.write('src/nemt.c', 'changed')
        with self.assertRaisesRegex(ValueError, 'Changed source'):
            checksums.check(self.root)

    def test_parse_rejects_unsafe_or_duplicate_paths(self):
        value = '0' * 64
        for name in ['../secret', '/absolute', 'C:/secret', 'a\\b', 'a//b']:
            with self.subTest(name=name), self.assertRaises(ValueError):
                checksums.parse(f'{value}  {name}\n'.encode())
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            checksums.parse(f'{value}  a\n{value}  a\n'.encode())

    def test_hashes_preserve_raw_crlf_bytes(self):
        p = self.write('test.bat', b'@echo off\r\n')
        self.assertEqual(checksums.digest(p), hashlib.sha256(b'@echo off\r\n').hexdigest())

    def test_package_leaves_entire_tree_unchanged(self):
        before = self.snapshot()
        self.package()
        self.assertEqual(before, self.snapshot())

    def test_package_is_deterministic(self):
        one, two = self.package('one.zip'), self.package('two.zip')
        self.assertEqual(one.read_bytes(), two.read_bytes())

    def test_release_excludes_development_files(self):
        with zipfile.ZipFile(self.package()) as archive:
            names = archive.namelist()
            for prefix in ['NEMT/tools/', 'NEMT/build/', 'NEMT/src/', 'NEMT/.github/']:
                self.assertFalse(any(n.startswith(prefix) for n in names))
            self.assertNotIn('NEMT/AGENTS.md', names)
            self.assertIn('NEMT/NEMT.exe.manifest', names)

    def test_release_checksums_cover_exact_payload(self):
        with zipfile.ZipFile(self.package()) as archive:
            entries = checksums.parse(archive.read('NEMT/SHA256SUMS.txt'))
            self.assertEqual(set(entries), {n.removeprefix('NEMT/') for n in archive.namelist()} - {'SHA256SUMS.txt'})
            for name, value in entries.items():
                self.assertEqual(value, checksums.digest_bytes(archive.read('NEMT/' + name)))

    def test_missing_sidecar_fails(self):
        (self.root / 'build/NEMT.exe.manifest').unlink()
        with self.assertRaisesRegex(ValueError, 'manifest'):
            self.package()

    def test_missing_frontend_fails(self):
        (self.root / 'build/NEMT.exe').unlink()
        with self.assertRaisesRegex(ValueError, 'frontend'):
            self.package()

    def test_integrity_failure_preserves_existing_output(self):
        self.write('runtime/DINPUT.dll', 'changed runtime')
        self.refresh()
        out = self.base / 'NEMT.zip'
        out.write_bytes(b'previous valid release')
        with self.assertRaisesRegex(ValueError, 'integrity'):
            self.package()
        self.assertEqual(out.read_bytes(), b'previous valid release')

    def test_stale_manifest_is_not_silently_rewritten(self):
        self.write('README.md', 'new docs')
        before = (self.root / 'SHA256SUMS.txt').read_bytes()
        with self.assertRaises(ValueError):
            self.package()
        self.assertEqual(before, (self.root / 'SHA256SUMS.txt').read_bytes())

    def test_broken_source_link_fails(self):
        self.write('docs/guide.md', '[Missing](missing.md)')
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'Broken relative'):
            self.package()

    def test_source_only_link_fails_in_release(self):
        self.write('docs/guide.md', '[Compiler](../tools/tcc/tcc.exe)')
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'Broken relative'):
            self.package()

    def test_external_anchors_and_encoded_spaces(self):
        self.write('docs/a b.md', '# Fine')
        self.write('docs/guide.md', '[Page](a%20b.md#section) [Web](https://example.org/x) [Here](#local)')
        self.refresh()
        self.package()

    def test_output_cannot_pollute_source_inventory(self):
        with self.assertRaisesRegex(ValueError, 'outside the source tree'):
            packager.package(self.root, self.root / 'build/NEMT.exe', self.root / 'NEMT.zip')

    def test_output_may_be_under_build(self):
        packager.package(self.root, self.root / 'build/NEMT.exe', self.root / 'build/NEMT.zip')
        checksums.check(self.root)

    def test_private_key_marker_is_rejected(self):
        self.write('docs/secret.txt', '-----BEGIN RSA PRIVATE KEY-----')
        self.refresh()
        with self.assertRaisesRegex(ValueError, 'Private key'):
            self.package()

    def test_missing_source_check_never_downloads(self):
        with patch.object(tcc_source, 'urlopen') as request:
            with self.assertRaisesRegex(ValueError, 'source is missing'):
                tcc_source.ensure_source(self.root, check_only=True)
            request.assert_not_called()

    def test_bad_source_download_does_not_write_archive(self):
        path = self.base / 'not-source.tar.bz2'
        path.write_bytes(b'not the compiler source')
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            tcc_source.ensure_source(self.root, supplied_archive=path)
        self.assertFalse((self.root / tcc_source.SOURCE_PATH).exists())


    def source_fixture(self, *, omit=None):
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode='w:bz2') as archive:
            for name in sorted(tcc_source.REQUIRED_MEMBERS - {omit}):
                data = b'unit-test fixture, not actual compiler source'
                info = tarfile.TarInfo('tcc-0.9.27/' + name)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
        return output.getvalue()

    def test_valid_source_storage_and_offline_reuse(self):
        data = self.source_fixture()
        path = self.base / 'fixture.tar.bz2'
        path.write_bytes(data)
        with patch.object(tcc_source, 'SOURCE_SHA256', checksums.digest_bytes(data)):
            target = tcc_source.ensure_source(self.root, supplied_archive=path)
            self.assertEqual(target.read_bytes(), data)
            with patch.object(tcc_source, 'urlopen') as request:
                self.assertEqual(tcc_source.ensure_source(self.root, check_only=True), target)
                request.assert_not_called()

    def test_incomplete_source_rejected_even_with_expected_fixture_hash(self):
        data = self.source_fixture(omit='COPYING')
        with patch.object(tcc_source, 'SOURCE_SHA256', checksums.digest_bytes(data)):
            with self.assertRaisesRegex(ValueError, 'missing required'):
                tcc_source.validate_source(data)

    def test_corrupt_existing_source_is_not_overwritten(self):
        target = self.write(str(tcc_source.SOURCE_PATH), b'corrupt existing file')
        with patch.object(tcc_source, 'urlopen') as request:
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
                tcc_source.ensure_source(self.root)
            request.assert_not_called()
        self.assertEqual(target.read_bytes(), b'corrupt existing file')

    def toolchain_fixture(self):
        spec = importlib.util.spec_from_file_location('verify_toolchain', ROOT / 'tools/verify-toolchain.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.write('tools/tcc/README.txt', 'local documentation')
        value = checksums.digest(self.root / 'tools/tcc/tcc.exe')
        self.write('third-party/tinycc/FILES.sha256', checksums.render({'tcc.exe': value}))
        return module

    def test_toolchain_inventory_and_hash(self):
        module = self.toolchain_fixture()
        self.assertEqual(module.verify(self.root), 2)
        self.write('tools/tcc/tcc.exe', 'changed')
        with self.assertRaisesRegex(ValueError, 'file changed'):
            module.verify(self.root)

    def test_toolchain_unexpected_files_rejected(self):
        module = self.toolchain_fixture()
        self.write('tools/tcc/unused.h', 'unneeded')
        with self.assertRaisesRegex(ValueError, 'inventory mismatch'):
            module.verify(self.root)

    def test_toolchain_missing_files_rejected(self):
        module = self.toolchain_fixture()
        (self.root / 'tools/tcc/tcc.exe').unlink()
        with self.assertRaisesRegex(ValueError, 'inventory mismatch'):
            module.verify(self.root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
