# Native frontend migration: validation and handoff

This is the current migration checkpoint for issue #4. It supplements, rather than rewrites, historical runtime/gameplay evidence.

## Scope preserved during repository finalization

The native C frontend, settings/JSON/viewport models, GUI regression harness, source manifest sidecar, injected runtime source/DLL and the 49 retained compiler/header/library inputs were left unchanged during the final housekeeping pass. Changes are limited to build/test diagnostics, cleanup, contributor tooling, source/release packaging, CI and documentation/notices.

The toolchain remains the 50-file reviewed x86 subset (including the local README). Generated GUI/test executables are deliberately absent from the commit-ready source delivery. The frontend and tests still build offline through XP-compatible batch scripts.

## Evidence and its limits

The maintainer reported successful frontend builds/launches with the trimmed toolchain on Windows XP, Windows 7 and Windows 11. This is **not** evidence that every injected runtime feature has been exercised on each of those operating systems. Windows 10 remains an intended target without a corresponding host-test report in this checkpoint. Low-memory Pentium-class usability remains a design goal, not a measured memory benchmark.

The portable settings model, viewport model, source-level guards and new repository-tool regression suite can run independently of a Windows GUI. PE import audits are useful guards against known unsupported APIs; they are not exhaustive proofs of OS compatibility. A packaging test with a supplied EXE does not prove that a fresh Windows compiler build produced that EXE.

The earlier synthetic DPI/scrollbar failures were traced to a test-window tracking-limit assumption. The corrected harness is included. Preserve the final native test output from an actual Windows run; do not replace that evidence with a static check or infer a zero-failure rerun merely from the application opening successfully.

## Maintainer preparation and checks

Run `python tools/prepare-commit.py` once on a connected development machine. This vendors the verified complete compiler source and refreshes hashes without changing the compiler or GUI. If the archive is missing, both PR and release checks deliberately fail. See [Build and publishing](maintenance.md) and [third-party notices](../../THIRD-PARTY.md).

Run `build.bat`, `TEST NEMT.bat --ci`, the Python source/repository-tool checks and frontend/runtime PE audits. Check packaging without source-tree modification. Attach the Windows test output and OS/architecture details to the PR. A working frontend does not justify silently waiving test failures.

## Release boundary

This is a source-branch/PR preparation change, not a release. `VERSION`, historical release notes and runtime integrity hashes have not been bumped or regenerated. Publication requires a separate reviewed version/release-note decision and an explicitly pushed matching tag. PR verification has read-only permissions and cannot publish.
