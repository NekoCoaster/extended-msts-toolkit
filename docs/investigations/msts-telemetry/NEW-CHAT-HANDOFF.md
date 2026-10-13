# MSTS telemetry research handoff

Updated 13 October 2026. Research goal is **active and incomplete**, resumed after the organization checkpoint2fcae46. Use the bounded function-index workflow; historical pause instructions below are superseded by this resumption.

## Current checkpoint

Last experimental checkpoint: `9cc85ba`, branch `research/issue-7-msts-telemetry`, draft [PR 9](https://github.com/NekoCoaster/extended-msts-toolkit/pull/9). Canonical workspace: `C:/dev/Codex/2026-09-10/msts-telemetry`. Publication worktree: `C:/codex/worktrees/NEMT-telemetry-research`, under `docs/investigations/msts-telemetry`. Production NEMT is separate.

Inventory: 1,063 candidates (458 direct, 26 derived, 68 cab, 511 configuration). Counts overlap in meaning and do not establish completion. Latest experimental audit: 995 evidence paths and 151 source hashes passed.

On13October the current process was10036 at route selection. Normal UI loaded Tokyo-Hakone Introductory Train Ride for an opening-station capture;see STATION-TIME-FINDINGS final section for the resulting checkpoint. Rediscover process,UI and addresses on continuation.

Installation context: supported image SHA256 `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`; user confirms MSTSBin, no NEMT loaded and no community night-cab addons. Historical patched process observations are not current executable behavior.

## Start here

1. Read [research navigation](RESEARCH-NAVIGATION.md), then the relevant row of [coverage](DISCOVERY-COVERAGE.md).
2. Query `python research_index.py 005a3941` or a finding topic such as `STATION`. Read the referenced finding section before exporting again.
3. Check current Git state and existing evidence. Revalidate executable/process state only when needed for new live work.
4. State a discriminating question. Batch related writer/caller analysis; run gameplay only where static evidence leaves an operational ambiguity.
5. Update the relevant finding and this short handoff at a meaningful checkpoint. Keep raw captures immutable. Put chronology in findings, not repeated current-state paragraphs here.

## Recent conclusions and next unresolved question

[Station timing](STATION-TIME-FINDINGS.md) distinguishes traffic schedule merge, temporary list markers, recorded times and automatic player driving. `005a3941` marks the previous station on its automatic-driver countdown path; `005a41c2` differs. Completion-modal state retained speed, selection and enabled driver gate. The fresh opening capture on13October recorded platform66flags0to2 with positive countdown and selection advance,while recorded times stayed0. The archived probe has an invalid service_stable check due to variable shadowing;fixed in current source,raw preserved. See latest STATION-TIME-FINDINGS section.

Opening capture automatic-opening-20261013-01 finished872samples/0errors. Simulator remained in the running introductory ride after two Escape attempts (second after explicit activation);do not assume exit succeeded. No capture remains running. Next consolidate guarded transition evidence and validate corrected service-pointer check;avoid repeating ineffective Escape input without a new method. This is one open question, not the entire objective. Broader gaps and completion requirements remain in the coverage review.

## Boundaries and evidence

Preserve game assets/saves. External reads only (QUERY_LIMITED_INFORMATION | VM_READ); no injection, process writes, debugger/native calls or production integration. Research is resumed;normal UI experiments remain authorized. Do not rank candidates or make keep/drop decisions. See [extraction handoff](EXTRACTION-HANDOFF.md) for build assumptions and read validity. Raw exports/captures remain canonical-local; published manifest retains their hashes.

The [verbatim prior handoff](NEW-CHAT-HANDOFF-ARCHIVE-20261010.md) is historical lookup only. Its many former current-state claims must not override this page.
