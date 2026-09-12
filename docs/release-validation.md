# Toolkit migration validation — 2026-09-12

These live observations describe the migration DLL hash below, not the later borderless build. The user subsequently confirmed successful host testing; checkpoint: `nemt-migration-host-tested` (`dd8da28`).

## Automated checks

- Native math/gateway suite: 60,000 calls, integer/x87 returns, inactive/paused bypass and caller filtering passed.
- Inherited lifecycle suite: graph membership, connected thrust, no deadline, pause, split, activity reuse, zero strength, steam control input, scoped rod restoration and invalid graph passed.
- Eight feature configurations: correct selected in-memory bytes, crawling dependency validation and default-off diagnostics passed against isolated memory fixtures.
- Three malformed-config cases: invalid boolean, out-of-range strength and nonnumeric strength rejected without modifying feature bytes.
- Shared mutation transaction: overlapping address claims rejected; a later mismatched byte rolled back an earlier write.
- Installer: 32 feature/variant cases across base/widescreen/LAA combinations; clean executable invariance, dry-run, unrelated wrapper preservation and uninstall passed.
- Migration: Ready V1, Native V2 and current MEDS packages upgraded successfully, with verified executable backups and known legacy payload retirement. Subsequent configuration changes and uninstall preserved the clean executable hash.

## Fresh live smoke check

DLL SHA-256: `0df0a3c77a6b16f192f064ef543cd3469049f4807f600e4b0c140b76a298d5f1`.

Normal `train.exe -vm:w` startup; no Frida attached. The [menu snapshot](evidence/menu.json) shows original activity-end/camera/frame-prefix bytes. The [activity snapshot](evidence/activity.json) shows the two selected in-memory changes and installed crawl frame hook, while the disk executable remained SHA-256 `69218fce876298c684a2140c7d3925a452c47bb10037ffd8c491f65c5c0c6e7a`.

The configured route showed a 2 mph limit. The eight-car Acela derailed naturally; memory reads confirmed derail flags. External camera selection worked, forward and 50% throttle controls were accepted, and activity exit returned normally to the menu. The game then closed normally. Diagnostic logging remained disabled and its installer placeholder was unchanged.

This smoke check did not quantitatively isolate propulsion from gravity/collisions, re-test every custom trainset, or benchmark performance. Steam physics retains inherited automated coverage; no new live steam session is claimed. The later borderless build has separate [automated coverage and pending visual checks](borderless.md).

## Reproduction

Compile `tests/native.c`, `tests/lifecycle.c`, `tests/features.c` and `tests/transaction.c` with x86 TCC. Lifecycle/features include the loader and need `-ladvapi32 -luser32`. Run the feature test in a fresh process for each value 0–10 (8–10 test malformed configuration), passing a newly created scratch directory followed by that number. Installer tests take `-BaseExe`, `-WidescreenExe`, `-Scratch` and `-LegacyPatchers` (an array of the prior scripts with their runtime folders). No game executables are shipped.
