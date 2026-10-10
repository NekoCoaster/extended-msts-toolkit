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
