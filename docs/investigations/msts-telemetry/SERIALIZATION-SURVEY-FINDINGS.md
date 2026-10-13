# Save-state discovery entry points

This is a bounded survey of a previously unexamined surface, not a complete save schema and not new telemetry rows. Inventory remains1005. No save was created, loaded, overwritten or deleted; original assets remain unchanged.

## Installed evidence

The scan restricted to C:/MSTS finds zero .sav and56.asv files. This says nothing about files elsewhere. The preferred activity's evegrain.asv is46934bytes, SHA2560c6ac34f45c65ae00890d9efaa5552df8d844281e52f76a273a1e5c5e441d443. It begins with the32-byte header `SIMISA@@@@@@@@@@JINX0v0b______` plus CRLF.

`survey_asv_blocks.py` tests an explicit structural assumption: after that header, each top-level block has a32-bit token,32-bit payload length, then payload. The following four blocks consume the file exactly with no remainder:

| Offset | Native token | Verified token label | Payload bytes | End offset |
| ---: | --- | --- | ---: | ---: |
| 32 | 40495 | SaveHeader | 680 | 720 |
| 720 | 40496 | SaveTDBs | 35123 | 35851 |
| 35851 | 4049b | SaveTrItems | 100 | 35959 |
| 35959 | 404a6 | SaveActivity | 10967 | 46934 |

`map_save_tokens.py` checks25 Save-prefixed string-pointer/token pairs against disk and live memory; all match. Tokens include object/train/engine/wagon/physics, track database/items/owners, activity/services/events and controller labels. A name alone is not an extractable field or a supported serializer, so these are not added as25 telemetry candidates. Interior token payloads remain undecoded. Exact top-level partition is structural consistency, not proof of full format semantics or every variant.

## Native paths and the ASV/SAV distinction

Pass199 searched interior string suffix addresses and yielded no references. Corrected full-string references inpass200 lead to004a0157 for `%s.sav` and0064b5fe for `.asv`. These reference lists are navigation, not byte/semantic validation.

Pass201 verifies7functions1837instructions8361bytes, all disk/live equal. 004a0157 constructs the activity/explore save basename and timestamp, uses a saves/route path, tries up to100 suffix variants, and calls0049f34f withEDX=1. No routine was invoked by the research. 0064b5fe strips an existing extension and appends.asv. Its caller0064b537 then reaches0049f33a through a thunk; this wrapper explicitly clearsEDX before calling0049f34f.

Pass202 verifies3functions530instructions1737bytes, all disk/live equal. The common0049f34f routine takes the second argument as a scope gate. It calls header routine0049f73c. When the gate is nonzero it emits SaveObj4049e and walks physical-object/train registries, including calls00639fb0,005f2d65 and0060d946. It then handles SaveTDBs40496, SaveTDB40497 and optional SaveRDB40498, and calls shared track/activity helpers. Additional tail routines00588d64/0048bb7c are also gated on the nonzero argument.

Thus the installed activity-side ASV and gameplay SAV use a shared serialization path with different scope; the ASV must not be mistaken for a complete saved gameplay instance. Its absence of a top-level SaveObj block agrees with the zero-gate path. This is native control-flow plus file-structure evidence, not a newly generated ASV/SAV comparison. Ghidra's inherited TokenReader/NextToken names on the write-side interface are misleading type labels; do not infer read-versus-write behavior from those labels alone.

## Concrete next work

Trace0049f73c's header fields and then one subsystem serializer against already inventoried live fields, preserving field order, type and reference encoding. The common path's specific object callbacks and005cf5f2/005b740d/005b6f2d/00591aa6 provide targeted leads. Generic token/string helpers should not trigger broad caller exports. Decode a bounded payload only after the writer establishes its schema. Identify genuinely new fields and unavailable/derived values, rather than count known field copies again.

Full save/load transitions, object-reference fixups, replay/reload identity, coverage across locomotive types and a comprehensive serializer schema remain open. No claim that all save-persisted fields are current/live or semantically independent is made. No UI actions occurred in this survey; the game was not resumed.
