# Physical-object serialization surface

This checkpoint maps native save-writer inputs to runtime object ranges. It is a coverage aid for finding missing telemetry, not a new set of named physical quantities. Inventory remains1015; raw bytes are not counted as independently understood candidates.

Pass207 verifies7functions828instructions2404bytes; pass208 verifies6functions421instructions1193bytes; pass209 verifies3functions152instructions413bytes; pass210 verifies3functions257instructions700bytes. All exported instruction bytes match disk and live image. Some passes include previously exported callers; these totals must not be summed as unique-function coverage. Token labels below reuse save-token-map.json's verified table pairs.

The full SAV path invokes SaveWagon00639fb0 or SaveEngine005f2d65 for physical objects and SaveTrain0060d946 for registered trains. The installed activity ASV omits this branch, so its contents cannot test this schema. Writer vtable+50 receives an address and byte length; register arguments in assembly establish the ranges, whereas the decompiler omits several arguments.

| Writer / native block | Observed source operations |
|---|---|
| 0060d946 / SaveTrain404a4 | Raw train+10 lengthE2; IDs from objects referenced at+62,+66,+6A,+6E using target+50 (FFFFFFFF for null); controller+72 presence; inline consist label at[train+76]+8; service ID from[train+E6]+40 orFFFFFFFF |
| 00639fb0 / SaveWagon404a2 | Calls005fb240; raw wagon+7C length216; definition strings only for native type compared against80AA98, otherwise empty; target+50 ID for+AC; track-position helper005b3a03 on+128; target+40 ID for+1F8; target+50 ID for+240; null references emitFFFFFFFF |
| 005f2d65 / SaveEngine404a3 | Nested SaveWagon; raw engine+292 length36C; inline definition strings at[engine+29A]+8A8 and+8; helper006106e2 on four subobjects+4BA,+4FA,+53A,+57A |
| 005fb240 / SavePhysobj404a1 | Wraps005e2534 and closes block; no additional raw range in this wrapper |
| 005e2534 / SaveCollobj404a0 | Calls004feeca; maps callback+74 against two entries at7A09B0 or special pointers402BC6/401DBB to codes0/1/100/101, otherwiseFFFFFFFF; emits+78 and original+74 through writer methods. Callback purpose and +78 semantics remain unnamed |
| 004feeca / SaveStatic4049f | Object ID+50; flags+18 masked3FE3C0; float+14; integer+60; twelve floats+20..4C; body+5C presence; if present, raw body+4 length191 and track-position helper005b3a03 on body+12D |

All offsets and lengths in the table are hexadecimal except callback codes100/101. SaveEngine's range ends at5FE and overlaps its separately emitted subobject ranges. The body range ends at195. Raw copies contain pointers and internal fields; later IDs/indexes coexist with them. Do not treat copied bytes as a portable telemetry schema, assume that pointers survive reload, or infer that every raw byte has independent meaning.

Helper006106e2 writes60decimal bytes from subobject+4, then examines the pointer at subobject+3C. A null pointer emitsFFFFFFFF. A nonnull pointer must equal engine_definition+B0C+i*6C for i0..3; the helper emits that index, or fails when no match exists. The pointer itself is included in the preceding raw60bytes. This is explicit save-side reference encoding; the loader and actual restoration behavior have not been traced. Prior ELECTRIC-TRACTION-FINDINGS.md already notes a consumer of the+53A subobject with unresolved physical meaning.

The read-only `save-object-sources-paused-01` snapshot contains one physical player train and23vehicles, including two powered vehicle definitions. All57raw-range rereads,74reference-pointer rereads,8subobject-pointer rereads and the train-registry reread agree. Four subobject definition links on the lead map to0,1,2,3; four on the other powered vehicle are null and map toFFFFFFFF. No invalid nonnull link is observed. Pause remains1 and dayclock74360.5859375. These sequential checks do not prove atomicity, save consistency, or correct loader behavior.

No physical AI train is present in this snapshot; persistent AI service metadata from the earlier checkpoint is a different surface. No native writer/loader was invoked, no save produced, and no game-memory/UI/assets changed. The retained raw spans support subsequent field comparisons without repeating this capture. Next steps are loader reference reconstruction, semantic consumers for unnamed saved fields, and actual save/load or gameplay lifecycle validation. Existing position, velocity, train/service IDs and physics candidates should be enriched with this provenance rather than duplicated.
