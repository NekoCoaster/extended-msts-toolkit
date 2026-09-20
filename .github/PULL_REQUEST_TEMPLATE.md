## Summary

Describe the change and link the tracking issue (for the native frontend migration: #4).

## Scope and safety

- [ ] No new end-user runtime/build prerequisite was introduced.
- [ ] Optional modern Windows APIs are still capability-detected.
- [ ] Generated build/test executables are not staged.
- [ ] Any intentional runtime DLL/integrity changes are explained.

## Verification

- [ ] `python tools/prepare-commit.py --check` passes.
- [ ] `python tools/verify-toolchain.py --require-source` passes.
- [ ] `build.bat` and `TEST NEMT.bat --ci` pass on Windows.
- [ ] Source guards and repository-tool regression tests pass.
- [ ] Frontend/runtime PE import audits pass.
- [ ] Packaging succeeds without modifying source checksums.
- [ ] `git diff --check` passes.

Attach test output. List the Windows versions/architectures actually tested and separate frontend build/launch results from gameplay/runtime-feature validation. Do not mark unchecked or synthetic-only behavior as host-tested.

## Remaining limits

Record untested environments, unresolved issues or intentional exclusions. Opening this PR does not authorize a release tag or publication.
