# MSTS telemetry research handoff

Updated 13 October 2026. Research is incomplete. This organization checkpoint adds no live experiment; recheck simulator state before any future observation.

## Current checkpoint

Parent research checkpoint: `10298c6`; this loading-duration checkpoint continues branch `research/issue-7-msts-telemetry`, draft [PR 9](https://github.com/NekoCoaster/extended-msts-toolkit/pull/9).

Canonical workspace: `C:/dev/Codex/2026-09-10/msts-telemetry`. Publication worktree: `C:/codex/worktrees/NEMT-telemetry-research`, under `docs/investigations/msts-telemetry`. This checkpoint includes loading-duration, override and manual-geometry findings.

Current local inventory: **1,064 candidates** (459 direct, 26 derived, 68 cab, 511 configuration). Structural audit passes: 1,007 evidence paths and 151 source hashes. These checks do not establish semantic correctness or completion.

## Start here

1. Use [research navigation](RESEARCH-NAVIGATION.md), then the relevant [coverage row](DISCOVERY-COVERAGE.md).
2. Query `python research_index.py 005a3941 --limit 8` or a topic such as `STATION`. Read the referenced finding before exporting again.
3. Check Git state and existing evidence. Validate process/build only when new live work requires it.
4. State a discriminating question; batch related analysis and publish coherent checkpoints.

## Latest evidence and next decision

[Station timing](STATION-TIME-FINDINGS.md) contains the latest opening capture, loading-duration reconstruction and activity override analysis. The opening capture recorded a positive automatic-player countdown and station selection advance while recorded times stayed zero. Its archived service-stability check is invalid; corrected source and a separate pointer check preserve that limitation.

The local duration model counts seven eligible cars and reproduces the first timer value using later inputs and an assumed quarter-second update. This corroborates the formula without proving simultaneous onset inputs. Override lookup prefers the selected endpoint, then its pair, then the route count; the current empty override list provides no positive runtime validation. Manual boarding has a separate path.

Manual duration is now traced to physical-vehicle endpoint membership and strict position bounds, distinct from automatic length-budget counting. Current bytes and constants match; contemporaneous onset counting remains unvalidated. Next station question: capture the manual contributing count at timer onset, trace minimum-wait use, or obtain an appropriate positive override fixture. Broader gaps remain in the coverage matrix; this is not the whole research objective.

Latest read-only state check (13 October, 05:58 UTC) found PID10036, pause0, automatic gate1 and an advancing clock. No UI action or continuous sampler was started. Earlier Escape attempts were ineffective; do not repeat them without a new method.

## Boundaries and history

Supported image SHA256: `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`. User installation context: MSTSBin, no NEMT loaded, no community night-cab addons. Rediscover process IDs and pointers; historical patches are not current behavior.

Preserve game assets/saves. External reads only; no injection, process writes, debugger/native calls, production integration or candidate ranking. See [extraction handoff](EXTRACTION-HANDOFF.md) for validity requirements.

The [prior handoff archive](NEW-CHAT-HANDOFF-ARCHIVE-20261010.md) is historical lookup only. Keep chronology in findings and raw evidence immutable.
