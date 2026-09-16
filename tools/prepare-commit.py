"""One-time source-redistribution preparation, then refresh reviewed source hashes.

Run after all intended edits, before git add/commit. Never run automatically from
build.bat: offline end-user builds must not need Python or Internet access.
"""
import argparse
import subprocess
import sys
from pathlib import Path
from source_checksums import ROOT, MANIFEST, check, current, render
from tcc_source import ensure_source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-archive', type=Path,
                        help='use a locally downloaded, unmodified tcc-0.9.27.tar.bz2')
    parser.add_argument('--check', action='store_true', help='verify only; no downloads or writes')
    args = parser.parse_args()
    if args.check and args.source_archive:
        parser.error('--check and --source-archive cannot be combined')
    try:
        source = ensure_source(check_only=args.check, supplied_archive=args.source_archive)
        subprocess.run([sys.executable, str(ROOT / "tools/verify-toolchain.py"), "--require-source"], check=True)
        if not args.check:
            (ROOT / MANIFEST).write_bytes(render(current(ROOT)))
        count = check(ROOT)
        print(f'Compiler source verified: {source.relative_to(ROOT)}')
        print(f'Source checksums OK: {count} files. No GUI/compiler binary was changed.')
        print('Review git status/diff, stage the intended files, and commit. Do not tag a release yet.')
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
