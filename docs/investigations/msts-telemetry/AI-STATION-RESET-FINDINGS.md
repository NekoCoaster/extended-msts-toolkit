# AI path-end reset and retained station selection

Validated 2026-10-10 in Tokyo-Hakone Passenger Activity Tutorial, supported train.exe PID12888. This is independent read-only telemetry research; no production runtime changes.

## Result

AI service9 reaches its path end, then disables updates, clears progress and reselects its first station record. A non-null selected station and retained positive speed therefore do not establish renewed movement or boarding. The earlier service8 reselection is consistent with the same reset, but its original capture lacked the update context needed to independently establish that transition.

Capture `captures/tokyo-ai-end-context-20261010-01` contains1764samples over180wall seconds at nominal0.1s:0read errors,0nested context errors,11clock-crossing reads and0flagged station/list instabilities. Reproduce with `python analyse_ai_station_reset.py`; output is `ai-station-reset-20261010-summary.json`. Bounds below are adjacent sampled simulation clocks, not exact instruction timestamps.

| Service9 transition | Sampled bounds in seconds | Evidence |
|---|---|---|
| Physical instance removed |65167.5234375 to65167.6484375|Physicalized1 to0, train pointer cleared; update gate remains1, station selection remains null.|
| Path-end flag raised |65223.5234375 to65223.6484375|service+1e0 becomes1; progress4138.37841796875, speed5.78689432144165m/s.|
| Scheduler reset |65224.6484375 to65224.7734375|update gate+144 becomes0, path-end+1e0 clears, progress+1d0 becomes0, selected+34 becomes56245280; previous+38 retains that record.|

All456inactive service9 observations retain speed5.78689432144165 and last-update65223 while progress remains0. Service8 is inactive throughout all1764samples with the same retained speed, progress0 and last-update65040. This is cached speed, not evidence of movement after deactivation. Neither service supplies a timed boarding-stop observation here.

## Native corroboration

Historical targeted exports were copied with provenance to `captures/ai-selection-native-20261010-01`, then compared against disk and live memory:4functions,909exported instructions,4081bytes,0mismatches and0read errors. The final report is `captures/ai-selection-native-20261010-01-byte-verification.json`; the initial three-function verification is retained separately. These are newly checked exported ranges, not a fresh whole-function decompilation or complete caller audit.

Scheduler005a662e tests enabled+144 and path-end+1e0, clears both at005a66ed/005a66fa, clears progress+1d0 at005a6747 and other stop bookkeeping, then calls0040355d at005a6785 and stores its return into selected+34 at005a678d. Verified thunk0040355d jumps to005a51ad, the distance-based ordered-record selector. Resetting progress to0 can thus select the first record again. This branch does not replace previous+38 or speed+138. AI updater005a41c2 separately maintains selection/previous and stop countdown during ordinary progression.

The observed path-end pulse followed by gate/progress/selection reset corroborates this branch; its execution was not instruction-traced. Sequential registry-context and station reads are not atomic. Zero flagged instability is a limited consistency check, not proof that every field belongs to one simulation instant. Do not infer service restart, boarding, movement, completion of the player activity, or universal AI lifecycle behavior from selection alone.

## Preserved state and remaining scope

Capture ended paused at65242.0234375, player speed0. Normal UI emergency braking stopped the player, throttle0; no assets or saves were modified. AI rephysicalization, reversal, scheduled station timing and broader lifecycle applicability remain open. Research goal remains incomplete.
