"""Verify retained evidence against a published manifest without accessing MSTS."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


def verify(root, manifest):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Evidence root must be a directory')
    entries = manifest['files']
    if not isinstance(entries, list) or not entries:
        raise ValueError('Manifest must contain a nonempty files array')
    seen = set()
    checked = 0
    failures = []
    for entry in entries:
        name = entry['path']
        if not isinstance(name, str):
            raise ValueError('Manifest paths must be strings')
        parts = PurePosixPath(name).parts
        if (not parts or PurePosixPath(name).is_absolute() or
                any(x in ('..', '.') for x in name.split('/')) or
                '\\' in name or ':' in name or name != '/'.join(parts)):
            raise ValueError('Invalid relative evidence path: ' + name)
        key = name.casefold()
        if key in seen:
            raise ValueError('Duplicate evidence path: ' + name)
        seen.add(key)
        size, digest = entry['bytes'], entry['sha256']
        if (type(size) is not int or size < 0 or not isinstance(digest, str) or
                len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest)):
            raise ValueError('Invalid size/hash for ' + name)
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Evidence path escapes root: ' + name)
        try:
            h = hashlib.sha256()
            actual_size = 0
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b''):
                    h.update(block)
                    actual_size += len(block)
            actual_hash = h.hexdigest()
            if actual_size != size or actual_hash != digest:
                failures.append(dict(path=name, reason='mismatch', bytes=actual_size,
                                     sha256=actual_hash))
            else:
                checked += 1
        except OSError as exc:
            failures.append(dict(path=name, reason='unavailable', error=str(exc)))
    return dict(root=str(root), entries=len(entries), verified=checked,
                failures=failures, passed=not failures,
                limitation='Byte identity only; not semantic accuracy, capture atomicity, '
                           'authenticity of the manifest or completeness of discovery.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--manifest', type=Path,
                        default=Path(__file__).with_name('local-evidence-manifest.json'))
    args = parser.parse_args()
    try:
        result = verify(args.root, json.loads(args.manifest.read_text(encoding='utf-8-sig')))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps(dict(passed=False, manifest_error=str(exc))))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
