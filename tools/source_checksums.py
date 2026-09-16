"""Shared source inventory and SHA-256 helpers (maintainer tooling, Python 3.11+)."""
from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'SHA256SUMS.txt'
IGNORED_DIRS = {'.git', 'build', 'work', '__pycache__', '.pytest_cache', '.venv'}


def source_file(rel: PurePosixPath) -> bool:
    """Mirror the project's generated-file rules without requiring Git."""
    if any(part in IGNORED_DIRS for part in rel.parts):
        return False
    if rel.as_posix() in {MANIFEST, 'NEMT.exe', 'NEMT.exe.manifest'}:
        return False
    if rel.name in {'status.json', 'installation.json'}:
        return False
    if rel.suffix.lower() in {'.bak', '.pyc', '.pending'}:
        return False
    if rel.suffix.lower() == '.exe' and rel.parent.as_posix() != 'tools/tcc':
        return False
    return True


def source_paths(root: Path) -> list[Path]:
    result = []
    for path in root.rglob('*'):
        rel = PurePosixPath(path.relative_to(root).as_posix())
        if not source_file(rel):
            continue
        if path.is_symlink():
            raise ValueError(f'Symlinks are not supported in source archives: {rel}')
        if path.is_file():
            result.append(path)
    return sorted(result, key=lambda p: p.relative_to(root).as_posix())


def digest_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def render(entries: dict[str, str]) -> bytes:
    return ''.join(f'{entries[name]}  {name}\n' for name in sorted(entries)).encode('utf-8')


def parse(data: bytes) -> dict[str, str]:
    entries: dict[str, str] = {}
    for number, line in enumerate(data.decode('utf-8').splitlines(), 1):
        if not line.strip():
            continue
        value, separator, name = line.partition('  ')
        path = PurePosixPath(name)
        if (not separator or len(value) != 64 or
                any(c not in '0123456789abcdef' for c in value) or
                not name or '\\' in name or ':' in name or path.is_absolute() or
                '..' in path.parts or path.as_posix() != name):
            raise ValueError(f'Invalid checksum entry at line {number}')
        if name in entries:
            raise ValueError(f'Duplicate checksum entry: {name}')
        entries[name] = value
    return entries


def current(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): digest(p) for p in source_paths(root)}


def check(root: Path) -> int:
    expected = parse((root / MANIFEST).read_bytes())
    actual = current(root)
    problems = []
    problems.extend(f'Missing source file: {p}' for p in sorted(expected.keys() - actual.keys()))
    problems.extend(f'Unlisted source file: {p}' for p in sorted(actual.keys() - expected.keys()))
    problems.extend(f'Changed source file: {p}' for p in sorted(expected.keys() & actual.keys())
                    if expected[p] != actual[p])
    if problems:
        raise ValueError('\n'.join(problems) + '\nAfter reviewing changes, run: python tools/source-checksums.py --write')
    return len(actual)
