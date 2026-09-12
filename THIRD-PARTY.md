# Third-party notices

The GitHub mark in the form is from [GitHub's official logo assets](https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png). It identifies the repository link; it is not part of the project's MIT-licensed artwork and does not imply GitHub endorsement.

The original patcher, native loader, physics code, tests and documentation are under the [MIT license](LICENSE). Microsoft Train Simulator assets and executables are not included.

The DLL was compiled with Tiny C Compiler 0.9.27 Windows x86. The compiler is not shipped. Its [license](docs/licenses/TCC-COPYING.txt), [runtime source and linking exception](docs/licenses/tcc-libtcc1.c), and [Windows DLL entry wrapper](docs/licenses/tcc-dllcrt1.c) are retained with this package. The runtime source header contains its linking exception; that exception is separate from this project’s MIT license.

Upstream archives: [Windows compiler](https://download.savannah.gnu.org/releases/tinycc/tcc-0.9.27-win32-bin.zip) and [complete corresponding compiler source](https://download.savannah.gnu.org/releases/tinycc/tcc-0.9.27.tar.bz2).

Frida was used during earlier research and for a brief V2 diagnostic attached to an already loaded activity. No Frida component or JavaScript runtime is distributed in NEMT. The separately retained V1 package has its own third-party notices.
