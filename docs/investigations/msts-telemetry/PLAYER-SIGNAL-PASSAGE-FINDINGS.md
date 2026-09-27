# Forward start and next-signal transition

After the emergency acknowledgement described in DIESEL-EFFORT-GATE-FINDINGS.md, normal UI resumed the preferred grain activity, selected N4 with brakes holding, then applied 48 semicolon inputs to release the train brake. Cab showed N4/900 A and Released; pipe/equalizing pressure recovered to 90 PSI and cylinder pressure reached zero. Signed speed became positive and signal distance decreased. No settings, saves, assets or game memory were written.

Two separately bounded read-only streams preserve this experiment. `player-cleared-passage-01` ends at simulation day-seconds 74322.859375; `player-cleared-passage-02` begins at 74378.578125. The intervening 55.71875 simulation seconds are **not captured**. Do not join these into a continuous acceleration trace. Each capture contains its exact probe and metadata. `analyse_player_signal_passage.py --name <capture-name>` reproduces the summaries.

Within the second stream, consecutive samples bracket a next-signal change:

| Field | Before | After |
|---|---|---|
| Simulation day-seconds | 74410.078125 | 74410.25 |
| Iterator node pointer | 114971836 | 114971900 |
| Direction selector | 0 | 1 |
| First/last node-local indices | 46/46 | 21/21 |
| Selected head address | 62412704 | 93791448 |
| Selected normal aspect | 7 | 7 |
| Next-signal distance, metres | 7.9150390625 | 2710.1025390625 |
| Signed player speed, m/s | 12.684707641601562 | 12.710098266601562 |

Both rows have stable clock and iterator rereads; asynchronous external reading is still not an atomic snapshot. This validates a representative forward approach and next-signal selection transition after clearance. The previous distance remained positive at the last old selection, so the data does not establish an exact locomotive-reference geometric crossing, a zero-distance event, or a universally valid passage trigger. Direction selector change reflects the iterator's local orientation; the player reverser stayed FWD and signed speed stayed positive. Indices alone are not globally unique signal identifiers. No separate speedpost or track topology crossing was measured.

MSTS was paused after the change at day-seconds 74421.9296875, N4, signed speed 14.246537208557129 m/s (cab 32 MPH), next signal 21/aspect 7/distance 2532.658203125 m. Pause freezes a moving state; it does not zero speed. Resume with that state in mind. Candidate count is unchanged; this adds runtime evidence to existing fields.

Final counts: first stream 2383 samples (2179 paused), second 1788 (1487 paused); zero read/signal errors and zero iterator reread differences. Each stream has three clock-crossing samples, away from the bracketing pair. Initial near-stationary speed includes slight negative creep to -0.00311 m/s before sustained forward movement; do not claim positive speed throughout the start.
