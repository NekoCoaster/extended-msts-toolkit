"""Check (default) or explicitly regenerate the source-only checksum manifest."""
import argparse
from source_checksums import ROOT, MANIFEST, check, current, render


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--check', action='store_true', help='verify contents and inventory (default)')
    modes.add_argument('--write', action='store_true', help='replace the manifest after reviewed source changes')
    args = parser.parse_args()
    try:
        if args.write:
            entries = current(ROOT)
            (ROOT / MANIFEST).write_bytes(render(entries))
            print(f'Source checksums written: {len(entries)} files; build outputs excluded.')
        else:
            print(f'Source checksums OK: {check(ROOT)} files.')
        return 0
    except (OSError, ValueError, UnicodeError) as error:
        print(f'ERROR: {error}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
