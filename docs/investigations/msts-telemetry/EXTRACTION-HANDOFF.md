Latest2026-10-10: STOP-ACTIVATION-FINDINGS.md validates stop-required event32 and activation decrements without latch/reset changes. EARLY-DEPARTURE-FINDINGS.md validates interruption of active loading,flags0x1a and next-stop advance. PID12888 paused65562.3984375,speed0,throttle0,emergency brake. Earlier simulator states below are historical. Goal active/incomplete.

Latest event checkpoint2026-10-10: EVENT-TRANSITION-FINDINGS.md validates location event13 radius entry,latch and matching message;exit retains non-reversible latch. PID12888 paused65311.3984375,speed0,throttle0,emergency brake. Earlier current-state notes below are historical. Goal remains active and incomplete.

Latest 2026-10-10: AI-STATION-RESET-FINDINGS.md captures AI9 physical removal, path-end flag, then update-gate disable/progress reset/station reselection. Retained positive speed is stale after deactivation. 1764samples,0errors;909native instructions match disk/live. PID12888 now paused at65242.0234375,player speed0,throttle0,emergency brake. Earlier simulator states below are historical. Research remains incomplete.

> New-chat continuation: see [NEW-CHAT-HANDOFF.md](NEW-CHAT-HANDOFF.md). Coupling/separation checkpoint is complete; the major goal remains incomplete.

# Extraction and evidence handoff

2026-10-10 update: current inventory is1,043 candidates; current coverage is DISCOVERY-COVERAGE.md. The counts and fixture descriptions in historical sections below are checkpoint-specific. STATION-DEPARTURE-FINDINGS.md and STATION-BOARDING-FINDINGS.md validate representative player arrival-on-loading,countdown,pause,expiry,departure/next-stop advancement and populated AI records. COUPLING-LIFECYCLE-FINDINGS.md validates player coupling/separation. Timed AI stops,full station lifecycle,clock and semantic-audit gaps remain open.

This is a working handoff for the independent research phase associated with issue 7. Discovery remains incomplete. It specifies how to use the existing evidence and probes; it does not authorize or implement production NEMT integration, prescribe export frequency, or select telemetry to retain.

## Catalogue and evidence

Start with `inventory.json`: each `data_points` entry has an ID, meaning, applicability, type, units, extraction description, evidence, evidence status, lifecycle and limitations. The 1,037 entries are candidate records, not 1,037 independent verified live quantities. Cab channels and native fields may describe overlapping quantities; configuration paths may contain several values. Unknown units, raw flags, unavailable branches and engine-specific limits remain explicit.

Read the referenced findings before implementing a field. `DISCOVERY-COVERAGE.md` contains the initial requirements review followed by later evidence updates; its initial 920-entry table is historical. `CHECKPOINT-VALIDATION.md` in the published checkout records validation at each checkpoint. Passing structural checks establishes neither field semantics nor complete discovery.

The canonical evidence root on this machine is `C:\dev\Codex\2026-09-10\msts-telemetry`. The research checkout is `C:\codex\worktrees\NEMT-telemetry-research`, branch `research/issue-7-msts-telemetry`; publication is under `docs/investigations/msts-telemetry`. Raw captures, retained probe versions and native exports are omitted from Git. `local-evidence-manifest.json` identifies their relative paths, byte lengths and SHA256 hashes. Its `local_workspace` string is provenance, not a directory that the verifier creates or assumes exists on another machine.

For a local checkout, verify the retained evidence with Python 3.9 or newer:

```powershell
python C:\codex\worktrees\NEMT-telemetry-research\docs\investigations\msts-telemetry\verify_evidence_manifest.py --root C:\dev\Codex\2026-09-10\msts-telemetry
```

On another machine, obtain an authorized copy of the retained evidence preserving the manifest's relative layout, then pass that directory with `--root` and the checkpoint's manifest with `--manifest`. A Git clone alone cannot recreate the historical raw observations. Missing files produce a failed verification, not fabricated replacements. The tool streams hashes, rejects duplicate/escaping paths, and returns exit 0 for complete agreement, 1 for missing/unreadable/mismatching evidence, or 2 for invalid input. Extra unlisted files do not affect verification. It reads files only and does not launch or attach to MSTS.

Use the probe copies inside each capture to inspect the acquisition logic that actually ran. The latest root-level probe may have changed since that capture. Reproduce summaries with the analyzer named in the relevant report against the retained capture; several analyzers assume the canonical directory layout. `audit_inventory.py` must run in the canonical workspace because it also checks local evidence references and installed source-asset paths. The published inventory omits embedded decompiler excerpts, so its hash intentionally differs from the canonical audit hash.

## Supported build and access

The base `Reader` in `read_live.py` opens only `PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ` (0x1010). It queries the process image path, hashes that disk file, accepts SHA256 `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`, and checks for MZ at image base 0x400000. It reads little-endian 32-bit pointers using fixed addresses. This is a researched build-specific layout, not an MSTS API or a portable ABI. Rediscover the PID after launch and reload; do not reuse the historical PID in instructions for another session.

The disk hash and MZ guard do **not** validate every live instruction, image relocation, installed hook, object type or producer. This installation has documented live patches. Targeted disk/live byte comparisons and exceptions are retained in native-pass reports; no blanket pristine-live-image claim is justified. An unsupported executable needs a separately validated layout, not removal of the hash guard.

The probes neither inject code, call native game functions, suspend the process, nor write game memory. Normal game UI testing changes gameplay, and the retained research save was intentionally created through MSTS. Original asset preservation is checked separately by the 126-file source manifest; it is not guaranteed merely by read-only process access.

## What a valid observation means

| Condition | Existing check or evidence | Interpretation limit |
|---|---|---|
| Readable bytes | `Reader.read` validates address range and exact byte count | Success is not proof of object type, current ownership or initialized semantics. |
| Registry and consist | Bounded traversals, cycle detection, car owner and body owner checks; selected reciprocal-link checks | Bounds are research limits. Errors must not become an empty train list. Not every probe checks all links or rereads every root. |
| Lifetime | Selected body/train pointer rereads and service backlinks | Numeric pointers and object IDs are not globally persistent identities. Reload changed all 23 player vehicle addresses. No reliable external load-complete gate is established. |
| Read interval | Before/after clocks and monotonic timestamps on supported captures | Same clock and stable pointers are necessary evidence for some comparisons, not atomicity. Nested reads may span producer phases. |
| Global position | Stable origin reread plus body identity; float64 X/Z translation by 2048 metres per tile | Two runs repeat one X-origin boundary across player/AI cars. Other boundaries, all frames and geographic conversion are not validated. |
| Physical versus track position | Separate body and track records, with derailment flags | All 45 track-section pointer checks passed after collision while body/track separation reached 69 metres. Valid track linkage is not physical on-track position. |
| AI state | Service registry plus physical-train associations and update state | Service existence is distinct from physical presence. Shared player-controller pointers do not provide independent AI controls. |
| Errors and nulls | Top-level errors plus nested registry/car/service errors and reread flags | An outer error count of zero can contain failed subreads. The save/reload run had 96 registry errors among 239 samples despite zero outer exceptions. |

Keep unavailable, absent, stale and numerical zero distinct. The evidence does not define a universal freshness bit. A bounded chain with a non-null successor is partial, not a complete count. Retain raw values and their applicability limits rather than inferring an event or physical action from a flag name.

Do not differentiate positions using a single assumed clock. `INTEGRATOR-TIME-FINDINGS.md` shows player motion agreeing more closely with the physics accumulator while AI absolute motion agrees more closely with gameplay time in the tested installation. Zero/nonpositive deltas, resets, identity changes and cross-origin samples require explicit handling before derived rates are meaningful. Paused gameplay does not freeze every rendering, audio or input surface. Wall-clock capture duration is not simulated elapsed time.

## Repeating gameplay observations

Load Marias Pass > **Grain Train Through the Night** (`evegrain.act`) through normal UI. Choose a fresh capture name; existing evidence directories must not be overwritten. A bounded paired example is:

```powershell
python C:\dev\Codex\2026-09-10\msts-telemetry\capture_infrastructure_transitions.py --pid <current-PID> --name <new-name> --seconds 30 --interval 0.5 --paired
```

This captures infrastructure, player cab/monitor and physical tracks sequentially, not at one instant. Metadata retains seven source files and their hashes. Read duration measurements are not isolated gameplay-overhead benchmarks. The nominal interval is a scheduling request, not a verified constant cadence or a recommended export rate.

Observe the UI while driving and pause for analysis. The unchanged N3 and N2 approaches reached red before the AI cleared, so they are failed successful-passage tests. Acknowledging the red-light alert resumed simulation in the tested installation and led to a collision; it is not an exit command. Prior clean AI passing and aspect-transition evidence remain valid within their separate scopes. Do not label a repeated stopped signal, a physical section change or a positive remaining monitor distance as successful player signal/node passage.

## Remaining handoff boundaries

The catalogue covers broad player/AI runtime, configuration and ancillary surfaces, but further discovery and semantic validation remain in the requirements review. Loaded loose-stock enumeration, player car node changes and next-signal selection transitions now have positive runtime evidence. Open work includes coupling/detachment transitions, remote loose-stock coverage, remaining adhesion/resistance and wheel/axle sources, unsupported cab-branch reachability, populated station operations, player speedpost changes and exact passage timing, repeated AI rephysicalization, additional lifecycle/clock boundaries, AI audio applicability, and complete save fidelity. Raw byte blocks or untraced names do not close those gaps.

The preserved data and scripts are research tools with per-probe guards, not a production-ready telemetry collector. Production design, export format, polling policy, compatibility support and keep/drop decisions remain outside this phase. Completion must still be audited against the full original objective.


## Populated player and AI wheel observations

The user loaded the activity and authorized autonomous normal UI control. The earlier unavailable-manager/UI limitation is superseded. `wheel-runtime-summary.json`, reproduced by `analyse_wheel_runtime.py`, summarizes two sequences and two manager surveys. `capture_wheel_sequence.py` retains exact reader copies and per-sample clocks, pause state, errors and identity checks.

At clock73800.6796875 the paused baseline has23player vehicles. At73864.640625 it has45vehicles:23player and22AI. The five manager lists have counts0/6/1364/23/1 then0/6/1364/45/2; stored counts agree with traversal, roots and sampled backlinks/identities are stable. The first list remains empty; this does not identify static or detached vehicles.

Opening sequence:80samples,71paused, sampled clock73800.6796875..73807.15625. Player engine200223 rate ranges2.8584873676..3.363550663;200224 ranges2.8621480465..3.3453645706. Paired sequence:50samples,45paused, clock73864.640625..73868.234375. Player rates range1.6238725185..1.6284261942 and1.6234132051..1.6282598972; both AI engines200146/200147 range6.3843708038..6.973692894. These are short positive stored-rate transitions, not complete gameplay coverage.

Both sequences have zero outer/vehicle read errors and zero flagged vehicle/shape identity changes. Player adhesion cache remains668360.0625; AI cache is0. All four powered driver accumulators remain0. Shape current times vary only between0 and approximately2e-7; player processed time remains0 and AI processed time varies approximately1e-7..2e-7. Zero AI cache is not proof of zero physical adhesion, and these cab-view observations do not validate visible wheel movement, physical slip or general animation cadence.

Both samplers ended before the final UI pause: the opening run has an unsampled tail to73864.640625, and the paired run to73877.21875. Do not describe the entire moving interval as captured. Escape successfully opens the pause menu and sets paused1; the Pause key did not. Last verified game state is paused at73877.21875. No failure alert was present. Prior runs failed near73904, so the next test must control approach speed before letting the activity advance substantially.

Inventory remains1026 candidates. These observations strengthen existing rows without adding fields or making keep/drop decisions. Physical angle, external-view animation eligibility, resistance-force magnitude and AI force freshness remain open.


## External camera and loaded branch eligibility

`wheel-external-view-01` captures180samples,25unpaused, clock73877.21875..73894.7265625, all45vehicles with zero outer/vehicle errors or flagged vehicle/shape identity changes. Normal UI switched from cab to external camera2, then Escape paused. Unlike the two earlier runs, this sampler continues through the final paused interval. The camera transition was visually confirmed but not timestamped inside the memory stream; do not assign an exact sample to it or infer visible wheel rotation from the distant screenshots.

Both player processed shape times now have three distinct values between0 and approximately2e-7, whereas earlier cab-view processed values stayed0. All four driver accumulators still stay0 while engine rates change. This is an association with the external-view run, not isolated proof of camera causation.

`read_wheel_gates.py` and `wheel-gates-external-paused-02/gates.json` inspect the traced branch inputs. All four engines have car+80=1, excluding the0x800 capability bit tested at638695. Native definition kind is byte+88=1. Shared Default Wheelset is0.30000001192092896. Thus the traced powered phase branch is ineligible at this paused observation; a zero phase is not a general wheel-angle measurement. The local+4e8 raw value is unselected (definition90bit10 clear), so its very large finite value must not be interpreted as a meaningful loaded multiplier. The reported selected multiplier is what the later selection would choose if execution reached it, not proof it was consumed. Frame delta is a paused stored value, not elapsed pause time.

The retained first diagnostic capture gates-01 read definition kind as a dword instead of the native byte and is superseded for that field. Assembly63830f establishes byte width; corrected gates-02 reads1 on all four engines. Original raw evidence and exact erroneous probe copy are preserved. No new inventory candidates;1026total. Eligibility transitions, other ordinary-wheel animation paths and visible physical angle remain open.

Last verified simulator state: external camera, Escape pause menu, paused1 at73894.7265625. No failure alert. The train is very close in simulation time to earlier failed approaches; apply verified braking controls immediately on any next resume, or restart the fixture before a longer run. Research goal remains active and incomplete.

## 2026-10-10: process-specific hook context

Current PID12888 user-confirmed noNEMT context differs from the historical hook captures. `captures/current-hook-context-20261010-01/ranges.json` reads16bytes each at loading-callsite494bc1 and wheelentry5d5381;both match supported executable disk bytes. This is32bytes of targeted evidence,not complete function verification or a blanket unmodified-process claim. Fourteen inventory entries now explicitly scope their prior loading/wheel-hook wording to historical captures and retain those original findings. Historical motion behavior is not retroactively attributed to this current process. Other hook sites,including405694,were not checked in this pass.

## 2026-10-10: animation and superseded-limit metadata review

Current16bytes at405694 match disk/live;`captures/animation-hook-context-20261010-01/range.json` preserves exact bytes and process/build context. The two animation timestamp candidates now distinguish historical redirection from this bounded current check. Loader metadata no longer states globally that no round trip was observed:the static loader pass alone does not prove one,while SAVE-RELOAD-RUNTIME records the actual bounded23vehicle fixture. Earlier moving-capture failure to cross a signal is now scoped to that run,without claiming its geometry represents the later successful transition.

`context-metadata-review-20261010.json` records39changed candidates and1020unchanged relative to the immediately preceding local inventory. Only limitations/evidence changed;IDs,meanings,types,units,extraction and all prior evidence links preserved. This is a scoped context consistency review,not the full inventory semantic audit. Latest inventory audit1059unique,944evidence paths,151source hashes passes.

## 2026-10-10: category and cab-evidence wording review

`inventory-category-review-20261010.json` confirms511configuration rows are explicitly SIMIS source tokens with source-written units;480remain source-only and31also cite separately mapped/read Acela values. These are not511independent live values. All68base cab channels have three engine dispatch outcomes:113static branches,78defaults with no update established,12not-routed and1invalid destination. Static branch identification is not UI/runtime support.26derived rows remain separately typed. This structural/category review does not establish semantic completeness.

Six diesel cab entries no longer share the inaccurate blanket pressure wording. Four pressure channels retain their bounded paused-display evidence;AMMETER cites actual N1cab225amps versus stored225.0000152588 after emergency acknowledgement,qualified against downstream force cutoffs;LOAD_METER retains shared-producer evidence without invented independent display agreement. Source declarations,unsupported branches and historical evidence remain intact.

## 2026-10-10: derived-value prerequisites review

Five early derived candidates now use scoped `derived-metadata-review.json` overrides:car.mass,train.total_mass,train.car_count,car.acceleration andtrain.lifecycle_events. Reciprocal masses require finite positive inputs and validated ownership;partial traversal cannot be a full count/total. Body-derived mass is distinct from native definition aggregate. Acceleration remains a hypothesis requiring a justified producer clock,not a universal gameplay denominator;historical player/AI integrator evidence is not current noNEMT timing proof. Lifecycle changes require complete observations and session-aware identity;read failure is not despawn. Representative coupling,AIreset and reload evidence is linked. Existing evidence remains retained. The other21derived candidates are not declared fully reviewed by this pass.

## 2026-10-10: coordinate-dependent derived candidates

Extended derived-metadata-review.json to11total reviewed candidates. Stored longitudinal projection requires finite vectors and a validated basis;3D speed magnitude is not signed train/track speed. Euler orientation remains an explicitly convention-dependent hypothesis. Pairwise relative motion requires matched reference points,origin/frame,time and defined train ordering;zero separation has no radial direction. Wheel angular-speed estimate is ideal no-slip kinematics,not animation phase or adhesion. The day-clock-minus-start extraction now explicitly states its observed midnight failure rather than requesting a test already completed. No new runtime quantities or validation claims were added. Existing raw evidence retained;15otherderived entries still require scoped review.

## 2026-10-10: track/topology derived review

Five track/topology derived rows reviewed against TRACK-GEOMETRY,TRACK-TOPOLOGY,INFRASTRUCTURE and MOVING-PLAYER-ORIGIN findings. Radius-derived nominal curvature and straight-grade hypotheses keep their existing direction/geometry limits. Route IDs remain build-specific registry joins. Updated stale route-position status to recognize two45identity observations of the same origin boundary;this is not different-boundary coverage. Selected-connection status recognizes the full732-node registry and resolved ambiguity while keeping traversal selection distinct from occupancy/authority/blade motion. Sixteen of26derived candidates now have explicit scoped review;ten remain. Inventory audit passes947evidence paths/151hashes;no new runtime experiment this pass.

## 2026-10-10: derived prerequisite review complete

All26derived candidates now have scoped entries in derived-metadata-review.json,with exact-ID coverage recorded in derived-review-20261010-summary.json. Final ten preserve established formulas and add decision boundaries:geometric predicates versus evaluator execution;conditional display versus physical electrical availability;solver endpoints/gap/projected rates versus physical slack/force/trajectory;distance gates versus full AI spawning decision;queue records versus voices/duration/audibility. This completes this metadata review only. It does not validate all runtime transitions,nonfinite/x87 behavior,coordinate conventions,AI reappearance or audible output,and does not complete the broad research goal. Inventory audit1059/947paths/151sourcehashes passes. Original evidence retained.
