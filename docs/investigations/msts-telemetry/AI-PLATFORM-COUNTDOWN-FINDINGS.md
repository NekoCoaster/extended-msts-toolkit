# AI platform countdown, braking and resumption

2026-10-10,Tokyo-Hakone > Shinjuku to Machida in the Winter,PID12888,supported MSTS Bin SHA256 `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`. Player remained stationary;AI services ran through ordinary gameplay. No assets/saves/settings or production sources changed.

## Fixture choice and correction of the initial hypothesis

The original question sought explicit AI arrival/departure intervals. `scan_ai_timetable_fixtures.py` finds3369adjacent numeric pairs in77installed TRAFFIC/*.trf files,matching3369ArrivalTime tokens;all pairs are equal. An initial unsigned-number scan missed8negative equal-time pairs;the retained signed scan corrects that limitation. This is a hashed lexical fixture survey,not proof of full grammar or runtime use.

Native005a41c2 instead exposes an AI platform-loading countdown+210/gate+214,distinct from the path-wait states+1e4/+1e8 and elapsed/duration+1ec/+1f0. The winter activity gives five AI services with repeated platform stops. ID72 starts with the player at61200 and its first configured stop platform255 is approximately1110.39m down its path. This permits observing an entire new platform-hold cycle rather than only a timer already running at initialization.

`captures/winter-ai-fixture-20261010-01` preserves the ACT,TRF,two service definitions and two paths with source hashes. The baseline service reader joins IDs1/2 to ShinHakWinter (Traffic) at60120/60600 and IDs70/71/72 to ShinHakWinter (Traffic01) at59400/60300/61200. TRF schedules for1/2 repeat60120/60600;the Traffic01 entries explicitly use0times. These loaded differences are not evidence that one group lacks a platform hold.

## Capture and representative transition

`read_ai_station_series.py` extends the existing station/service reader with+210,+1ec,+1f0 floats and another selected-pointer reread. Access remains QUERY_LIMITED_INFORMATION | VM_READ. Exact sources and metadata accompany the1132sample capture at nominal0.2s intervals,ended cooperatively after the observed cycle and UI pause.0outer/inner service errors,49whole-read clock crossings,0flagged selection/sentinel/node instabilities. Stable checks do not guarantee atomicity.

`analyse_ai_platform_countdown.py` generates `ai-platform-countdown-20261010-summary.json`. ID72 remains abstract (physical flag0) through the sampled stop:

| Observation | Previous / first changed simulation sample | State |
|---|---|---|
| Countdown begins |61294.7734375 /61295.0234375|Gate0->1,remaining59,speed5.549277305603027m/s;selected changes255->247,previous becomes255|
| Braking reaches zero |61300.7734375 /61301.0234375|Speed0,remaining53,gate1;progress then holds through the stop|
| Countdown releases |61354.6484375 /61354.8984375|Gate1->0,remaining0,speed still0|
| Movement resumes |61355.6484375 /61355.8984375|Speed0.9599999785423279m/s;progress resumes while selected remains247|

First positive59is a sample,not a proven initialization duration. Timer starts before speed0,so it is not an exact stationary-arrival or physical door-open timestamp. While holding at255,the selected pointer already identifies247;previous identifies the stop being serviced in this observed transition. Do not associate the hold with selected alone.

IDs2,70,71 also show gate initiation,braking,zero-speed hold,expiry and resumption,with first positive values49,39,29,44 or32.33333206176758 in different cycles. ID1 has a physical train attached while its already-active countdown expires and movement resumes;later it loses its physical instance and reselects the first record. This does not establish rephysicalization or a new timed stop at that later reset.

All falling adjacent active-countdown observations decrease by1second in this fixture. Other sample pairs repeat the same value. This supports the observed scheduler granularity,not a universal update-rate guarantee. IDs1/2/70 each have93paused active pairs with unchanged remaining values. Across all services29samples have gate1 and remaining0;zero remaining alone is not release. ID72 has289active samples,260at zero speed,and4with active gate/zero remaining. The separate path-wait dwell state+1e8 stays0 throughout;these platform holds do not validate it.

## Station records and native branch

All sampled station schedule/recorded-time/flag fields remain unchanged for all five AI services. IDs1/2 retain their repeated configured schedule values and flags1;Traffic01 records retain schedule0/flags0. Recorded arrival/departure values remain0. Therefore player arrival-on-loading/departure writer semantics cannot be transferred to these AI platform holds. Positive timetable fields and positive runtime countdown are separate surfaces.

Assembly005a41c2 tests whether the distance selector changes a nonnull selected record. It derives a loading duration from platform/eligible-consist inputs (or20second fallback),sets gate1,copies selected to previous,installs the new selection,and recalculates effective efficiency. It subtracts the update interval from+210 and forces the target toward0 while the resulting value is nonnegative. Only the negative-sign branch clears countdown and gate;this explains observed active-zero samples. The full loading-duration formula and invalid/nonfinite inputs remain unvalidated.

The distinct braking-to-wait branch+1e4 waits for speed0,sets+1e8 and clears elapsed+1ec;the dwell branch advances+1ec until it exceeds+1f0. Do not conflate that mechanism with+210/+214. Helper005a8a9c can advance active countdowns during service scheduling/initialization,so positive timers in the initial snapshot do not establish their gameplay start time.

`captures/ai-platform-countdown-native-20261010-01` preserves historical exports with fresh disk/live byte checks:2functions,809instructions/3704bytes,0mismatches/errors. Only exported ranges checked;this is not a native execution trace. No remote native call or memory write was made.

## Remaining boundary

The observed AI hold is supported by service speed,progress,target,countdown and selection together;distant AI vehicles were not visually identified. Physical wheel/brake/door state,AI timetable adherence,other loading-duration inputs,path-wait/reversal/rephysicalization and midnight remain open. Existing catalogue meanings remain separately qualified.

Final UI is the pause menu at61414.5234375,player speed0,throttle0,Neutral;F5 displayed train brake0%. A BackSpace attempt did not establish a changed brake state and is not claimed as a successful intervention. No capture remains running. Earlier finalized-report UI table became visible on fresh observation before fixture change,showing five station rows consistent with the stored report;no report file was edited retroactively. Overall discovery remains active and incomplete.

## Distinct path-wait writer follow-up, 2026-10-10

A bounded displacement-write scan finds two positive braking-to-wait writers in005af21f,at005af7dd and005af88d. Both are in the operational iterator type5 branch,with direction-dependent progress comparisons. On entry they set service+1e4 to1 and convert the uint32 at the associated iterator payload+8 to float service+1f0. They also advance accumulated progress and copy the iterator state before returning. This identifies the duration source inside the operational path traversal;it does not yet identify a PAT-file flag or an installed active wait fixture.

Fresh PID12888 comparison of005af21f covers460instructions/2041bytes with no disk/live mismatches or read errors. captures/path-wait-native-20261010-01 preserves the function and source hashes;the sibling verification report records the comparison. path-wait-writers-20261010/wait-offset-writes.tsv records50displacement matches,which include unrelated object types and are navigation evidence,not50service writers. The initial scanner-wrapper call failed parameter binding before launch because it inherited an unused Addresses parameter;the new wrapper removes that parameter. No duplicate native analysis was started over a running export.

Next dependency: trace iterator005bbda9 type5 creation and payload+8 back to the loaded path parser before selecting a fixture. Platform+210/+214 evidence does not close this separate path-wait gap.

Iterator005bbda9 delegates to005bbe66 unless the parent flags include0x10. In the delegated iterator state1 branch, a loaded path-node uint16 at+6 with bit0x2, together with node+10 matching the current track-node pointer, selects iterator type5. It copies the node+1c position to iterator+18/+1c, retains the event node at iterator+24 and advances the path-node cursor via node+14. The preceding bit0x1 branch has precedence and creates type2;the path-end type check also precedes these flags. This is loaded-node interpretation,not a direct assertion about the first PAT-file integer. Wrapper handling of node bit0x4 may perform additional iterator steps.

The wrapper and iterator are verified in captures/path-wait-iterator-native-20261010-01:629instructions/1927bytes,zero disk/live mismatches and zero read errors. Source copies and hashes are retained. The path-file parser link remains open;no installed fixture has yet been selected from inferred raw flags.

## PAT node parser link, 2026-10-10

The actual file keyword is TrPathNode (not PatPathNode). Installed UTF16 label75cb70 pairs with token4041d at796b70. Token-byte navigation finds writer005bcdbb and loader005bde77. The loader's TrPathNodes branch allocates and zeroes count*0x24bytes. In the TrPathNode branch it reads the first scalar through stream slot10,then two successor indexes through slot8. At005be249 it stores the first scalar as a dword at loaded node+6. This overlaps the uint16 flags at+6 and the lower half of duration storage+8;the upper half of that storage begins zero from allocation. Thus first-scalar bit2 reaches the inspected wait flag,while its upper16bits supply the initial duration low16bits. Later conversion005be457 and path fixup005bd799 still require review before treating this as the complete final loaded mapping.

path-node-parser-20261010 retains both functions;730instructions/2245bytes match current PID12888 and disk with zero read errors. Assembly is needed because the loader decompilation omits the detailed node branch. Exact flag/token observations are navigation and parser evidence;no live wait transition is asserted.

## Provisional installed wait-node fixtures

005be457 reads the fourth node token as a reference-list index and writes node+0. 005bd799 copies resolved track/position values to node+10/+1c and may mark the first node flag8/path flag10 invalid;it invokes further validators. These two inspected functions match disk/live across177instructions/492bytes. Their direct code does not rewrite duration+8,but the downstream validators are not yet fully traced.

scan_path_wait_fixtures.py scanned211 installed PAT files with zero decoding errors and zero unmatched TrPathNode tokens. Four nodes have first-word bit2: JAPAN1 itr (traffic 01).pat node69;JAPAN2 isaburo rescue (traffic).pat node6;JAPAN2 shinpei.pat nodes17 and28. All have packed00000002,so the initial duration candidate is0;none also has preceding reversal bit1. The scan preserves file hashes and successor/PDP indexes in path-wait-fixture-scan-20261010.json. These are provisional loaded-node candidates,not proof of reachable waits or nonzero dwell. A zero-duration branch may clear within one update,requiring sampling expectations different from the platform countdown. Activity/service linkage and final loaded node values remain the next evidence needed.

## Route-scoped service/activity linkage

link_path_wait_fixtures.py ties candidate path names to PathID in services,then exact service references in same-route TRF/ACT text. Tokyo itr(traffic01).pat is used by both itr(traffic01).srv and itr(traffic).srv;each has seven references in itr(traffic).trf and seven in itr_e1_s1_w1_t1.act. Shinpei's path is used by the player service in shinpei.act. Isaburo Rescue's service is referenced only in its traffic file in this scan,with no direct matching ACT service declaration. That absence does not exclude compiled ASV or other indirect use. Cross-route names are not joined:the identically named JAPAN2 ITR service is not a match to JAPAN1's path.

path-wait-fixture-links-20261010.json preserves all matching source hashes and repeated references. This supplies an existing Tokyo activity candidate for a later AI path-wait test,but actual loaded-node values,reachability and zero-duration event visibility remain unvalidated. The active midnight run was not changed.

## Direct validator review

The four direct fixup callees are now exported in path-wait-validation-20261010.005bd3aa refreshes associated path-point track resolution and invalid flags;005bdc4d clears/recomputes loaded node flag8 and terminal-track information;005bd8f0 assigns node type at+4 from successor topology;005bd9ed validates adjacency and assigns junction pin bytes at+d,with invalidity at node flag8/path flag10. None of their inspected direct instructions writes loaded node duration+8 or changes wait flag2. This narrows the remaining concern to called helpers,other load paths and actual fixture state;it is not a whole-program no-writer proof. A loaded-node read remains required before a runtime wait claim.

Fresh PID12888 comparison of those four validators:561instructions/1762bytes,zero disk/live mismatches and zero read errors. See path-wait-validation-20261010-byte-verification.json.

## Loaded-path probe availability baseline

read_loaded_path_nodes.py follows observed service+1d4 to the iterator's path pointer, bounds the path-node count at4096 and retains raw36-byte records plus header/root/content rereads. The current Explore Route player path exposes48nodes with all implemented rereads equal;see captures/explore-loaded-path-20261010-01/path.json. This is reader availability evidence,not the candidate Tokyo AI wait fixture or proof of a wait transition.

## 2026-10-10: loaded Tokyo introductory path-wait fixture

Normal UI Home -> Introductory Train Ride -> Tokyo-Hakone -> Start loaded the installed ITR fixture. At day clock43208.82421875, `captures/tokyo-itr-paths-20261010-01/paths.json` records21services with zero path-read errors and unchanged registry addresses. All21path header/node/root rereads match. Fourteen AI service instances (IDs187-196,198,199,203,204) share path object55414508 and node base such that index69 is56360252. That node has flags2,type0,duration uint32 at+8 equal0,primary successor56360216 (index68),no secondary,track79795888,position200.6443328857422. This matches installed PAT index69 flags00000002 and zero packed duration.

Services named ITR (Traffic 01) and ITR (Traffic) share this path despite different consists. The shared path/node addresses are not distinct service identities; timers and iterator state remain per-service. None of the14snapshots has braking-wait1e4 or dwell1e8 set; three have platform gate214set instead. A loaded wait flag does not establish that the iterator reaches/executed it. Zero duration may be cleared within one update and missed by external sampling. `read_service_paths.py` preserves exact source copies/hashes and bounded loaded-node extraction; sequential rereads cannot prove atomicity or exclude pointer reuse. No game assets changed.

Completed ITR baseline `tokyo-itr-wait-baseline-20261010-summary.json`:483samples/0errors across43217.44921875..43277.44921875. No sampled braking-wait/dwell flags;1755service samples have platform gate214. No selection/sentinel/wait-selection reread changes. Player train speed0..11.460050582885742 under introductory automatic driving. This is a negative short-window wait observation,not proof of absent event execution. Full nodes/registry snapshot positively validates installed zero-duration wait data and shared path ownership.

Loaded primary successor chain for ITR Traffic01 is0->1->...->67->69->68;node68is terminal type2,while69is wait flag2/type0. Thus node69 is not simply disconnected extra data. A current read at43341.69921875 finds AI189cursor65,AI190/191cursor60,others earlier;AI187/188cursor1 after earlier progression remains ambiguous without transition evidence. `tokyo-itr-wait-reachability-20261010.json` preserves bounded cursor indices and current starts/speeds. Dedicated series uses AI189session identity/address and samples cursor,event,type andwaitflags every~20ms. First series progress field was incorrectly read from previous-record pointer+38;analysis-notes.json explicitly excludes it,raw remains unchanged,and root probe corrected to+1d0 for future captures. Other fields retain their documented offsets.

Dedicated AI189capture completed8737samples/0errors over180.012wall seconds,day43366.82421875..43546.82421875. No root/cursor instability,wait-braking,dwell or cursor/event/type transitions;cursor remains65 while speed changes20.04->1.92. This does not establish proximity by time-to-arrival or prove event unreachable. Next discriminate whether service+1d4 is a retained lookahead iterator versus movement position,using current+1d0 and native advancement conditions;do not repeat equivalent waiting without this check. `analyse_path_wait_series.py` reproducibly summarizes terminal captures and excludes invalid progress field.

## 2026-10-10: zero-duration wait boundary reached by AI189

`path-movement-context-20261010/005a7e9c.asm` selects service inline endpoint+4c for nonnegative speed bits and+b4 for negative.25instructions/74bytes match disk/live. The already-verified005af21f copies retained service+1d4 iterator to a local48byte iterator and advances that local to inspect eventtype5. Direction-specific endpoint position crossing sets1e4 and converts node uint32+8 tofloat1f0,then advances/copies the iterator. Stored iterator therefore need not expose eventtype5. Node index alone is not distance-to-event; movement endpoint/segment boundaries provide context.

Corrected capture `captures/tokyo-itr-path-wait-20261010-02` completes4290samples/0errors in88.535wall seconds,with no flagged root/cursor instability. It was cooperatively stopped after wait boundary and path-end reset were captured. Sequence66->67->69->68->1. At43668.07421875:cursor69,speed0.3453092575,endpointposition200.5723419. At43668.19921875:cursor68,speed0,endpointposition200.6443329 exactly equals the installed loaded wait-node position;1ecchanges0->1 while duration1f0remains0. Neither1e4nor1e8is sampled nonzero at~20ms observation cadence. This supports wait processing at the zero-duration boundary,not direct observation of either gate becoming set. Brief set/clear within an update remains possible. Ordinary platform gate214is0 here.

By43675.07421875 speed4.7999997,endpoint212.6443176 shows movement after the stop. At43675.19921875 retained cursor resets68->1,type1->3,progress61319.60546875->0,while endpoint and speed remain unchanged. These stale movement fields after path-end reset must not be interpreted as current displacement along the reset path. Summary `tokyo-itr-path-wait-20261010-02-summary.json` preserves transitions and source sample hash. First capture's invalid progress is explicitly excluded;second uses verified+1d0. Positive-duration waits and direct dwell-gate transitions remain unvalidated.
