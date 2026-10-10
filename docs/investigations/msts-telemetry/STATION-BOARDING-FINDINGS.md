# Player boarding countdown and populated AI station records

Completed representative station sequence on2026-10-10. Independent discovery only; no production NEMT integration or telemetry selection decisions.

## Fixture, acquisition and UI evidence

Normal UI loaded Tokyo-Hakone > Passenger Activity Tutorial, `JAPAN1/ACTIVITIES/tokyohakonetutorial.act`, Series2000 player train. PID12888 retained the supported executable hash `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`. Baseline at64801.2734375 has five player station records and two AI services with one record each. The first player station, Sangubashi/platform9, already has flags0x22 and a recorded arrival copied from the scheduled64805.0; it is not a suitable true-arrival/boarding test.

The player departed Sangubashi, drove to Yoyogi Hachiman/platform29 and stopped with F10 showing approximately-0.04km. The UI accepted the stop and offered ENTER to load/unload. ENTER started a displayed50-second loading period. Escape paused during that period, then normal UI resumed it. After expiry the brake was released and low traction produced departure, advancing F10 to Setagaya Daita/platform70. Tutorial dialogs paused the simulation during the drive. The slight platform overrun was accepted; no optimal stopping-position or loading-time formula is inferred.

Capture `tokyo-boarding-20261010-01` has2971samples over a requested600wall-clock seconds at nominal0.2s interval:0outer errors,1334paused samples,20clock-crossing reads,0flagged service/list/record-pointer instabilities. Gameplay clock spans64802.0234375..65132.6484375. Exact `read_station_series.py`, `read_services.py` and `read_live.py` sources and hashes are retained. The only sampler extension is the already traced global frame-delta read at828fb4. External access remains QUERY_LIMITED_INFORMATION | VM_READ; no injection, process writes or native calls.

Reproduce the summary with:

```powershell
python analyse_station_boarding.py tokyo-boarding-20261010-01 --output station-boarding-20261010-summary.json
```

## Player transitions

All brackets below are consecutive observation starts; they are not exact native event timestamps.

| Transition | Previous start -> first changed start | Observed values |
|---|---|---|
| Sangubashi departure |64897.0234375 ->64897.2734375|Record departure64897.1484375,flags0x62->0x6a;selected becomes Yoyogi and previous Sangubashi.|
| ENTER/boarding accepted |65044.6484375 ->65044.8984375|Yoyogi arrival becomes65044.7734375,flags0->2;boarding active0->1,first sampled remaining49.75.|
| Deliberate pause during loading |Repeated clock65052.3984375|Remaining42.25 stays identical across90consecutive paused active pairs.|
| Countdown expires |65094.6484375 ->65094.8984375|Active1->0,remaining->0,Yoyogi flags2->0x62. Bit0x20 completion and0x40 cue latch appear together at this sampling cadence.|
| Departure after loading |65113.6484375 ->65113.7734375|Yoyogi departure becomes65113.7734375,flags0x62->0x6a;selected advances to Setagaya Daita and previous retains Yoyogi.|

There are339active samples and247falling adjacent active pairs, with observed decrements0.125..0.25seconds. Multiple native updates may occur between samples. The first positive observation is49.75, while the UI displayed50; no claim that the sampler caught the exact initialization write. Recorded arrival occurs at accepted loading, several seconds after the train physically stopped, so it must not be described as an exact wheel-stop sensor timestamp. F10 displayed rounded actual arrival18:04:05 and departure18:05:14.

Effective player service+208 remains1.0 across selection advances, while Yoyogi and later record+24 values are0.5. This repeats the Maryland finding: selected per-stop efficiency and effective service efficiency are separately observable; selection change alone does not prove application of an override.

## AI records and selection lifecycle

The activity explicitly configures two `Tut3TrafficService` entries (IDs8 and9), with platform459,distance64.043 and efficiency0.75; it supplies no ArrivalTime/DepartTime fields for these AI entries. Both live station records contain that platform and approximately64.04297distance, with all four schedule/recorded time values0 and flags0 throughout. This is positive populated-list evidence, not evidence of timed AI boarding.

Service9 at55277172 advances selected56245280->0,previous0->56245280 between64983.6484375 and64983.8984375. Service8 at55282476 later changes selected0->56245120 with previous still56245120 between65041.3984375 and65041.6484375. Its record times/flags stay0. This is a live example of non-monotonic selected-record lifecycle; null cannot be a universal route-completion indicator. The station sampler does not capture driver state or physicalization at those exact edges, so their causes are not assigned.

The separate final `tokyo-station-final-services-20261010-01` snapshot identifies IDs/keys and finds service8 without a physical train and service9 with physical train67976328. It does not establish their physicalization state at the earlier selection transitions. A train passing the player's cab was visually observed, without an exact UI-to-service identity join.

## Limits and current state

Pause verified at65132.6484375,player speed6.2985272408m/s,throttle20%,Forward,brakes released. Readings remain build/session-specific and asynchronous. The bounded pointer rereads do not guarantee atomicity, complete nested-registry validation or exclusion of address reuse. Raw records are retained for review. No save was overwritten and no installed route/train asset was edited.

Representative player arrival-on-loading, nonzero countdown, paused stability, expiry, departure and next-stop selection are now observed. Timed AI station stops, AI braking/boarding, final-stop outcomes, loading-duration factors, early departure during loading and broader lifecycle/reset cases remain open. These results do not complete the overall telemetry survey.
