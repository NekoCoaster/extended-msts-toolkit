# Player station departure and next-stop selection

Resumed 2026-10-10. Independent read-only research; no production NEMT changes.

## Fixture and bounded question

Can actual player movement produce the recorded departure and selected-stop advance that the earlier stationary Maryland experiment did not reach? Normal UI loaded Northeast Corridor > Morning in Maryland (`USA1/ACTIVITIES/morningmaryland.act`) in PID12888. `read_live.py` revalidated executable SHA256 `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843` before probing. Initial route-selection snapshot has null player/controller roots and a nested registry error; it is not a loaded-game observation.

`read_station_series.py` retains its exact sources and acquisition metadata in `captures/maryland-resume-departure-20261010-01`. The probe requests QUERY_LIMITED_INFORMATION | VM_READ only. UI lever drags left SelfLap67% unchanged; semicolon decrements released the train brake. Forward and 3% throttle produced slow movement. F10 displayed Baltimore actual departure08:00:55 and the next-station distance18.71 miles. Escape paused at28862.025390625 with sampled speed0.2280087173m/s. No save was overwritten.

## Observed transitions

Reproduce with `python analyse_station_departure.py`; the JSON summary contains final sample totals and read-consistency counts.

* At28810.900390625 the first record retained flags0x22. At28811.025390625 it had0x62 while speed0, departure0 and selection unchanged. This repeats the schedule-related cue latch.
* At28855.275390625 departure was still0 and Baltimore was selected. At28855.400390625 departure became28855.400390625, flags changed0x62->0x6a, selected became Edgewood56431456 and previous became Baltimore56431416. Sampled speed at the latter observation was0.1036876813m/s.
* The first record's scheduled departure remains28811.0; recorded departure is a distinct retained event value. Arrival remains28801.0 and may have been synthesized by the already traced startup branch.
* Effective service+208 remains0.75 even after selection advances to Edgewood, whose record+24 is0.2890630066. This directly cautions against treating selected-record change as proof that the effective efficiency override was applied.
* Boarding-active and remaining time stay0 throughout. Both observed AI services have empty station lists. These observations do not validate a boarding countdown, an AI station departure, final-stop completion or the full timetable lifecycle.

The observations are asynchronous, not atomic events. The stored native departure value agrees with the sampled clock at its first observation, but is not an independently measured exact platform-crossing time. Pointer/list consistency checks cannot exclude every transient change or identity reuse. Existing native-writer analysis supplies the interpretation; this run did not repeat disk/live instruction comparisons.

## Continuation

Representative player departure and next-stop selection now have positive runtime evidence. True boarding countdown, populated AI stops, later efficiency updates, final stop/outcomes and broader lifecycle cases remain open. The simulator is paused; the research goal remains active and incomplete.
