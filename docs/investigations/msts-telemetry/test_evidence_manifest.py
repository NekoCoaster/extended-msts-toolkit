"""Offline failure-mode checks for the evidence handoff verifier."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from verify_evidence_manifest import verify


class EvidenceManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.file = self.root / 'sample.bin'
        self.file.write_bytes(b'abc')
        self.entry = dict(path='sample.bin', bytes=3,
                          sha256=hashlib.sha256(b'abc').hexdigest())

    def check(self, entries=None):
        return verify(self.root, {'files': entries if entries is not None else [self.entry]})

    def test_matching_and_extra_unlisted_file(self):
        (self.root / 'extra').write_bytes(b'not in manifest')
        self.assertTrue(self.check()['passed'])
        self.assertEqual(self.check()['verified'], 1)

    def test_same_size_corruption(self):
        self.file.write_bytes(b'abd')
        self.assertEqual(self.check()['failures'][0]['reason'], 'mismatch')

    def test_missing_is_unavailable(self):
        self.file.unlink()
        self.assertEqual(self.check()['failures'][0]['reason'], 'unavailable')

    def test_invalid_manifest_entries(self):
        cases = [[], [self.entry, self.entry],
                 [dict(self.entry, bytes=-1)], [dict(self.entry, sha256='x'*64)]]
        for path in ['../outside', '/absolute', 'C:/absolute', 'a\\b',
                     './sample.bin', 'a//b']:
            cases.append([dict(self.entry, path=path)])
        for entries in cases:
            with self.subTest(entries=entries):
                with self.assertRaises(ValueError):
                    self.check(entries)


if __name__ == '__main__':
    unittest.main()
