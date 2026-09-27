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
