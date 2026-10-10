# Finalized evaluation report and station summaries

2026-10-10,supported MSTS Bin SHA256 `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`,PID12888. This adds a distinct finalized-report surface to the live activity/station inventory. Normal early exit from the restarted Tokyo tutorial was used;no game asset/save or production source changed.

## Confirmed extraction

Report base00809790 is distinct from activity00809810. `read_final_report.py` bounds circular-list traversal to1024nodes,retains string pointers without dereferencing them,and rereads list roots/node payload pointers. Exact probe copies accompany before/after captures. `analyse_final_report.py` compares the final report to a separately retained pre-exit player station snapshot.

Before exit,the gameplay station list has5records but report station count/list are0/empty. After normal Exit Activity,report count5 matches five26byte records at list+0x58. Each record copies all four scheduled/recorded times and flags exactly from the corresponding ordered source record. Allocated report addresses differ from live source addresses. Report record layout is name pointer+0,marker location float+4,scheduled arrival+8,recorded arrival+c,scheduled departure+10,recorded departure+14,flags uint16+18. Native finalizer00589a96 establishes this layout and resolves station label/location independently;the pointer names are not decoded by this reader.

The UI states failure to complete due to exiting after11seconds and four missed stations. Report duration10.8515625 agrees with that displayed example;report success0 and termination code0 do not identify an executed failure outcome. Activity stop/success and player pointer are0 after teardown. **This does not validate event outcome7.**

Five copied flags are0x22,0,0,0,0;first arrival64805 equals its scheduled time from the synthetic initialization path. Finalizer counts missed when bit0x4 is set OR bit0x2 is clear. This yields4,matching memory/UI. The four later stations had not yet been reached when the user exited,so this report is final evaluation coverage,not a live count of physically passed missed platforms. Late count0 and action list/count0 are readable,but positive late/action cases were not sampled with this reader.

## Native field semantics

Three historical exports copied into `captures/final-report-native-20261010-01` were freshly checked:554instructions/2038bytes match disk/live across005897f1,00589a96 and0059a0c0,0mismatches/errors. Only exported ranges were compared;this is not an execution trace or whole-function completeness proof.

| Report offset | Meaning and boundary |
|---|---|
|+4 uint32|Copied activity success+34c during finalization;retained report value distinct from subsequently cleared activity field;positive report value not captured here|
|+8 uint32|Report presence flags already seen by evaluation reader;raw1 here,not a full decoded flag vocabulary|
|+c uint32|Selected termination code from ordered activity+378 bit tests;not a copy of the whole bitmask;0 on observed manual exit|
|+10 float|Day clock80acd4 minus activity start+7c at finalization;not the independent elapsed accumulator and not measured wall duration|
|+48 uint32|Count of bit2 records where scheduled arrival plus configured tolerance is strictly less than recorded arrival|
|+4c uint32|Count where bit4 is set or bit2 is absent;4 on early exit|
|+50 float|Last eligible arrival deviation after tolerance adjustment;overwritten per bit2 record,not summed|
|+54 float|Last eligible departure deviation after tolerance adjustment;only overwritten within bit2 and bit8 branch,not summed|
|+58 pointer /+60 uint32|Final station-summary list/count;5copied records observed|
|+5c pointer /+64 uint32|Final action-summary list/count;types6..9 only in native0059a0c0;empty here|
|+68 uint32|Count of those action records whose source trigger latch is0;empty0 here|
|+6c uint32|Distance display unit selector;native route flag4 maps to1,otherwise0;existing display mapping1km/0mile;before finalization0,after1|

For finite ordinary inputs,the deviation adjustment has a signed dead band:positive difference subtracts tolerance and clamps a negative result to0;negative difference adds tolerance and clamps a nonnegative result to0. Tolerance is read through global007b8d3c+0xc0. The assembly tests sign bits;NaN,signed-zero,negative tolerance and unusual initialization cases are not modeled as proven behavior. New runtime values are0only. The previous successful-run UI overall lateness is not retroactively claimed as a read of these newly captured fields.

The termination selector tests activity bits in order2,400,800,1000,2000,4000,100,8000,200,20000(hex). The last branch transfers an additional pointer. Full reason names,payload/string ownership and nonzero cases remain open. Report duration has no midnight correction in the inspected finalizer;cross-midnight/save-resume interpretation is untested.

Action record size24:raw type+0,type-label pointer+4,source event+72 text pointer copy+8,event+76 copy+c,event+14 copy+10,trigger latch+14. Pointers in report are copied text allocations,not stable source identities. No positive action record was observed;keep raw types and avoid inferring work-order completion from an empty list without fixture context.

## Evidence and limits

`captures/final-report-before-exit-20261010-01/report.json`, `captures/final-report-pre-exit-stations-20261010-01/samples.jsonl` and `captures/final-report-after-exit-20261010-01/report.json` are the paired evidence. `final-report-20261010-summary.json` reproduces count/flag/time equality and missed4. Both report snapshots have equal start/end clock and stable roots;all five final node rereads match. This is sequential consistency checking,not atomicity or a guarantee against pointer reuse. UI summary/details are recorded separately in `final-report-ui-20261010.json`;lower table rows were not visually verified.

Fourteen candidates are added for these report fields/structures. They overlap semantically with source activity/station state but have different storage and finalization lifecycle. No candidate ranking or production export selection was made. Further work includes successful report+4,nonzero late/deviation/action/termination cases,report reset timing,strings and serialization. The broad goal remains incomplete. Simulator is left on the early-exit Evaluation Details page,player0,day64810.8515625,paused0;no capture runs and no gameplay is active.
