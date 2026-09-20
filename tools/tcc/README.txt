NEMT's reduced offline source-build toolchain
===========================================

Keep this directory's 50-file layout together. It is the reviewed subset of
TinyCC 0.9.27 x86 and the WinAPI overlay needed by NEMT and its current C tests,
not a general-purpose Windows SDK. No additional download is needed to build
the NEMT frontend with BUILD AND RUN NEMT.bat or run TEST NEMT.bat.

Required components:
  tcc.exe and libtcc.dll
  lib/libtcc1-32.a
  lib/kernel32.def, msvcrt.def, user32.def and gdi32.def
  42 headers in include/ and its original subdirectories
  this README.txt

Do not remove libtcc.dll: tcc.exe depends on it. The separate libtcc/ embedding
API directory and the x64 compiler/archive are intentionally not included.
The selected header/library files and compiler binaries remain unmodified.

Do not substitute the minimal upstream base-header package: it omits required
headers such as commdlg.h, commctrl.h, shellapi.h and tlhelp32.h. New C includes
may require deliberately extending this subset and its pinned file inventory.

Maintainer verification (Python 3.11+, not an end-user build requirement):
  python tools/verify-toolchain.py --require-source

Exact retained-file hashes and provenance:
  third-party/tinycc/FILES.sha256
  third-party/tinycc/UPSTREAM.json

Licenses and complete corresponding source:
  THIRD-PARTY.md
  docs/licenses/TCC-COPYING.txt
  third-party/tinycc/tcc-0.9.27.tar.bz2

Before public source redistribution, run python tools/prepare-commit.py once
on a connected maintainer machine and commit the verified source archive too.
Subsequent runs reuse that archive; the ordinary .bat build never downloads it.
The LGPL/compiler runtime and MinGW header terms differ by component; preserve
the original source/header notices rather than applying a blanket license.
