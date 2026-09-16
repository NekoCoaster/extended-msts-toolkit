# Build, verify, package and publish

These are contributor instructions. Opening NEMT or building its frontend from an already complete source ZIP does not require Python or Internet access; see the [installation guide](../installation.md).

## Offline frontend build and native tests

From the repository root on Windows:

```bat
build.bat
"TEST NEMT.bat" --ci
```

`build.bat` uses the bundled, reduced TinyCC 0.9.27 x86 toolchain. It produces `build/NEMT.exe` and `build/NEMT.exe.manifest`. Keep the sidecar next to the executable. `BUILD AND RUN NEMT.bat` builds and launches the panel; `clean.bat` removes known frontend/test outputs. Generated files under `build/` are not committed. Do not remove the intentional compiler binaries or committed runtime DLL.

The native tests use temporary synthetic fixtures, not a real game installation. The corrected display tests temporarily relax tracking limits only for synthetic off-screen DPI cases, then restore normal limits. A Windows CI pass does not establish that every injected feature works on every supported OS.

## One-time compiler-source preparation

Maintainer checks and packaging use **Python 3.11+** on a modern development/CI machine. Before the initial public commit of the bundled compiler, run:

```text
python tools/prepare-commit.py
```

This downloads the complete compiler source archive, verifies its pinned SHA-256, stores it under `third-party/tinycc/`, and refreshes source hashes. It does not execute or extract downloaded code. Commit that archive along with its sidecar/metadata. Subsequent runs reuse the archive without downloading. To supply an archive obtained elsewhere, use `--source-archive PATH`. Do not distribute the compiler with only an archive link or hash in place of its source. See [third-party notices](../../THIRD-PARTY.md).

After all later source/documentation edits, explicitly refresh and check the manifest:

```text
python tools/source-checksums.py --write
python tools/prepare-commit.py --check
python tools/verify-toolchain.py --require-source
```

The manifest hashes raw file bytes. Existing `.gitattributes` disables line-ending normalization; preserve batch CRLF and vendored input bytes. Build products, Git metadata, local work directories and the manifest itself are excluded. Do not keep unrelated local files outside the ignored work/build directories.

## Contributor checks

```text
python tests/native-frontend.py
python tests/repository-tools.py
python tools/check-win32-imports.py build/NEMT.exe
python tools/check-win32-imports.py runtime/DINPUT.dll
git diff --check
```

The PE audit is a guard against known incompatible imports, not an exhaustive proof of XP compatibility. Keep real-machine observations separate from source/static tests.

## Runtime changes only

The frontend build uses the existing `runtime/DINPUT.dll`. It does **not** rebuild the injected runtime. For an intentional runtime change:

```text
python runtime/build.py tools/tcc/tcc.exe
```

This rebuilds `runtime/DINPUT.dll`, repairs exports, audits imports and refreshes `runtime/integrity.json`. Review those tracked changes, run the appropriate runtime tests, then refresh source checksums. A frontend/documentation-only change should not rebuild the DLL unnecessarily.

## Package without dirtying source

After a successful frontend build and current source checksums:

```text
python tools/package.py
python tools/source-checksums.py --check
```

The packager reads **both** `build/NEMT.exe` and `build/NEMT.exe.manifest` directly. No root-level staging copies are needed. It validates runtime integrity and relative Markdown links in both the source and the selected release payload. It creates `NEMT.zip` and `NEMT.zip.sha256` beside the repository directory. Use `--frontend PATH` or `--output PATH` when needed; outputs may also go under ignored `build/`, but not among source inputs.

The source `SHA256SUMS.txt` covers the tracked-intent source inventory, including compiler inputs. The **separate manifest inside the release ZIP** covers the release payload. Packaging never overwrites the source manifest, and deterministic ZIP metadata gives identical ZIP bytes for identical input bytes. This does not claim that compiling the application or compiler is reproducible across all machines.

The ready-to-run ZIP contains the frontend, its manifest, runtime, notices and documentation. It excludes the toolchain, complete compiler-source archive, GUI source, tests, frontend build scripts, legacy frontend, GitHub workflows and agent notes. The source archive and its checksum remain independently distributed with the compiler/tagged source tree. No game executable/assets are packaged.

## PR and release workflows

`verify.yml` runs for pull requests, pushes to `main`/`dev`, manual dispatch and reusable calls. It checks source/toolchain/source-archive integrity, builds with the bundled compiler, runs native regression tests, source guards and repository-tool tests, audits PE imports and smoke-tests packaging. Its token is read-only; it never publishes.

`release.yml` runs only on `v*` tags, calls the same verification workflow, then checks `VERSION` and the matching `releases/vVERSION.md`. Only the publishing job has write permission. It builds the frontend again and attaches the end-user ZIP/checksum plus the complete compiler-source archive/checksum. Existing releases are not overwritten.

Do not tag merely to open a PR. Keep `VERSION` and released notes unchanged until an explicit release decision. Do not retag old releases or rewrite published history. Develop on the working branch and submit it for review; a prepared version is not evidence of a published or newly host-tested release.

## Local research

Use `work/` for executable fixtures, probes, disassembly exports, raw logs and VM snapshots. Keep them out of commits and archives. Earlier Frida/Python investigations belong in historical testing documentation, not normal installation instructions. Never present separate MEDS checkpoints as new NEMT measurements.
