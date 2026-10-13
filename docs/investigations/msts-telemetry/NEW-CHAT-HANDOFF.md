# MSTS telemetry research handoff

Updated 13 October 2026. Research is incomplete. This organization checkpoint adds no live experiment; recheck simulator state before any future observation.

## Current checkpoint

Previous published research checkpoint: `2943bfd`, branch `research/issue-7-msts-telemetry`, draft [PR 9](https://github.com/NekoCoaster/extended-msts-toolkit/pull/9).

Canonical workspace: `C:/dev/Codex/2026-09-10/msts-telemetry`. Publication worktree: `C:/codex/worktrees/NEMT-telemetry-research`, under `docs/investigations/msts-telemetry`.

Published through `73c0be1`: automatic/manual loading-duration analysis, the guarded manual reader, force-configuration lifetime corrections, moving body-accumulator observations, and force-entry/clear predicates. These establish bounded observations and conditions, not independent AI force simulation or native execution of the inspected gates. See [station timing](STATION-TIME-FINDINGS.md) and [wheel/adhesion](WHEEL-ADHESION-FINDINGS.md).

Published metadata cleanup: seven existing inventory records now acknowledge retained player/AI or ownerless observations while preserving semantic, cadence and lifecycle limitations. See `population-metadata-review-20261013.json` and [vehicle systems](VEHICLE-SYSTEM-FINDINGS.md). The other 1,060 records are unchanged by that review.

Current local inventory: **1,074 candidates** (466 direct, 29 derived, 68 cab, 511 configuration). Structural audit passes: 1,053 evidence paths and 151 source hashes. These checks do not establish semantic correctness or completion.

## Start here

1. Use [research navigation](RESEARCH-NAVIGATION.md), then the relevant [coverage row](DISCOVERY-COVERAGE.md).
2. Query `python research_index.py 005a3941 --limit 8` or a topic such as `STATION`. Read the referenced finding before exporting again.
3. Check Git state and existing evidence. Validate process/build only when new live work requires it.
4. State a discriminating question; batch related analysis and publish coherent checkpoints.

Retained platform follow-up: platform loader defaults are now traced and current-byte verified: absent minimum-wait input stores float32 180; absent passenger input stores uint32 20. See TRACK-ITEM-FINDINGS.md. These are configuration defaults, not proof of runtime scheduling use. A fresh read confirms the same paused initial-station state, with no onset timer.

Retained force follow-up: setter0060ceee and callers establish train mode1 sets car mask2; mode3 clears it. Current paused snapshot covers8player/11AI cars with matching mode/flag correspondence. Three candidates added. Collision response sets body mask2 and gated placement clears the body word; live transitions and exhaustive writers remain open. See AI-SYSTEM-UPDATE-FINDINGS.md.

Retained Friction follow-up: token4017c maps ten scalars at definition478..49c. Current guarded19car snapshot captures the full block; one candidate added. Final four consumers, exact branch units and runtime contributions remain open. See WHEEL-ADHESION-FINDINGS.md and friction-inputs-summary-20261013.json.

Retained interaction follow-up: paired horizontal-distance history and dispatcher predicates are traced. Bounded180record snapshot passes guards,all state0;seven synthetic tests pass. Service128 initializer sums definition lengths with a conditional208 addition. Three candidates added. Static transfer/removal callers now establish threshold refresh after definition-list changes; nonzero live transitions, coupling timing and exhaustive writers remain open. Collision extraction also now covers8player/11AI cars;two speedpost records reconciled.

## Organization checkpoint and resumption

The navigation map, compact coverage matrix and historical archives are retained. This cleanup reconciles the summaries with existing evidence; it adds no simulator observation. Pause the research goal after checkpoint validation at the user's request.

Latest retained follow-up: [track interaction](TRACK-INTERACTION-FINDINGS.md) now distinguishes service threshold refresh callers from an alternate writer of physical train length. [Consist aggregates](CONSIST-AGGREGATE-FINDINGS.md) and the existing `train.definition_length_sum` record preserve that distinction. The ordinary writer sums definition lengths; another gated caller can use the extra-inclusive service formula. Static calls do not establish live coupling behavior.

Next bounded question on resumption: compare current player and AI physical length caches with their service thresholds and definition sums. The old `probe_consist_totals.py` needs pointer/content/clock guards before using a new capture as evidence. This question remains untested; no new capture is required for this cleanup. Broader outstanding work remains in the coverage matrix.

## Latest evidence and next decision

[Station timing](STATION-TIME-FINDINGS.md) contains the latest opening capture, loading-duration reconstruction and activity override analysis. The opening capture recorded a positive automatic-player countdown and station selection advance while recorded times stayed zero. Its archived service-stability check is invalid; corrected source and a separate pointer check preserve that limitation.

The local duration model counts seven eligible cars and reproduces the first timer value using later inputs and an assumed quarter-second update. This corroborates the formula without proving simultaneous onset inputs. Override lookup prefers the selected endpoint, then its pair, then the route count; the current empty override list provides no positive runtime validation. Manual boarding has a separate path.

Manual duration is now traced to physical-vehicle endpoint membership and strict position bounds, distinct from automatic length-budget counting. Current bytes and constants match; contemporaneous onset counting remains unvalidated. Helper argument tracing now confirms the paired endpoint supplies the manual waiting count; the reader is corrected and eight synthetic tests pass. Next station question: capture the manual contributing count at timer onset, trace minimum-wait use, or obtain an appropriate positive override fixture. Broader gaps remain in the coverage matrix; this is not the whole research objective.

Last recorded simulator state (not refreshed by this documentation cleanup): Passenger Activity Tutorial, paused on a late-arrival message, still at initial platform 9 by selected record; PID 39096. Reverser was Reverse (-1), throttle 0 and speed 0. No sampler remained running. The proposed next fixture is Forward travel to Yoyogi Hachiman, stopping before pressing Enter. Recheck state before any future observation; the tutorial message does not prove arrival.

## Boundaries and history

Supported image SHA256: `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`. User installation context: MSTSBin, no NEMT loaded, no community night-cab addons. Rediscover process IDs and pointers; historical patches are not current behavior.

Preserve game assets/saves. External reads only; no injection, process writes, debugger/native calls, production integration or candidate ranking. See [extraction handoff](EXTRACTION-HANDOFF.md) for validity requirements.

The [prior handoff archive](NEW-CHAT-HANDOFF-ARCHIVE-20261010.md) is historical lookup only. Keep chronology in findings and raw evidence immutable.
