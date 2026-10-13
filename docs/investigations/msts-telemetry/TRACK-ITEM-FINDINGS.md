# Track-item kinds and stored subtype payloads

Paused at simulation time 74525.53125 throughout. Probes used query/read access only; no controls or assets changed.

## Type and index join

The native item-array index matches `TrItemId` in this route. All 2,970 live nonnull entries joined without missing IDs or mixed type labels. The TDB contains 3,387 entries; all 417 additional asset-only entries are `EmptyItem`. Three more empty placeholders remain live. The reason those three are retained has not been traced; null slots are legitimate, not reader failures.

| Native kind | Route item name | Live count |
|---|---|---:|
| 0 | SignalItem | 292 |
| 2 | PickupItem | 1 |
| 3 | PlatformItem | 100 |
| 4 | HazzardItem (native spelling) | 593 |
| 6 | SidingItem | 226 |
| 7 | LevelCrItem | 180 |
| 8 | SpeedPostItem | 545 |
| 9 | EmptyItem | 3 |
| 10 | SoundRegionItem | 1030 |

Native serializer `0x5b5475` dispatches by this enum and emits the corresponding named tokens. Other binary-supported kinds are not established by this route sample. Hazard presence does not establish a currently active hazard; level-crossing and sound-region entries are not proof of barrier or audio state.

## Stored fields

Common nonempty item fields: float distance +0xc and uint32 flags +0x10, serialized as TrItemSData by `0x5b5d9f`. Empty records are excluded from these reads. Item identity is its database array index; this differs from one-based route-node IDs.

Platforms (kind 3), serializer `0x4e0730`: UTF-16 station pointer +0x28, platform name pointer +0x2c; flags +0x30 and paired endpoint item ID +0x34; minimum waiting time float +0x38; waiting passenger count uint32 +0x3c. Token names in the native table establish these semantics. Waiting values match loaded configuration; their runtime evolution is untested.

Sidings (kind 6), serializer `0x4e3d5d`: UTF-16 name pointer +0x14, flags +0x18, paired endpoint item ID +0x1c. Null name pointers remain absent in raw telemetry even though a serializer may substitute a display fallback.

Speed posts (kind 8), serializer `0x4f5703`: uint16 flags +0x28, byte payload +0x2a, float payload +0x2c, final angle +0x30. The byte is serialized when low three flag bits are 1 or 2, or are zero with bit 0x8 set. The float is serialized when low three bits are zero or bit 0x10 is set. Do not label every float as a speed limit: observed flags 896 have float 1088.9, consistent with a distance-marker payload. Exact subtype labels, unit flags, applicability to freight/passenger trains, direction and effective speed-limit selection remain open.

## Verification

`read_track_items.py` preserves the paused values and reader sources in `captures/track-items-paused-01`. `analyse_track_items.py` joins them to the installed TDB and writes `track-item-summary.json`, including asset hash and compact examples.

Zero comparison differences: 2,967 common distances (tolerance 0.02 m), 2,967 common flags, all 100 platforms' six payload fields, all 226 sidings' three payload fields, and all 545 speed-post serialized payloads (numeric tolerance 0.002). Platform waiting floats use tolerance 0.001. These are exact-current-asset comparisons within declared tolerances, not proofs of dynamic gameplay behavior.

Pass36: 782 instructions / 2186 bytes; pass37: 1609 / 4397. All exported instructions matched installed disk and live process, zero errors. Assembly arguments and field offsets were inspected because decompiler output omits some serializer register parameters.

These findings add 15 flat candidates and clarify the existing item-kind candidate. No telemetry has been prioritized or discarded. Further work includes active speed restrictions, crossing state, sound-region behavior, pickup availability, platform interaction and item-to-track/service applicability.


## Platform loader defaults, 13 October 2026

Retained loader 004e0450 establishes configuration producers distinct from gameplay consumers. Its switch subtracts token base 0x40326 and dispatches through a byte index and address table. Token 0x40329 maps to 004e0574: destination item+0x38 is passed to parser virtual slot+0x14; success sets the local presence flag. Token 0x4032a maps to 004e059d: item+0x3c is passed to slot+8 and success sets its separate presence flag. On successful completion, absent minimum-wait input receives bits 0x43340000 (float32 180) at 004e062f; absent passenger input receives uint32 20 at 004e063f. Failed field parsing exits via the failure path rather than establishing successful defaults. This is absent-token behavior, not a claim that explicit zero is replaced or values are clamped.

Evidence: captures/platform-loader-native-20261013-01 copies the retained loader and serializer; the sibling byte report verifies 406 instructions/1153 bytes against disk and PID39096 with zero mismatches/errors. dispatch.json separately verifies both relevant switch-table bytes and targets against disk/live. check_dispatch.py and its imported readers are retained. This proves current code/data correspondence, not that this session exercised absent-token loading, and does not resolve minimum-wait gameplay consumers or dynamic passenger evolution.

The bounded literal-token search of indexed exports found only serializer 004e0730. A read-only Ghidra scalar scan likewise reported that literal; its log contains a duplicate-source compilation warning from the archived source copy (now retained as .java.txt). Do not use this lexical scan as proof of no loader or other consumers: the loader encodes the token through switch-table arithmetic. The existing neighboring loader export supplied the decisive evidence without another decompilation.

A fresh one-shot manual-loading-state-20261013-02 read confirms PID39096 remains paused at clock64965.1015625, speed0, boarding inactive and six contributing/eligible vehicles; comparison guards pass. It adds no timer-onset validation.


## Minimum-wait consumer search boundary, 13 October 2026

The read-only Ghidra recognized-instruction scan in captures/platform-offset-scan-20261013-02 retains all 1748 scalar-0x38 matches. platform-minimum-consumer-scan-20261013.json filters direct nonstack float operands for FLD/FADD/FSUB/FCOMP/FMUL/FDIV and preserves leads and source hash. No such match falls in [00580000,005b0000), a bounded station/activity search range rather than a complete subsystem map. This does not exclude integer copies, adjusted pointer bases, indirect consumers or undisassembled code. Minimum-wait gameplay use remains unknown; do not label it ignored.

Selected retained sources resolve misleading same-offset references: 005a3941 at005a3fe3 copies service+34 to service+38 and then operates on the referenced station flags at+1e; 0058782c reads its service argument+38 into a local. These are not direct platform+38 float reads. Several other indexed float hits visibly use camera globals007c2a88/007c2aac; offset equality alone is not object identity.

The first scan attempt (platform-offset-scan-20261013-01) failed with a script source-bundle lookup error and supplies no scan evidence. A uniquely named script in an isolated script directory completed on the second attempt without error. Both logs and the successful source are retained; no executable, game asset or live process memory was modified.
