# Build, package and publish

These instructions are for contributors. Installing NEMT requires only the packaged control panel and its accompanying files; see the [installation guide](../installation.md).

## Build

From the repository root, use Python and the x86 Tiny C Compiler 0.9.27 toolchain:

```powershell
python runtime/build.py C:/Tools/tcc/tcc.exe
python tools/package.py
```

Building refreshes runtime/DINPUT.dll and runtime/integrity.json. Packaging validates DLL integrity, relative Markdown links, archive contents and exclusions, updates SHA256SUMS.txt, and creates NEMT.zip plus its SHA-256 file beside the repository directory. No compiler or game executable is distributed. Licensing notices remain in THIRD-PARTY.md and docs/licenses.

Run checks appropriate to a runtime or installer change. Documentation-only changes need link, terminology and package validation, not new claims of gameplay testing.

## Release publication

The repository's VERSION file identifies the package. Keep it synchronized with the matching releases/vVERSION.md notes before publishing. A vVERSION tag triggers the release workflow, which checks committed hashes and attaches NEMT.zip and its checksum to the GitHub release. Existing releases are not overwritten.

Do not retag old releases, rewrite published history or describe an alpha checkpoint as a newly tested stable build. Develop on `dev` and submit release changes to `main` for review. The prepared 1.1.0 version is not published until a matching tag is explicitly authorized.

## Local research

Use work/ for executable fixtures, probes, disassembly exports, raw logs and VM snapshots. Keep them out of commits and archives. Earlier Frida and Python investigations belong in testing documentation; they are not part of the normal installation or play instructions.

The authorized repository is NekoCoaster/extended-msts-toolkit. Preserve the separate MEDS checkpoints and unrelated game files.
