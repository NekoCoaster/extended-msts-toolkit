# Third-party notices

NEMT's original control panel, native loader, physics code, tests and documentation are under the [MIT license](LICENSE). Third-party files retain their own licenses and notices. Microsoft Train Simulator assets and executables are not included.

## Tiny C Compiler 0.9.27

The source-build toolchain in `tools/tcc/` is a **reduced x86 Windows subset**, not the full SDK or the entire upstream distribution. It contains 50 files: the compiler, its supporting DLL, the x86 runtime archive, four import-definition files, 42 required headers, and NEMT's local README. The retained compiler/header/library bytes are unchanged from the user-tested toolchain; only the file selection and local README have changed.

TinyCC is LGPL-licensed. Version grants are component-specific: for example, upstream `libtcc.c` grants LGPL version 2 or later, while the distribution supplies the LGPL 2.1 text. Do not describe the entire bundle as `LGPL-2.1-only`. See the retained [LGPL text](docs/licenses/TCC-COPYING.txt), [runtime source and linking exception](docs/licenses/tcc-libtcc1.c), [Windows DLL entry wrapper](docs/licenses/tcc-dllcrt1.c), and [GPL version 2 text](docs/licenses/GPL-2.0.txt). The runtime source has its own GPL grant and linking exception; using the compiler does not make NEMT's original source LGPL code.

### Complete corresponding source

Before committing or publicly redistributing the bundled compiler, run:

```text
python tools/prepare-commit.py
```

This maintainer-only command obtains the **complete unmodified `tcc-0.9.27.tar.bz2`**, verifies its pinned SHA-256, stores it under `third-party/tinycc/`, and refreshes the source checksum manifest. It never executes or extracts the downloaded code. The archive must be committed with the compiler so it accompanies GitHub's repository/source ZIP. Both PR and release verification check that it is present and correct; an upstream link or a checksum sidecar alone is not a substitute for the actual archive.

The ready-to-run `NEMT.zip` excludes the compiler and its source archive. The release workflow separately attaches the source archive and checksum alongside the release assets, in addition to its availability in the tagged source tree. Do not remove the complete source archive from a compiler-containing source distribution merely to save download space.

Upstream references:

- [TinyCC project](https://bellard.org/tcc/)
- [Windows x86 compiler archive](https://download.savannah.gnu.org/releases/tinycc/tcc-0.9.27-win32-bin.zip)
- [Complete 0.9.27 compiler source](https://download.savannah.gnu.org/releases/tinycc/tcc-0.9.27.tar.bz2)
- [Full WinAPI header overlay](https://download.savannah.gnu.org/releases/tinycc/winapi-full-for-0.9.27.zip)
- [Upstream per-file license grant](https://github.com/TinyCC/tinycc/blob/release_0_9_27/libtcc.c)

The complete source archive's SHA-256 is:

```text
de23af78fca90ce32dff2dd45b3432b2334740bb9bb7b05bf60fdbfc396ceb9c
```

This digest is also recorded by [Homebrew's TinyCC formula](https://github.com/Homebrew/homebrew-core/blob/master/Formula/t/tcc.rb). The previously recorded official x86 compiler ZIP digest is `02e2bfe8c272a549b15e4bfa4507bd7e05304692af1761db6c1e8e88af675651`.

`third-party/tinycc/FILES.sha256` pins the 49 retained compiler/header/library inputs; the local README is covered by the main source checksum manifest. These file hashes identify the reviewed snapshot, not a new independent reproduction of the compiler or an independent byte comparison with downloaded upstream binary/header packages. See `third-party/tinycc/UPSTREAM.json` for provenance details.

## MinGW-derived headers

The retained Windows and C library headers carry their original notices. Many explicitly state that they are public-domain files from the w64 mingw-runtime package; `_mingw.h` has its own public-domain/no-warranty notice. Preserve those notices and any applicable upstream terms when changing the subset. They are not covered by NEMT's MIT grant or by a blanket TinyCC license label. See the [header notice summary](docs/licenses/MINGW-NOTICES.md).
