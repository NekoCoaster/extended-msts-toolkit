# Final-station loading and activity success

2026-10-10: Tokyo-Hakone Passenger Activity Tutorial, supported MSTS Bin executable SHA256 `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`, PID12888. This bounded experiment validates one positive AllStops/ActivitySuccess path. Research remains incomplete; no production NEMT code, game asset or save was changed.

## Question and result

Does finishing the final station's loading trigger the loaded AllStops event and actual activity-success state? Yes in this fixture: loading expiry precedes event0 latch and both result fields becoming1. The UI then displays **Activity complete**. Success occurs while the last station remains selected and its recorded departure is still0. An earlier station retains interrupted-loading flags0x1a, so this result does not certify perfect loading at every stop or timetable compliance.

The preceding location event39 congratulations message is a separate message outcome. At simulation time65974.1484375, that message was visible while event0 latch, evaluation-stop and success remained0. It said the activity would end after the loading countdown reached0. The actual result was observed separately after loading.

## Retained transitions

`captures/tokyo-activity-outcome-20261010-01/samples.jsonl` contains6044samples with0read exceptions. `analyse_activity_outcome.py` produces `activity-outcome-20261010-summary.json`. Times below are sample brackets in simulation seconds, not instruction timestamps.

| Observation | Previous / first changed sample | State |
|---|---|---|
| Gotokuji loading accepted |65666.8984375 /65667.0234375|Arrival65667.0234375,active1,first remaining179.875,flags2|
| Gotokuji loading expires |65846.8984375 /65847.0234375|Active0,remaining0,flags0x62,result fields0|
| Gotokuji departure |65883.0234375 /65883.1484375|Departure65883.1484375,flags0x6a,selection advances to final platform481|
| Final loading accepted |65979.1484375 /65979.2734375|Arrival65979.2734375,active1,first remaining33.20833206176758,flags2|
| Final loading expires |66012.3984375 /66012.5234375|Active0,remaining0,flags0x62,event0 latch0,result fields0|
| AllStops success |66012.5234375 /66012.6484375|Event0 latch1,evaluation-stop1,success1,paused1,speed0|

The expiry sample has equal start/end clock66012.5234375 and both separate result reads0. The next changed sample has equal start/end clock66012.6484375 and both result reads1. This supports the observed ordering but is not an atomic snapshot or a universal one-frame latency guarantee.1033samples retain success. Final selected record56244880/platform481 remains nonnull,previous56244800/platform464;final recorded departure0. Earlier platform70/record56244720 remains0x1a,without0x20.

## Native interpretation

Loaded event0 has category1/action,type2,activation1,outcome `[6,0,0]`;the ACT fixture identifies EventTypeAllStops and ActivitySuccess. The exported assembly of0059b27b accesses the embedded player service at activity+0x80,station list+0x30 and selection+0x34. It returns false for a null/empty list;true for null selection in a nonempty list;otherwise true only when identity successor00690280 returns0 and selected-record flags+0x1e contains0x20. It does not scan earlier records for completed loading. The observed final-selected path matches this predicate;the null-selection and empty-list branches were not exercised as success cases here. The helper also returns0 for missing identity;the analysis reports unknown for an invalid selected identity rather than treating malformed state as validated completion.

Outcome handler0059ae8e type6 writes activity+0x348 and+0x34c to1. Existing evaluator findings identify the stop guard and latch-before-outcome sequence. The captured event0 transition and UI result agree with this path;this is not an instruction execution trace. `captures/all-stops-native-20261010-01` retains copied historical exports and provenance;its sibling byte-verification report checks197instructions/661bytes across3functions against disk and live memory,with0mismatches/errors. Only exported ranges were checked;decompiler calling conventions are not substituted for the assembly arguments.

## Extraction and limits

`read_outcome_series.py` composes the existing station/service reader with the bounded event reader,using only QUERY_LIMITED_INFORMATION | VM_READ. Exact probe sources and hashes accompany the capture. The requested maximum was900seconds at0.1second intervals;after result observation a local stop.request ended it cooperatively. No process memory write or native function call was made.

Quality:190whole-read clock crossings,0flagged event-root changes,0flagged station selection/sentinel/node instabilities and0disagreement between the two result reads. Stable checks do not prove atomicity,complete event-node consistency or absence of pointer reuse. `activity-outcome-ui-20261010.json` records the separately observed UI and fixture hash;it is an observation note,not a saved screenshot or independent timing instrument.

Final state: actual Activity complete alert remains open,paused66012.6484375,speed0,throttle0,Forward,emergency brake. No capture remains running. Failure outcome7,reset/reload/result dismissal,other action predicates,AI timed stops and universal termination behavior remain unvalidated. Existing runtime modifications and the supported build bound transferability;the positive result applies to this observed installation.
