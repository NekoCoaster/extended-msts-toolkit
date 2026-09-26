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


## Activity, clock, evaluation and stored vehicle motion checkpoint

826 unique candidates:233 direct-read candidates/structures,18 derived,68 cab channels and507 configuration paths. All87 published JSON files and39 Python scripts parse. The canonical audit checks224 evidence paths and126 unchanged asset hashes; the local inventory hash differs from the publication because embedded decompiler excerpts are omitted.

Added evidence covers activity trigger/outcome semantics and finite location-condition reconstruction, independent elapsed/day clocks with installed NEMT timing patches, capped evaluation lists and installed error labels, and stored per-car motion plus loaded Durability. Empty or stopped reads are explicitly distinguished from observed transitions. Moving/reversing/AI motion, nonzero new evaluation events and broader discovery coverage remain open. Pass70/71 clock-related live mismatches and pass82 debug-call mismatch are documented; no blanket live-byte equality claim is made.

Verified4140 existing raw-evidence hashes unchanged and added1429 local-only evidence entries. Source/toolchain verification,28 source guards,29 repository-tool tests and both PE import audits passed using unchanged existing binaries. No production code, build input, version or integration changes. The earlier full-native Device Guard block remains unresolved; the batch was not rerun or bypassed. GitHub run36248751990 succeeded for the preceding2978ac2 commit; the new commit's remote checks are separate.

## Steam, electric, motion and event checkpoint — 27 September 2026

866 unique candidates:272 direct-read candidates/structures,19 derived,68 cab channels and507 configuration paths. All132 published JSON files and56 Python sources parse. The canonical audit checks313 evidence paths and126 unchanged asset hashes. Verified5569 previous raw-evidence hashes unchanged and added553 local-only entries. Publication strips embedded decompiler excerpts; its inventory hash intentionally differs from the canonical audit hash.

New evidence covers moving player/AI stored motion, shared Default parameters, steam cab/debug fields and producer cadence, electric cab/voltage/control transitions, stale electric throttle caches and event receiver routing/scalars. Steam coal-burn units have a float32 mass-delta check; AI stored acceleration stays zero despite changing speed. Electric throttle scalar1 has a nonzero runtime transition. The sampled traction gate bit does not guarantee cache freshness. Raw event bits cannot supply counts or a complete ordered history.

Pass101 has three live entry-span mismatches, separately recorded; it was an exploratory path rather than evidence that all native instructions match. Earlier pass70/71/82 exceptions remain documented. No blanket byte-equality claim follows from the newer passing targeted comparisons. Moving electric traction, event clearing, broader AI systems and the full remaining scope in CHECKPOINT.md are still open.

The full native batch remains incomplete due to the previously observed Device Guard exit4551. No policy bypass or equivalent retry is part of this documentation checkpoint. Current validation passed: source/toolchain/corresponding-source checks for507 files,28 frontend source guards,29 repository-tool tests and both existing frontend/runtime PE import audits. These are documentation/tooling checks using unchanged binaries, not new full native gameplay validation.


## Receiver lifecycle and brake systems checkpoint — 27 September 2026

887 candidates:293 direct-read candidates/structures,19 derived,68 cab and507 configuration paths.151 published JSON files and63 Python sources parse. The canonical audit checks346 evidence paths and126 unchanged asset hashes.6122 existing raw evidence hashes remain unchanged;224 entries added (6346 total). Native exports/captures remain local and inventory decompiler excerpts are stripped in publication.

Receiver-list discovery observed20 receivers,9 linked to player cars,48 declared streams, camera/distance activation changes and processing timestamps advancing while simulation remained paused. Event masks coalesce and clear; they cannot represent a complete ordered event history or prove playback. Twelve flags changed during cab/external/cab observation and all returned to baseline.

Brake observation captured1740 samples, zero reader errors, and13920 exact pressure-to-force formula comparisons. A rising pressure reference/latch transition was observed; full release/falling events, actual wheel force and AI brakes remain unverified.23 named configuration fields now have loaded native-definition mappings; two new candidates read actual auxiliary/emergency reservoir pressures. The loaded configuration values are not the live reservoir values. Six unequal-cylinder samples cannot establish physical propagation timing under sequential reads.

Previous66f5bd1 remote workflow36254778869 completed successfully. This checkpoint's new remote checks are separate. The prior full-native DeviceGuard4551 block remains unresolved; no policy bypass or equivalent retry was attempted. Production sources and binaries remain unchanged. Goal remains active and PR remains draft.

Validation passed:534 source files and complete bundled toolchain/source verified;28 frontend source guards,29 repository-tool tests and both PE import audits passed using unchanged binaries. JSON/Python parsing and diff whitespace checks passed. These checks do not prove complete discovery or replace runtime validation.

## Brake release and moving powered-car checkpoint

889 candidates:295 direct-read candidates/structures,19 derived,68 cab channels and507 configuration paths.158 published JSON files and70 Python sources parse. Canonical audit checks363 evidence paths and126 unchanged installed-asset hashes. All6346 previous raw-evidence hashes were verified unchanged;88 added (6434 total). Raw evidence remains local; publication strips embedded decompiler excerpts.

Acela brake selector modes and mode-relative fractions now have native lookup evidence. A failed release attempt is preserved separately from the successful release and settling captures. All eight cars reached zero cylinder pressure and110 pipe pressure; a12.9296875 simulation-second capture gap prevents claiming exact time to zero. The pressure-event reference retained a nonzero residual despite zero cylinder pressure.

Moving electric capture:1182 samples, zero reader errors, positive force/current under released brakes and zero outputs while subsequently coasting. Paired-powered-car capture:875 samples, zero errors, identical front/rear stored force and power, rear current always zero and rear sampled gate bit clear. Neither rear current nor the lead gate interpretation can be generalized to independent per-car measurements. Shared force ramp native tracing retains the unusual car-field predicate, asymmetric time factors and untested reverse behavior; no claim of actual wheel-rail force or AI validation.

Validation:548 source files and complete bundled toolchain/source verified;28 source guards,29 repository-tool tests and both existing-binary PE import audits passed. Production code and binaries remain unchanged. Previous e695189 remote workflow36256558628 succeeded. New commit checks are separate. The earlier full native Device Guard4551 block remains unresolved; no equivalent retry or bypass was attempted. The full discovery goal remains active and incomplete.

## AI service and station records checkpoint

895 candidates:301 direct-read candidates/structures,19 derived,68 cab channels and507 configuration paths.180 published JSON files and77 Python sources parse. Canonical audit checks390 evidence paths and126 unchanged installed-asset hashes.6434 previous raw-evidence hashes verified unchanged;376 added (6810 total). Raw captures/native exports remain local and embedded decompiler excerpts remain omitted.

AI service400005 was observed with22 physical cars and changing speed while sampled brake-force/cylinder/traction/power fields remained zero, including the stable-read subset. The capture includes666 failure-alert paused samples after the player passed a red signal; it is not uninterrupted120-second gameplay or evidence of successful signal clearance.47 consecutive one-second AI service speed calculations matched final float32 values using target-capped integration. This is not independently measured vehicle acceleration.

Native source tracing resolves baseline versus selected-record efficiency and the installed baseline clamp helper. Morning in Maryland provides two populated player station records: platform/skip/efficiency match, while live path distances differ slightly from text declarations. Scheduled arrival/departure assignments and merge rules are traced separately from recorded event times. Recorded arrival can be synthesized from scheduled arrival. Departure/selection transitions and AI stop-time applicability remain open.

Validation passed:582 source files and bundled toolchain/corresponding source verified;28 frontend guards,29 repository-tool tests and both unchanged-binary PE import audits. Previous9f9d445 remote workflow36257858496 passed; new commit checks are separate. The earlier full-native Device Guard4551 block remains unresolved; no equivalent retry or bypass. No production code, binaries, version, protocol or runtime integration changed. Goal active, discovery incomplete, PR draft.

## Station transitions and coupling/motion interpretation checkpoint

902 candidates:304 direct-read structures/fields,23 derived,68 cab channels,507 configuration paths.193 published JSON files and83 Python sources parse. Canonical audit covers409 evidence paths and126 unchanged original-asset hashes.6810 prior raw-evidence hashes verified unchanged;296 added,7106total. Raw exports/captures remain local;embedded decompiler excerpts remain stripped.

Station cue flags cross a scheduled departure while actual departure remains unset. Identity-based successor semantics and null ambiguity are traced;boarding/departure/next-stop transitions remain unvalidated. Coupling endpoint geometry/velocity helpers are traced and paused geometry read;derived endpoint velocity is not yet a validated trajectory derivative. Preserved moving player/AI captures change orientation with zero stored angular velocity. Native AI placement resets angular momentum before recomputing angular velocity. Player position/velocity discrepancies remain with either simulation or wall time;no correction factor or stock-physics conclusion follows.

Validation:603 source files and bundled toolchain/source verified;28 frontend guards,29 repository-tool tests,both unchanged-binary PE import audits and whitespace checks passed. Previous651591a remote workflow36259730661 succeeded. New commit checks are separate. Earlier full-native Device Guard4551 block remains unresolved;no retry or bypass. No production code or binaries changed. Goal active,incomplete;PR remains draft.
