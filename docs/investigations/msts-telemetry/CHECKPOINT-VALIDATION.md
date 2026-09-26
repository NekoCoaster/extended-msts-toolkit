# Research checkpoint validation — 26 September 2026

Branch: `research/issue-7-msts-telemetry`, based on main `5cd5896`. Research files are confined to this directory; the repository source checksum inventory is refreshed. Production source, committed runtime DLL, build entry points and version are unchanged.

Passed locally:

- All 32 checkpoint JSON files parsed; all 23 Python scripts parsed without executing live probes.
- All 735 inventory IDs unique and carrying meaning, applicability, type, units, extraction, evidence, lifecycle and limitation fields. This is a structure check, not semantic proof of every candidate.
- Source/toolchain/corresponding-source verification.
- Bundled native frontend build.
- Frontend model: 52 checks; viewport model: 104,984 cases / 998,600 assertions; native GUI/installer: 302 checks, zero failures.
- Frontend source guards: 28 checks; repository-tool tests: 29 tests.
- Frontend and committed runtime PE32/x86 import audits.
- Packaging smoke test; source manifest unchanged by packaging. No release was published.

Incomplete local gate: `TEST NEMT.bat --ci` stopped when Windows Device Guard blocked `build/high-resolution-test.exe` (exit 4551). The later native tests in that batch were not run. This is not a passed full native suite, and the policy was not bypassed or changed. Remote PR checks may provide additional evidence separately.

Historical gameplay findings and native-byte verification are documented in their individual reports. This publication check did not repeat the historical captures and does not establish complete telemetry discovery.

## Track-item follow-up

The inventory now has 750 unique entries. Updated JSON and Python sources parse successfully. Native pass36/pass37 instruction verification passed; all stored platform/siding/speed-post comparisons and common item fields agreed with the installed TDB within documented tolerances.

GitHub Actions run 36245441062 (Verify source and native frontend) completed successfully for checkpoint commit eb0e87fee5fdeca90d2e4a7437cf80c38509ed03. This is remote workflow evidence for that commit; it does not remove the local Device Guard observation or prove gameplay findings beyond their cited captures. New follow-up commit checks are separate.

## Speed-cap and track-interaction checkpoint

763 unique candidates:206 direct-read candidates/structures,16 derived,68 cab channels,473 configuration leaf paths. All51 published JSON files and28 Python scripts parsed; every inventory row has the required provenance/meaning/lifecycle/limitation fields. This verifies structure, not complete live semantics.

Source guards28 and repository-tool tests29 passed. Frontend and committed runtime PE import audits passed using the existing unchanged binaries. Native byte comparisons for passes38-47 and50-54 matched the installed disk/live process. The paused captures verified speed-cap reproduction, freight class, pickup absence and retained sound-region values; no new moving crossing/refill/hazard test was performed.

Production code and build inputs remain unchanged. The full native batch was not rerun for this research-only update: its earlier Device Guard block remains unresolved, with no bypass attempted. The initial build/model/GUI results above remain historical evidence, not new tests of this checkpoint.


## Camera, consist, cadence and configuration checkpoint

806 unique candidates:215 direct-read candidates/structures,16 derived,68 cab channels and507 configuration paths. All66 published JSON files and35 Python scripts parse. The canonical local audit checks182 evidence paths and126 unchanged asset hashes; it is tied to the unstripped local inventory hash. The publication intentionally strips embedded decompiler excerpts, so its inventory hash differs.

New evidence includes cab/front/rear/trackside/cab mode switches, exact float32 consist mass/length aggregation, a bounded pause/resume cadence test, sound-region handle lifecycle tracing and extended cab-helper limitations. Configuration coverage now retains long leaves and values beside child blocks, and correctly handles the observed anonymous annotation groups. These are evidence improvements, not keep/drop prioritization or proof of all live semantics.

363 additional local evidence files were hashed; existing manifest entries were verified unchanged. Raw captures, native exports and game assets remain local. Source guards28, repository-tool tests29 and both PE import audits passed again using unchanged binaries. No production source/build/version change or NEMT integration was made. The earlier full-native Device Guard block remains unresolved; that batch was not rerun or bypassed. GitHub run36246913033 passed for previous commit285a0ff, not for this new checkpoint.
