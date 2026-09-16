"""Build a deterministic end-user ZIP without modifying the source tree.

Python 3.11+ is contributor tooling only; neither the GUI nor build.bat uses it.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

from source_checksums import ROOT, MANIFEST, check, digest, digest_bytes, render, source_file, source_paths

ROOT_FILES = {'README.md', 'LICENSE', 'THIRD-PARTY.md', 'VERSION'}
RELEASE_DIRS = {'docs', 'releases', 'runtime'}
FORBIDDEN_SUFFIXES = {'.bak', '.pyc', '.pub', '.exe', '.pending'}
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def links_in(data: bytes):
    text = data.decode('utf-8')
    # Fenced examples are not actual document links.
    text = re.sub(r'^```[^\n]*\n.*?^```\s*$', '', text, flags=re.M | re.S)
    for match in re.finditer(r'!?\[[^\]]*\]\(([^)]+)\)', text):
        target = match.group(1).strip()
        if target.startswith('<') and '>' in target:
            target = target[1:target.index('>')]
        else:
            target = target.split(' "', 1)[0].split(" '", 1)[0]
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        yield unquote(parsed.path)


def normalized_link(name: str, target: str) -> str:
    if target.startswith('/'):
        raise ValueError(f'Absolute local Markdown link: {name}: {target}')
    parts = list(PurePosixPath(name).parent.parts)
    for part in PurePosixPath(target).parts:
        if part == '..':
            if not parts:
                raise ValueError(f'Markdown link escapes archive: {name}: {target}')
            parts.pop()
        elif part != '.':
            parts.append(part)
    return '/'.join(parts)


def validate_links(payload: dict[str, bytes]) -> None:
    names = set(payload)
    for name, data in payload.items():
        if not name.lower().endswith('.md'):
            continue
        for target in links_in(data):
            resolved = normalized_link(name, target).rstrip('/')
            if resolved not in names and not any(p.startswith(resolved + '/') for p in names):
                raise ValueError(f'Broken relative Markdown link: {name}: {target}')


def release_file(rel: PurePosixPath) -> bool:
    return (rel.as_posix() in ROOT_FILES or
            (bool(rel.parts) and rel.parts[0] in RELEASE_DIRS and source_file(rel)))


def payload_for(root: Path, frontend: Path) -> dict[str, bytes]:
    check(root)  # Packaging must never silently repair a stale source manifest.
    source = {p.relative_to(root).as_posix(): p.read_bytes() for p in source_paths(root)}
    validate_links(source)
    integrity = json.loads(source['runtime/integrity.json'])
    if digest_bytes(source['runtime/DINPUT.dll']) != integrity['DINPUT.dll']:
        raise ValueError('Runtime DLL integrity mismatch; rebuild and review it first.')
    manifest = frontend.with_name(frontend.name + '.manifest')
    if not frontend.is_file() or not manifest.is_file():
        raise ValueError('Build the frontend first: build.bat (EXE and manifest are both required).')
    payload = {name: data for name, data in source.items() if release_file(PurePosixPath(name))}
    for name, data in payload.items():
        p = PurePosixPath(name)
        if (p.suffix.lower() in FORBIDDEN_SUFFIXES or
                p.name in {'MstsCrawl.dll', 'DINPUT.def', 'known_hosts'}):
            raise ValueError(f'Unexpected file in release: {name}')
        if re.search(rb'-----BEGIN [A-Z ]+PRIVATE KEY-----', data):
            raise ValueError(f'Private key material in release input: {name}')
    for name in ROOT_FILES:
        if name not in payload:
            raise ValueError(f'Missing required release input: {name}')
    payload['NEMT.exe'] = frontend.read_bytes()
    payload['NEMT.exe.manifest'] = manifest.read_bytes()
    validate_links(payload)
    payload[MANIFEST] = render({name: digest_bytes(data) for name, data in payload.items()})
    return payload


def package(root: Path, frontend: Path, archive: Path) -> dict:
    root, frontend, archive = root.resolve(), frontend.resolve(), archive.resolve()
    if archive.is_relative_to(root) and archive.relative_to(root).parts[0] != 'build':
        raise ValueError('Write release outputs outside the source tree, or under build/.')
    payload = payload_for(root, frontend)
    archive.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=archive.name + '.', suffix='.pending', dir=archive.parent)
    os.close(fd)
    temp = Path(temp_name)
    try:
        with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as output:
            for name in sorted(payload):
                info = zipfile.ZipInfo('NEMT/' + name, FIXED_TIME)
                info.create_system = 3
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                output.writestr(info, payload[name], compresslevel=9)
        with zipfile.ZipFile(temp) as output:
            if output.testzip() is not None:
                raise ValueError('Release ZIP integrity check failed.')
            for name, data in payload.items():
                if output.read('NEMT/' + name) != data:
                    raise ValueError(f'Release ZIP verification failed: {name}')
        os.replace(temp, archive)
    finally:
        temp.unlink(missing_ok=True)
    checksum = archive.with_suffix(archive.suffix + '.sha256')
    checksum.write_bytes(f'{digest(archive)}  {archive.name}\n'.encode('utf-8'))
    return {'archive': str(archive), 'zipBytes': archive.stat().st_size,
            'exeBytes': len(payload['NEMT.exe']), 'dllBytes': len(payload['runtime/DINPUT.dll']),
            'files': len(payload), 'sourceManifestUnchanged': True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frontend', type=Path, default=ROOT / 'build/NEMT.exe')
    parser.add_argument('--output', type=Path, default=ROOT.parent / 'NEMT.zip')
    args = parser.parse_args()
    try:
        print(json.dumps(package(ROOT, args.frontend, args.output), indent=2))
        return 0
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(f'ERROR: {error}')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
