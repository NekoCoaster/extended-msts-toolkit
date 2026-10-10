# Activity dismissal, debrief retention and UI restart

2026-10-10, Tokyo-Hakone Passenger Activity Tutorial, PID12888, supported executable SHA256 `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`. Continuation of ACTIVITY-OUTCOME-FINDINGS. Ordinary UI dismissal and Restart Activity were used;no game assets,saves,settings or production sources changed.

## Result

The Activity complete alert is not a persistent result store. Dismissing it leads to evaluation UI and clears the activity stop/success fields while evaluation records remain available. Restart Activity resets the two clocks and rebuilds gameplay state. Old station selection and clock values can remain after the corresponding lists/player are gone;new list roots and selection appear before the player/controller. None of these pointers alone establishes load completion.

`read_session_reset.py` samples only fixed globals and never dereferences stored heap pointers during unload/loading. The1784samples contain0read exceptions and0start/end day-clock differences. These checks do not make a sequential sample atomic. `analyse_session_reset.py` writes `session-reset-20261010-summary.json`;capture files and exact sources are retained in `captures/tokyo-result-reset-20261010-01`. A local stop.request ended the bounded600second capture after90.488215seconds.

## Observed sequence

Times in this table are seconds since probe start,not simulation time or exact native instruction timestamps. A row reports the first sampled changed state.

| Wall elapsed | Observed state |
|---|---|
|0.000413|Actual completion alert open;paused1,stop1,success1,player56611120,controller57552564,day66012.6484375,elapsed1212.6500244140625|
|14.112866|After dismissal,pause0 while player,lists and result1/1 still present|
|14.265161|Player/controller/control type0,station/event roots0,stop/success0;old selected56244880 and previous56244800 remain|
|66.940574|During restart,day64800 and elapsed0;new station/event roots,selection0,player/controller0|
|66.991260|New selected record55485724 appears while player/controller remain0|
|67.092599|New player56329944 appears while controller/type remain0|
|67.143368|Controller57739272,type3 appear;clock still64800|
|69.121390|Startup briefing visible separately;pause1,day64801.2265625,elapsed1.225000023841858|

The simultaneous sampled clock decrease is bracketed by wall66.889715..66.940574. This is a normal UI restart reset,not midnight wrap or saved-game restoration. Day/month/year remain3/6/2000;clock components change from18:20:12 to18:00:00 and subsequently18:00:01. Internal calendar provenance and narrative date remain unresolved. Existing CLOCK-FINDINGS documents the native setter and the installation's timing patches;this experiment does not validate stock MSTS floating-point behavior or reverify those patch bytes.

1038samples contain a nonzero old selection with station root0.1041samples have no player and result0/0. Pause0 persists through the debrief and parts of loading despite no active player and no advancing clock. Interpret these as observed lifecycle states,not universal readiness rules. Root changes and matching clock reads cannot rule out unseen intermediate changes or pointer reuse.

## Restarted objects and event definitions

After the UI briefing appeared, `captures/tokyo-restarted-outcome-20261010-01` uses the existing bounded station/event reader. It finds the fixed embedded player service8427664 with new station objects,platform9 selected,previous0,player speed0,boarding0 and result0/0. Event0 AllStops latch is0. Events32/42/44 also have latch0 and activation/baseline1;earlier activation decrements and latches did not persist through restart. This is reconstruction/reinitialization evidence,not execution of event outcome4 ResetActivationLevel or reversible clearing.

The first station already has flags0x22 and recorded arrival64805 even though current time64801.2265625 precedes it. Other records have flags0 and arrival/departure0. This agrees with the previously traced initial synthetic-arrival path and reinforces that recorded arrival is not invariably the physical stop or user loading time. Final selected record from the old run was56244880;the rebuilt final record is55486084. Do not carry those session-local identities across reload.

## Evaluation retained after gameplay teardown

The evaluation summary displayed completion after20minutes13seconds,one minor error,four late stations,overall9minutes25seconds late,and three speed-limit episodes totaling47seconds. Details identified the error as leaving a station while loading at18:12:07,km5.36,and stated that no station was missed. `session-reset-ui-20261010.json` retains these UI observations;it is not a saved screenshot.

`captures/tokyo-final-evaluation-20261010-01/evaluation.json` reads the independently retained report after gameplay teardown. Three completed speed records have durations42.25,1.875 and3.0,total47.125,count3. The sole operational record is code64,time65526.7734375,marker location5.3583502769470215. Its timestamp exactly matches the earlier interrupted-loading departure capture;the installed label mapping and debrief text agree. The emission itself was not sampled by this turn's global reader. UI rounded display values support this example without proving every display conversion or route interpolation.

`captures/tokyo-restarted-evaluation-20261010-01/evaluation.json` has speed count/duration0,empty speed and operational lists,count0 and zero active speed details. Thus this report survives dismissal into debrief but resets by the next started activity. Report reset timing was not continuously sampled. Freight/passenger condition lists remain empty in both snapshots;no new positive condition semantics are established.

## Boundary and continuation

The simulator is left at the restarted tutorial briefing,paused64801.2265625,player speed0. No capture remains running. Native function calls/process writes were not used. Only observed installed-build paths are validated:failure outcome7,saved-game result restoration,midnight/calendar carry,other load paths,complete-ready indication,AI timed stops and remaining broad discovery/semantic review remain open. The overall goal is active and incomplete.
