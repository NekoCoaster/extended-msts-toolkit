"""Verify the reviewed 50-file x86 toolchain without executing the compiler."""
import argparse
from pathlib import Path
from source_checksums import ROOT, digest, parse
from tcc_source import ensure_source


def verify(root: Path) -> int:
    folder = root / 'tools/tcc'
    entries = parse((root / 'third-party/tinycc/FILES.sha256').read_bytes())
    actual = {p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()}
    wanted = set(entries) | {'README.txt'}
    if actual != wanted:
        raise ValueError(f'Toolchain inventory mismatch. Missing: {sorted(wanted - actual)}; '
                         f'unexpected: {sorted(actual - wanted)}')
    for name, expected in entries.items():
        path = folder / name
        if path.is_symlink() or digest(path) != expected:
            raise ValueError(f'Toolchain file changed: {name}')
    return len(actual)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-source', action='store_true', help='also require the complete compiler source')
    args = parser.parse_args()
    try:
        print(f'Bundled x86 toolchain OK: {verify(ROOT)} files (49 pinned upstream-input files + local README).')
        if args.require_source:
            ensure_source(check_only=True)
            print('Complete compiler source archive verified.')
        return 0
    except (OSError, ValueError) as error:
        print(f'ERROR: {error}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
