"""Acquire and verify TinyCC's complete, unmodified 0.9.27 source archive.

This maintainer-only utility never executes or extracts downloaded code.
"""
from __future__ import annotations

import hashlib
import io
import os
from pathlib import Path
import tarfile
import tempfile
from urllib.error import URLError
from urllib.request import Request, urlopen

from source_checksums import ROOT

SOURCE_NAME = 'tcc-0.9.27.tar.bz2'
SOURCE_SHA256 = 'de23af78fca90ce32dff2dd45b3432b2334740bb9bb7b05bf60fdbfc396ceb9c'
SOURCE_PATH = Path('third-party/tinycc') / SOURCE_NAME
URLS = (
    'https://download.savannah.gnu.org/releases/tinycc/' + SOURCE_NAME,
    'https://download-mirror.savannah.gnu.org/releases/tinycc/' + SOURCE_NAME,
    'https://download.savannah.nongnu.org/releases/tinycc/' + SOURCE_NAME,
)
MAX_BYTES = 2 * 1024 * 1024
REQUIRED_MEMBERS = {'COPYING', 'README', 'configure', 'Makefile', 'tcc.c', 'libtcc.c',
                    'tcc.h', 'tccpe.c', 'lib/libtcc1.c', 'win32/build-tcc.bat'}


def validate_source(data: bytes) -> None:
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError('TinyCC source SHA-256 mismatch; refusing to use this download.')
    # The pinned digest identifies the full upstream archive, not a repacked snapshot.
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:bz2') as archive:
        names = {member.name.removeprefix('tcc-0.9.27/') for member in archive if member.isfile()}
    if not REQUIRED_MEMBERS <= names:
        raise ValueError('TinyCC source archive is missing required source/build/license files.')


def ensure_source(root: Path = ROOT, *, check_only: bool = False,
                  supplied_archive: Path | None = None) -> Path:
    target = root / SOURCE_PATH
    if target.exists():
        validate_source(target.read_bytes())
        return target
    if check_only:
        raise ValueError('Complete TinyCC source is missing. Before committing/distributing the compiler, '
                         'run: python tools/prepare-commit.py')
    if supplied_archive is not None:
        data = supplied_archive.read_bytes()
        validate_source(data)
    else:
        errors = []
        data = None
        for url in URLS:
            print(f'Downloading compiler source (not executing it): {url}', flush=True)
            try:
                request = Request(url, headers={'User-Agent': 'NEMT-source-preparation/1.0'})
                with urlopen(request, timeout=20) as response:
                    if not response.geturl().startswith('https://'):
                        raise ValueError('Refusing a non-HTTPS download redirect.')
                    candidate = response.read(MAX_BYTES + 1)
                if len(candidate) > MAX_BYTES:
                    raise ValueError('Download exceeds the expected source-archive size limit.')
                validate_source(candidate)
                data = candidate
                break
            except (OSError, URLError, ValueError, tarfile.TarError) as error:
                errors.append(f'{url}: {error}')
        if data is None:
            raise ValueError('Cannot obtain the verified compiler source.\n' + '\n'.join(errors) +
                             '\nDownload the named upstream archive on a connected machine, then use '
                             '--source-archive PATH. No compiler files were changed.')
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=target.parent, prefix=SOURCE_NAME + '.', suffix='.pending')
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
        os.replace(temp_name, target)
    finally:
        Path(temp_name).unlink(missing_ok=True)
    return target
