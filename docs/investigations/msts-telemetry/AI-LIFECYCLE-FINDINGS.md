# Scheduled AI lifecycle observation

Independent read-only research, incomplete. Capture `captures/scheduled-traffic-01/lifecycle.jsonl` contains 539 samples, zero top-level read errors, simulation time 74000.0546875 through 74522.0390625. 171 samples crossed a simulation step; successful reads are not atomic snapshots. Reproduce the summary with `python analyse_lifecycle.py scheduled-traffic-01`.

## Observed transitions

| Service | Observation | Boundary |
|---|---|---|
| EveGrain (Traffic), ID 2 | Physical train pointer and physicalization flag became zero at 74064.96875; service remained loaded | Object disappearance is not service deletion |
| EveGrain (Traffic01), ID 3 | Flags changed 4 to 20 at 74460.765625, near configured 20:41 start; movement followed | No physical train instance appeared during this capture |
| Player, ID 0 | Physical train remained present; speed stayed zero | Player physicalization flag remained zero despite valid train |

First AI crossed 37 section boundaries. Later AI crossed two after initialization; initial null-to-valid track record is excluded from boundary counts. Later AI reached 6.78867 m/s in the capture, with target 13.41120 m/s and acceleration 0.1396845 m/s². Among 33 eligible position/speed comparisons its largest chord-speed discrepancy was 0.05009 m/s. These observations support offscreen kinematic movement for this service, not complete equivalence with physical train simulation.

## Positive speed does not always establish movement

Follow-up: [Service update findings](SERVICE-UPDATE-FINDINGS.md) identifies the disabled update gate and stopped AI update clock. The exact deactivation trigger and earlier doubled-position outlier remain unproven. The discussion below preserves the initial observation.

First AI retained speed 4.42694664 m/s while track position was stationary from the later portion of the run. At sample 338 (74321.140625), the position-derived speed was zero with a one-second interval and unchanged coordinate origin. This persisted through the end. A prior outlier at sample 215 gave position-derived speed 31.05023 m/s versus native speed 15.64640 m/s. `scheduled-traffic-01-summary.json` preserves representative anomalous comparisons.

The discrepancy is unresolved: stale completed-service fields, coarse updating, and other lifecycle conditions require native producer tracing. Do not label positive speed as proof of active movement, or apply physical-train velocity semantics to every loaded service. Even same-simulation-time sampling does not prove all fields were produced together.

Final paused check at 74525.53125 (`captures/service-lifecycle-final-paused/services.jsonl`) still showed ID 2 speed 4.42694664, target zero, no physical train, flags 20. Stop-state words +0x1e0, +0x1e4, +0x1e8 and +0x214 were zero; +0x1dc was one. These candidates do not by themselves explain the freeze. ID 3 speed was then 7.207724 m/s, still without a physical train.

## Sampling and remaining work

Origin stayed [-12560,14766], so this run does not validate origin shifts. Player remained stopped; no event-trigger or alternative-engine validation was performed. AI physical reappearance and service removal remain untested.

`captures/reader-cost-01/measurement.json` measures 30 combined external snapshots: median 2.80785 ms, maximum 6.0994 ms; eight crossed a simulation step. This measures reader execution cost only, not game frame-time impact.

Game left paused at 74525.53125 with player intact (23 cars, zero derailment flags), emergency brake applied. NEMT production code and game assets were unchanged; no save was made. Existing runtime modifications remain an explicit limitation of this installation.
