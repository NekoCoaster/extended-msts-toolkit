# Service scheduling, stale values and update validity

## Established code behavior

Native scheduler `0x5ae68e` walks the service list and skips services whose uint32 +0x144 is zero. `0x5a662e` compares scheduled start float +0x24 against its one-second scheduling window, enables +0x144 after successful initialization, and writes the full or partial integration interval to +0x14c. `0x5ae0f8` consumes that interval and writes AI last-update time +0x150. The physical AI path `0x5ae731` computes a time delta from +0x150, including an apparent day-wrap branch, then calls `0x5a5c9a`. Midnight has not been tested.

`0x5a662e` also disables +0x144 when path-end condition +0x1e0 is nonzero, and clears +0x1e0 in the same branch. Consequently, a later zero path-end flag is not proof that path-end handling never happened. That branch does not directly zero speed +0x138. Native `0x5a41c2` treats +0x1dc equal to one as positive travel and other values as negative; this is distinct from track direction and player reverser.

These conclusions were checked against assembly, not decompiler output alone. Pass28: 1,362 instructions / 5,770 bytes; pass29: 612 instructions / 2,185 bytes. All exported instructions matched both installed disk and live process, with zero read errors. Coverage is limited to the exported instructions, not a whole-image or all-caller proof.

## Live corroboration

`captures/service-schedule-paused-01/services.jsonl`, PID 7160, paused time 74525.53125:

| Value | First AI (ID 2) | Later AI (ID 3) | Player |
|---|---:|---:|---:|
| Scheduled start +0x24 | 73020 | 74460 | 73800 |
| Update gate +0x144 | 0 | 1 | 1 |
| Integration interval +0x14c | 1 | 1 | 0 |
| Last update +0x150 | 74316 | 74524 | 725.528076 |
| Physical train pointer | null | null | valid |
| Speed +0x138 | 4.426947 | 7.207724 | 0 |

The existing long capture first reaches the first AI's final unchanged 0x68-byte track record at sample 334, time 74317.125; preceding sample 333 at 74316.125 still had speed 4.777559. The stopped update clock and zero update gate explain why its old positive speed is not current movement telemetry. This is no longer merely an unexplained disagreement between two speed estimates.

**Not proven:** the exact gate-off moment was not captured because the earlier reader lacked +0x144. Path-end handling is a code-supported explanation for deactivation, but this run does not directly prove which caller deactivated it. The earlier sample-215 doubled position increment also remains unresolved; it must not be explained by this later gate-off result.

The player last-update value is near elapsed activity time (simulation time minus 73800), unlike the AI clock. Do not export a uniform service timestamp or freshness age without identifying the producer/time base. Update interval is not a wall-clock sampling guarantee. +0x148 and +0x154 remain offset-labeled candidates in captures; their semantics are not established here.

## Extraction implications

Read service identity, update gate, physical-instance state and last-update time alongside AI motion fields. Inactive is not equivalent to absent, finished, or not-yet-started; distinguish these only with schedule/history and supporting state. Null physical train is compatible with actively moving AI. Keep raw values with their validity context instead of silently replacing stale values with zero. These are evidence and interpretation constraints, not keep/drop decisions.

Game remained paused throughout this investigation; no process writes, asset changes or NEMT production changes were made.
