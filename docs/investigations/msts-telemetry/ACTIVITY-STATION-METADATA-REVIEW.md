# Activity and station metadata review

2026-10-10, against published checkpoint fec7342 and the current canonical evidence. This is a field-specific review of all20activity and7station candidates,not the inventory-wide semantic audit or a claim of research completion. No new gameplay was performed. Supported PID12888 was rechecked paused at65562.3984375,player speed0.

## Method and corrections

Compared each candidate's meaning,type,units,extraction,applicability,cadence,evidence status and limitations with the relevant native findings and retained captures. The catalogue contained historical blanket descriptions that no longer matched the newer evidence:time events described as untested;clock reset described as unresolved despite CLOCK-FINDINGS;geometry given clock cadence;station departure described as absent;and unrelated efficiency/cue limitations copied across station fields.

`activity-station-reviewed-metadata.json` is the reviewed declarative metadata applied by `build_inventory.py` after historical evidence accumulation. It preserves candidate identities,types,counts and all original evidence paths,while replacing stale summaries and deduplicating repeated evidence links for these27entries. Original historical reports and raw files remain unchanged. New activity/station candidates cause an explicit review-scope error instead of silently inheriting this review.

## Field-by-field disposition

Each row is a scoped metadata reconciliation. Retained native offsets/types are supported by the referenced findings,not newly verified whole-program semantics.

| Candidate | Evidence used and corrected interpretation | Remaining limitation |
|---|---|---|
|activity.event_registry|Tokyo baseline50events:14time,34location,2action;broaden observed list coverage|Action presence does not validate action predicates;root stability not atomicity|
|activity.event.id|Fixture IDs and native0059c430 target lookup;stop-event target changes|Identity reuse/load lifecycle|
|activity.event.category|Tokyo category0time,1action,2location versus ACT categories|Other enum values|
|activity.event.type|0059b083 dispatcher;time0/location1;raw action2/3 present|Action predicates not live-validated|
|activity.event.state_10|Location/time latches and non-reversible persistence|Reversible clearing/reset|
|activity.event.state_20|Baseline1 retained during target decrement;native reset source|Actual outcome4 reset/non-default baseline|
|activity.event.activation_level|Targets42/44 current1to0 with unchanged latch/baseline|Increment,negative level,reset,reversal|
|activity.event.location_tile|Signed tile offsets and retained first-car/origin joins|Full origin-boundary invariance|
|activity.event.location_offset|Fixture X/Z values and finite reconstruction|Nonfinite/exact floating-point boundaries|
|activity.event.location_radius|Event13 radius10 and stop32 radius60|Invalid/negative radii|
|activity.event.trigger_on_stop|Moving event13 versus stop-required32 with49inside-moving-unlatched samples|Exact evaluation cadence/equality edge|
|activity.event.outcome_count|Loaded0..3counts;bounded common layout|Stored count not dispatch success count|
|activity.event.outcomes|Types2/5/6present;decrement2 and message5executed|Other outcomes and global result lifecycle|
|activity.event.reversible_candidate|Native conditional reevaluation;live zero-case persistence|Nonzero-case clearing|
|activity.event_evaluation_stop|Native guard/writers;zero during non-result tests|Nonzero result and UI lifecycle|
|activity.event_outcome_success|Native outcome6/7stores;zero during non-result tests|Actual success/failure;zero alone not failure|
|activity.time_event_clock|CLOCK producer/reset tracing;time45/48elapsed crossings|Runtime reset/midnight and stock timing precision|
|activity.event.horizontal_distance|Derived per sample;radius crossing/stop distance|Not a native stored distance;origin handover and x87 limits|
|activity.event.location_condition|Derived spatial/optional-stop predicate versus actual latch|Excludes activation/latch/reversal/global gates|
|activity.event.time_threshold|14stored thresholds;time45threshold468 matched|Post-transition read;exact equality/reset|
|station.recorded_arrival|Accepted ENTER writes;alternate native synthesis branches|Not necessarily physical stopping time;AI semantics|
|station.recorded_departure|Normal and unfinished-loading departure writes|Not necessarily platform crossing or loading completion|
|station.scheduled_arrival|Maryland/Tokyo declarations;AI zeros with omitted declarations|AI timetable merge/mutation|
|station.scheduled_departure|Schedule versus recorded departure and cue|AI timetable merge/mutation;zero not proven midnight stop|
|station.state_flags|Arrival2,expiry/cue0x62,normal departure0x6a,interruption0x1a|Partial branch meanings;AI equivalence|
|station.boarding_active|Activation,pause,expiry and cancellation|Inactive is not proof of completion|
|station.boarding_remaining|Positive/decreasing/paused/expired/cancelled values|Duration factors;zero ambiguous;AI applicability|

## Sources and validation boundary

Principal evidence:ACTIVITY-EVALUATOR,CLOCK,EVENT-TRANSITION,STOP-ACTIVATION,STATION-TIME,STATION-DEPARTURE,STATION-BOARDING and EARLY-DEPARTURE findings;Tokyo baseline event list;time-threshold snapshot;and their native exported ranges and raw transition captures. The baseline confirms50events and outcome counts0..3 with types2,5,6. Native0059b083 dispatches by type+8;category+4 is not substituted for it.

The generated structural audit checks evidence existence and installed source hashes. The scoped before/after comparison records whether other1017candidate records changed and whether any original evidence paths were lost. Neither check proves semantic completeness. This review still leaves all explicit limits above and every unaudited candidate family open;no candidate ranking,selection or production integration was performed.

The before/after check compares published inventory to published inventory:the existing sync script strips `decompiler_excerpt` from cab metadata. An initial canonical-versus-published check detected those expected67cab excerpt differences;the like-for-like comparison confirms only27reviewed candidates changed and all other1017records are identical. See activity-station-review-20261010.json.


## Subsequent outcome evidence, 2026-10-10

ACTIVITY-OUTCOME-FINDINGS.md supersedes the above historical unvalidated-success and unvalidated-type2 descriptions. The declarative metadata now incorporates one final-selected AllStops/ActivitySuccess transition and final loading/departure semantics. The review above and its before/after report describe checkpoint3667952;they are not rewritten as if that later experiment had already happened. Failure/reset and broader semantic review remain open.
