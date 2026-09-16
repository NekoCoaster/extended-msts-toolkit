# Retained MinGW-derived header notices

The C/Windows headers bundled under `tools/tcc/include/` retain the copyright and license comments supplied with those individual files. They are source files, not Windows system DLLs. No Microsoft SDK binary is bundled here.

For example, `winapi/windows.h`, `winapi/commdlg.h`, `winapi/winnt.h` and `stdint.h` declare public-domain status and identify the w64 mingw-runtime package. They also disclaim warranty and refer to their original package's DISCLAIMER. `_mingw.h` separately declares public-domain use and disclaims warranties, including merchantability and fitness for a particular purpose. Other headers may carry additional file-specific notices; do not replace them with NEMT's MIT license or a blanket LGPL label.

The source subset is drawn from the TinyCC base headers and the `winapi-full-for-0.9.27.zip` overlay. The exact retained snapshot is identified by `third-party/tinycc/FILES.sha256`. Original header bytes are preserved, rather than rewritten or minified to reduce size. The upstream full header overlay is available from [TinyCC's release directory](https://download.savannah.gnu.org/releases/tinycc/).

See [THIRD-PARTY.md](../../THIRD-PARTY.md) for the compiler source distribution and the distinct runtime-library linking exception.
