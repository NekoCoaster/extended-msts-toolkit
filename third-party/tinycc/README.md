# TinyCC source and provenance

This folder is redistribution/support material, not an extra runtime dependency. The actual 50-file build toolchain remains under `tools/tcc/`.

`FILES.sha256` records the exact 49 retained compiler/header/library files; the local README is intentionally excluded from that upstream-input lock. `UPSTREAM.json` identifies the version, archive names and provenance limits. Neither file claims that the compiler has been independently rebuilt.

## Required archive preparation

Run `python tools/prepare-commit.py` on a connected maintainer machine before the initial public commit of the bundled compiler. It downloads the complete, unchanged `tcc-0.9.27.tar.bz2`, checks the pinned digest and archive contents, writes it here, and refreshes `SHA256SUMS.txt` at the repository root. The download is never executed or extracted. Review the changes before committing.

For an already downloaded archive:

```text
python tools/prepare-commit.py --source-archive C:/Downloads/tcc-0.9.27.tar.bz2
```

Subsequent runs validate/reuse the existing archive without a download. `--check` verifies everything without modifying files or using the network. A missing archive is an explicit failure, not silently accepted license preparation. Keep the compressed source archive committed; do not add an ignore rule for it. Normal NEMT frontend builds do not need to unpack this archive or install Python.

The source digest is `de23af78fca90ce32dff2dd45b3432b2334740bb9bb7b05bf60fdbfc396ceb9c`, as recorded by the [Homebrew formula](https://github.com/Homebrew/homebrew-core/blob/master/Formula/t/tcc.rb). The source is distributed at [the upstream release location](https://download.savannah.gnu.org/releases/tinycc/tcc-0.9.27.tar.bz2).

## Rebuilding TinyCC itself

The complete archive contains its own `README`, `COPYING`, `configure`, `Makefile`, `win32/build-tcc.bat` and Windows build instructions. Follow those instructions to rebuild the compiler in a **separate** directory. Rebuilding TinyCC is not part of `build.bat`; that script compiles NEMT only. Record the exact compiler version/options and revalidate all retained input hashes before replacing a toolchain binary.

See [the project third-party notices](../../THIRD-PARTY.md) for the compiler, runtime linking exception and header notices. The release workflow also attaches the complete compiler source and checksum separately; it does not include the compiler in the small ready-to-run NEMT ZIP.
