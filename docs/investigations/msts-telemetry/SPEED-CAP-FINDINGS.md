# Effective service speed-cap selection

Independent research checkpoint; no NEMT integration or candidate prioritization.

Native assembly `pass38/005a33af.asm` writes service+0x220 using this ordered selection:

1. Start with float [0x809878] if its raw sign bit is clear; otherwise use float [[0x809b48]+0x64].
2. If service flags contain 0x20, reduce by float [[0x809b48]+0x5c] when smaller.
3. If service flags contain 0x10 and service+0x224 has a clear sign bit, reduce by +0x224 when smaller.
4. If service+0x22c has a clear sign bit, reduce by +0x22c when smaller.
5. If service+0x228 has a clear sign bit, reduce by +0x228 when smaller.

Zero is eligible; testing strictly positive values would be incorrect. These are raw sign-bit tests, including the distinction between positive and negative zero. The independent reader rejects non-finite inputs rather than claiming to reproduce x87 unordered comparisons. +0x22c already has signal-profile producer evidence; producers and exact meanings for +0x224/+0x228 remain unresolved. Do not label them permanent/temporary restrictions yet.

`read_speed_caps.py --pid 7160 --name speed-caps-paused-01` captured one stable paused snapshot at simulation 74525.53125. Global override was -1; fallback 26.822399139404297, conditional flag20 cap 6.705599784851074. All three services had flags 20 decimal (0x14), so the flag20 cap was NOT eligible. The final cap matched the independently reproduced result for all three:

| Service | Update gate | +0x220 = +0x224 (m/s) | mph equivalent |
| --- | --- | --- | --- |
| Player 0 | 1 | 17.88159942626953 | 40 |
| AI 2 | 0 | 15.64639949798584 | 35 |
| AI 3 | 1 | 13.411199569702148 | 30 |

All +0x228/+0x22c values were -1. This confirms the current selection and disabled-sentinel path, not each branch or a runtime transition. The inactive service retains its cap; numerical validity does not establish operational freshness. Effective cap is separate from driver target speed and actual speed. No game state was modified.

Byte validation: pass38, 8 functions / 1,711 instructions / 7,415 bytes; pass39, 4 functions / 1,233 instructions / 5,281 bytes. All exported bytes matched both installed disk and live memory, with no read errors. Coverage is limited to exported instructions.

`pass39/005b01b4` builds a direction-dependent forward/backward profile, calls 005b0866 while traversing nodes, and selects shared scratch buffers 0x809f48/0x809f08 through 0x809f00. Absolute xrefs to player+0x224/+0x228 yielded no direct producers; these are likely accessed through a service pointer. Next inspect 005b0866 and its speed-post handling, and find service-relative writes. The speedpost serialization conditions established in TRACK-ITEM-FINDINGS.md do not yet prove speed units or train-type applicability.

Inventory remains 750 entries: this checkpoint refines existing effective-cap evidence without prematurely adding named restriction fields. Raw snapshot and script hashes are under captures/speed-caps-paused-01. This checkpoint is local and not yet published to draft PR #9.

## Follow-up: posted restrictions and applicability

The above 750-entry count describes the first checkpoint. Follow-up adds two service candidates (+0x224 and +0x228), bringing the inventory to 752. These changes remain local pending publication.

The proposed signal-profile route was ruled out: 005b0866 traverses node item pointers, but its consumer 005b09fd handles kinds 0 (signals) and 3 (platforms), not kind 8 speedposts. Do not describe that profile as a list of all posted restrictions.

The actual speedpost consumer is 004f5862. Assembly establishes:

- Processing requires stack argument +8 equal to 1. The exact event-name meaning is not yet assigned.
- Direction is gated using a dot product (004f9817) of an item direction vector with the service track record's vector at record+0x3c. Nonnegative speed uses service+0x4c; negative speed uses +0xb4 and inverts the sign result. With no linked world object (item+8 zero), the item angle+0x30 constructs the vector; otherwise the linked object vector at +0x38 is used. This is more than a simple track-node direction comparison.
- Flag0x100 chooses float32 0.44704, consistent with mph-to-m/s; otherwise float32 0.27777, the game's approximate km/h-to-m/s multiplier. Preserve the native approximation when reproducing values.
- Low-three-bit subtype 2 uses unsigned byte item+0x2a, converted by 004f5cf1 (integer-to-float), multiplied by that factor. It calls 004faf30, writes service+0x224 and sets service flag0x10. Subtype3 calls004faf90, writes -1 and clears flag0x10.
- For nonzero subtypes, applicability requires item flag0x80 OR (item0x20 AND service0x2) OR (item0x40 AND service0x4). Freight/passenger names for service bits are not yet independently established; retain the exact bit relations.
- Subtype4 sets service flag0x20 (004faf70); subtype5 clears it (004fafc0). This activates/deactivates the extra route cap already traced by005a33af. Do not assign a zone name solely from numeric subtype.
- Subtype0 with item flag0x8 converts the same byte and calls004faf10 to write service+0x228. It bypasses the nonzero-subtype train-class gate. The float payload at item+0x2c is not read by this consumer.

Service+0x228 also has initialization producers:0058aa22 and005addfe copy a positive configuration value at their input+0x68 through004faf10. Therefore it is not safely described as exclusively a speedpost or temporary cap. The separate004faee4 setter writes+0x228 and resets+0x22c/+0x24c to-1, but no direct caller was found in the current export. No inference of dead code from absence of direct xrefs.

Service constructor005a31d4 initializes+0x224/+0x228/+0x22c to-1. A false lead005db5f0 writes identical offsets in a locomotive-system object, not a service; excluded. Offset equality alone is insufficient type evidence.

Validation: passes40/41/42/43/44/45/46 respectively checked 547/368/277/32/43/223/1753 instructions and 1889/1198/1175/138/122/700/6856 bytes against installed disk and live process. All matched with zero errors. No runtime crossing test has yet established these setter transitions. Existing paused snapshot supports retained values and final selection only. Next trace subtype naming/service class bits, inspect crossing/init callers, and validate a posted-limit transition during ordinary gameplay.

## Service class and initialization follow-up

Native service initialization005a5eb1 sets bit0x2 and clears0x4, then scans configured vehicles. If any resolved vehicle definition has byte+0x88 equal to2, it clears0x2 and sets0x4. Parser00614c8e maps token0x40138 to definition type2 and0x40139 to type3. Native token-table entries at795448/795450 point to strings Freight/Carriage respectively. Thus bit0x4 denotes freight detected at initialization; bit0x2 denotes the default non-freight class. It does NOT prove passenger occupancy or even the presence of a carriage: a locomotive-only consist also follows the default path. Reclassification after coupling changes is untested.

Speedpost flag0x40 therefore applies to the freight class;0x20 applies to the default non-freight class;0x80 admits either. These are conditions in the traced consumer, not a claim that every bit combination is valid in the editor.

`probe_service_class.py --pid 7160 --name service-class-paused-01` verified the paused player's physical consist: two type1 engines and21 type2 freight wagons; service class bits were4, agreeing with the initialization rule. Both token-table entries and their strings matched live memory to disk. Both AIs lack physical cars at this checkpoint, so the runtime car comparison does not cover them. Snapshot time remained stable and paused; no writes or remote calls.

Initialization005a67af calls005a6cf4. That function saves the two0x68-byte service track records, searches backward across track nodes for a subtype2 speedpost, temporarily sets service speed to+1 for the direction-dependent consumer, restores speed, and later restores both track records. It stops the local search when bit0x10 is established and bounds traversal by a distance threshold. Therefore an initialized posted cap need not represent a crossing observed during the capture. Native internal temporary changes are evidence from code; the research probe never invokes this function.

The ordinary dispatcher005bafc0 also invokes004f5862 from tracked item/service interactions. It computes a state argument using stored distances and service+0x128; naming its exact entry/overlap/exit semantics still requires tracing the record producer. Other dispatched item kinds include pickup, hazard, crossing and sound regions, which offer concrete next research entry points004dcc7f/004d3a19/004d7e0c/004ef178.

Pass47:11 functions,1365 instructions,5309 bytes; pass50:2 functions,3454 instructions,12947 bytes. All exported instruction bytes match disk and live memory. Pass48/49 returned no functions because the strings are reached through the token table; raw pointer/token lookup led to pass50. The decompiled serializer006171f8 compares a byte with wide token constants and must not be used to infer a working inverse mapping; the parser's assembly provides the mapping above.

Inventory stays752; existing flags and cap metadata are refined. Outstanding: actual crossing transitions, non-freight runtime consist, post-coupling class refresh, subtype names for4/5, exact dispatcher event states, and speed restriction reset semantics. Current local checkpoint has not yet been published to PR9.

Publication note: this report and its standalone probes are included in the current research-branch checkpoint. Earlier local-only notes above describe the stages before publication. Raw captures/native exports remain local and are listed in local-evidence-manifest.json.
