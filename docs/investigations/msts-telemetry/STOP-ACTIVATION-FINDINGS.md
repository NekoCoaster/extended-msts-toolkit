# Stop-required event and mutable activation

2026-10-10, Tokyo-Hakone Passenger Activity Tutorial, PID12888 on the supported executable. Normal UI approach/stop and external read-only probes. No assets or saves changed.

Event32 (Setagaya Stop) requires a stop inside its60m radius. It has message outcome5 and two outcome2 records targeting event IDs42 and44. The capture records49samples inside the radius while the stop condition is false and latch remains0. At simulation65501.5234375 the player speed is0.0211279355m/s with latch0; at65501.6484375 speed is approximately-0.0000006984m/s, distance41.4146512703m and latch1. The good-platform-stop message appears in the UI. The previous sample already satisfies the reconstructed stop threshold, so this is not proof of exact same-frame native evaluation or an exact threshold crossing timestamp.

In the same sampled bracket, targets42 and44 change current activation+24 from1 to0. Their reset baseline+20 stays1. Event42 was already latched1 and retains it; event44 was unlatched0 and retains it. Thus disabling current activation neither clears an existing latch nor changes the reset baseline. The source event remains activated1 and latched1. No reversal or reset operation was tested.

## Evidence and native meaning

`captures/tokyo-stop-activation-20261010-01` retains the full event/geometry series and UI observation with fixture hash. `analyse_event_activation.py` generates `event-activation-20261010-summary.json`, including all latch/activation changes, quality counts and final state. Additional message events14,47,52,30 and time-event48 fire during the approach; these are included rather than silently removed. Three route-origin tile pairs occur. Origin/player/sentinel rereads are limited consistency checks, not atomicity guarantees or a complete origin-boundary study.

Existing verified0059b146 compares horizontal radius and absolute first-player-train speed against double0.10000000149011612. Existing verified0059ae8e outcome2 resolves the target via0059c430, subtracts1 at0059af59 and stores target+24 at0059af5f; it does not clear target+10 or replace+20. Fresh ID-lookup verification covers29instructions/71bytes with0disk/live mismatches/errors (`captures/event-target-lookup-native-20261010-01-byte-verification.json`). The same-PID event handler/predicate verification from EVENT-TRANSITION remains applicable. This is exported-range checking,not instruction tracing.

Signed current activation,reset baseline,and trigger latch must remain distinct telemetry. Only the1to0 decrement case is validated here; increment,negative activation,reset-to-baseline and reversible-event clearing remain open. The scene was later used for the separate unfinished-loading departure test, documented in EARLY-DEPARTURE-FINDINGS.md.

Final capture totals:5566samples,0errors,129clock-crossing reads,0flagged origin/player/sentinel instability. Final paused65562.3984375,speed0.0.
