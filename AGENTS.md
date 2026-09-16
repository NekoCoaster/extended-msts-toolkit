# Agent notes

NEMT has two native components:

- `src/nemt.c`: the dependency-light Win32/x86 control panel and installer.
- `runtime/loader.c`: the injected x86 `DINPUT.dll` runtime.

The frontend targets Windows XP SP3 APIs (`0x0501`). Do not introduce mandatory imports newer than XP; resolve optional modern APIs dynamically. Keep runtime dependencies to Win32 system DLLs already present on the target OS. Do not change the working GUI while performing packaging or documentation housekeeping.

Build the frontend with `build.bat` using the reviewed 50-file TinyCC 0.9.27 x86 subset in `tools/tcc/`. `BUILD AND RUN NEMT.bat` and `TEST NEMT.bat` are offline, XP-compatible entry points; never introduce Python, PowerShell, an SDK installer or a network download into their normal path. Keep `NEMT.exe.manifest` beside the generated executable. The `C:\Tools\tcc\tcc.exe` fallback is for an explicitly configured developer machine, not the CI toolchain.

Contributor tooling uses Python 3.11+. Rebuild the runtime only when intended, with `python runtime/build.py tools/tcc/tcc.exe`; this changes the committed runtime DLL/integrity hash. Refresh reviewed source checksums with `python tools/source-checksums.py --write`. `python tools/prepare-commit.py` additionally ensures the full corresponding compiler source is vendored; its `--check` mode never downloads or writes. Preserve the compiler-source archive when redistributing the compiler.

Package releases with `python tools/package.py`: it reads `build/NEMT.exe` and `build/NEMT.exe.manifest`, creates the small end-user ZIP outside the repository, and does not rewrite any source file. Do not copy a stale root-level EXE into a release or regenerate source hashes by packaging. Source and release manifests serve different inventories.

Run `TEST NEMT.bat --ci`, the source guards, repository-tool tests and PE import audits before review. Native Windows execution, portable model checks and user-reported host observations are different evidence; do not claim more than was actually tested. PR checks have read-only permissions and must not publish. Release publication remains tag-only and requires matching VERSION/release notes. Do not bump versions, create tags or overwrite releases without an explicit release task.

The former PowerShell frontend is under `legacy/` and is reference material only. Never reintroduce it as a runtime dependency. Never present old MEDS traces as new toolkit measurements.
