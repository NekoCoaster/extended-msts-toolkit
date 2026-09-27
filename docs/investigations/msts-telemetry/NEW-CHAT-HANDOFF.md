# Resume MSTS telemetry discovery in a new chat

Prepared2026-09-28 after completing player/loose-stock coupling and separation. The major goal is INCOMPLETE. User requested wrap-up and a new-chat handoff; the old task goal is to be paused after publication. No capture remains running. No production NEMT changes were made.

## Starter prompt

Set a goal to resume the independent MSTS telemetry discovery research described in C:/dev/Codex/2026-09-10/msts-telemetry/NEW-CHAT-HANDOFF.md. Read that handoff first, inspect current Git and simulator state, and continue the comprehensive player and AI telemetry inventory. Keep research independent of NEMT implementation and do not rank, prioritize or decide which data to keep. You may manage MSTS autonomously through the computer-use skill and use the existing research branch/draft PR linked to issue7. Preserve game assets and saves. Use bounded, evidence-led experiments and document unknowns honestly.

## Objective and boundaries

Discover all realistically accessible telemetry during regular MSTS gameplay for player and AI: session/time, controls/instruments/systems, vehicles/consists/physics, AI services/lifecycle, track/signals/traffic, activities/stations/events, environment and other evidenced surfaces. For each candidate retain meaning, applicability, units/type, extraction/build assumptions, cadence/lifecycle, provenance/confidence and limitations. Distinguish direct reads, derived values, configuration and hypotheses. Discovery is intentionally broad; neither a large inventory nor successful structural checks proves completion. Do not redefine completion as reversing every byte.

Normal UI gameplay is authorized. Memory probes are external read-only QUERY_LIMITED_INFORMATION | VM_READ: no injection, process writes, native-function invocation or modification of working assets. Research/probes stay separate from production. No categorization/prioritization/keep-drop decisions yet. No token budget was requested. A new chat has its own goal; create its goal from the starter prompt rather than assuming the old task goal transferred.

## Where to work

- Canonical research and raw evidence: C:/dev/Codex/2026-09-10/msts-telemetry
- Publication worktree: C:/codex/worktrees/NEMT-telemetry-research
- Branch: research/issue-7-msts-telemetry
- Draft PR: https://github.com/NekoCoaster/extended-msts-toolkit/pull/9
- Issue: https://github.com/NekoCoaster/extended-msts-toolkit/issues/7
- Publication baseline before this checkpoint:78fadd1. Run git log -3 and git status in the worktree for the final handoff commit; do not infer HEAD from this baseline.
- Production repo C:/codex/repo/NEMT baseline5cd5896cfa22a3752328176d65b1db5608ee9471; untouched by this research.
- Prior environment/Unity research C:/codex/repo/msts-unity-kb; reuse targeted findings as needed, do not rescan wholesale.

Read only this handoff, DISCOVERY-COVERAGE.md and relevant Git changes first. EXTRACTION-HANDOFF.md gives the build/reader/raw-evidence recipe. inventory.json is the authoritative candidate catalogue; INVENTORY.md is its generated table. Finding documents and summaries are better entrypoints than bulk raw captures or the old conversation. Historical progress notes may have been superseded; use dated latest evidence.

## Current checkpoint

Inventory1039 candidates:438direct,26derived,68native cab channels,507configuration paths;59installed cab channels. These are inventory counts, not completeness evidence. Representative research already covers player diesel/steam/electric surfaces, AI physical/abstract lifecycle, body/shape/wheel transforms, route infrastructure, signal selection, sky/environment, audio/input, activity/evaluator/station structures and serialization/reload. Read coverage for applicability gaps.

Newest area is complete: five loose wagons gain player ownership on coupling and return to null owner on F9 separation. Player chain1to6to1,outside population39to34to39,stored physical count40. Object IDs/addresses persist in this run; body pointers alternate. Final capture2397samples/0read exceptions includes5incomplete rows,845full-read clock crossings,8unstable car and142unstable body subreads. Stable roots/counts do not guarantee a complete atomic snapshot. See COUPLING-LIFECYCLE-FINDINGS.md and coupling-transition-summary.json; reproduce with analyse_coupling_transition.py.

Recent earlier evidence:39loaded owner-null vehicles independently enumerated in six configured loose cuts;40valid yard track joins. Preferred grain activity signal46red0toClear7 while oncoming AI passes,then forward next-signal iterator46to21 and21toheads2/3. Eight player-car node crossings and AIservice3speed-cap gate activation observed;player speedpost cap transition remains open. Emergency acknowledgement/positive diesel current validated; current is not actual rail force. Save reload preserved23player IDs while changing addresses.

## Simulator and saves at handoff

C:/MSTS/train.exe,PID33612,imagebase0x400000,SHA256 2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843. Recheck PID/build; addresses below are session-local and become stale after restart/reload.

Marias Pass > Setting Out Westbound Pickup (USA2/ACTIVITIES/yard_one.act). Escape pause menu,external rear camera. Final read40371.26171875simulation seconds,paused1,speed0. GP38-2 alone beside the separated five-car cut:Idle,Forward,train brake released,independent brake25%. Playertrain63073680,lead63322752,IDs400000/200000. No need to repeat this coupling experiment just to resume discovery.

New UI-confirmed save C:/MSTS/saves/USA2/yard_one_28092026_012813.sav,154215bytes,SHA256 9e474fed0fd5313c658e4386e5b84a340c509875d3dfe2095fec5595d31dd3b9. Copied to captures/yard-final-save-01 with provenance and final read. Reload has NOT been tested.

Preserved grain saves in the same directory:

- evegrain_27092026_184329.sav,124886bytes,SHA256 6064ec5975dca19d0d392df318bd1b15c432381ab19ca5f3cdf4d1c5f17c6010; saved before switching to yard,restoration untested.
- evegrain_27092026_051532.sav,124746bytes,SHA256 787f435189dcd5b645c3f448070d5d94e42330f8bca5275555d8e75b1b915a9d; earlier restoration tested.

User's preferred fixture is Marias Pass > Grain Train Through the Night (evegrain.act), initially moving/prethrottled with oncoming AI and temporary red. Earlier misspelling in the original goal is obsolete. Loading a saved later state does not recreate the opening encounter; restart the activity only when an experiment requires that opening.

## Useful next experiments, without priority ranking

Unresolved coverage includes station boarding/departure/next-stop and activity outcomes; player speedpost cap changes; AI rephysicalization/reversal/station stops and force/brake applicability; midnight/reset/calendar/load-completion; extended cab-context reachability; force/torque/wheel sign and axes; AI audibility/peripherals; unnamed serialized subobjects/full save fidelity; inventory-wide semantic consistency and objective completion audit. Select one stated uncertainty with a discriminating fixture after reviewing coverage. This list is continuation guidance, not a keep/drop or priority decision.

## Tools, validation and publication

Use the installed computer-use skill for native Windows UI via node_repl and @oai/sky. Read its SKILL.md and required docs in the new chat. Reobserve/reselect the window before input; no shell UI or direct Win32 input workaround. Prior activation failures recovered through fresh selection; they are not a current blocker. F9 Train Operations,double-click verified coupler to detach. G/Shift+G turnout direction depends on engine orientation. Independent brake brackets change1.25% per step; do not assume an old UI state. Use short bounded driving intervals and observations.

Readers validate this executable; retain exact copied probe sources and metadata with captures. Do not import read_loose_track_context.py: it parses arguments at top level. capture_coupling_transition.py uses reader classes instead. Its first preliminary capture predates origin fields; use each capture's own copied version. Avoid interpreting sampled clock as an exact event timestamp or caching physics body pointers.

Canonical checks: python analyse_coupling_transition.py; python build_inventory.py; python audit_inventory.py. The last is structure/evidence-path/source-hash validation, not semantic proof. Raw evidence stays local and is hash-manifested in the PR, not committed wholesale. Do not edit previously manifested raw files.

Publish only after captures finish: python C:/dev/Codex/work/sync-telemetry-checkpoint.py verifies old raw hashes,copies root reports/probes,and updates local-evidence-manifest.json. Then in publication worktree run python tools/source-checksums.py --write and python tools/prepare-commit.py --check; inspect diff and run git diff --cached --check before commit/push. Follow repo AGENTS.md. Native execution was previously blocked by DeviceGuard4551; do not bypass or misreport that limitation. No native code changed in this checkpoint. See CHECKPOINT-VALIDATION.md for actual check results. Keep the PR draft until broader research and review are complete.
