# Collision-object callback and unnamed state

SaveCollobj005e2534 serializes callback binding car+74 and state car+78. Earlier SAVE-OBJECT-SURFACE-FINDINGS.md left both meanings open. This follow-up identifies a readable structured surface without assigning collision/damage labels to numeric state.

map_collision_callbacks.py verifies the two entries at7a09b0 and four five-byte stubs against disk/live PID33612, including repeated live reads. Save codes0/1 map403cd3->5e1414 and4035f3->5e143c;100/101 map402bc6->5e1428 and401dbb->5e1400. Codes are serializer encodings, not object state values. Pass274 exported zero functions because the stub addresses lacked function definitions; retained as negative evidence. Resolving the rel32 targets permitted pass275 to export allfour targets.

Targets5e1400/5e1414/5e1428 return zero without modifying object state. Target5e143c selects a context pointer, calls401aa0 (decompiler resolves5e17a0), then calls5e14dc, which computes the sum of squares of a three-float vector. A comparison against77138c selects behavior: the greater branch writes output bits3ca3d70a, selected object+78=2 and context+1c bits3c23d70a;the other branch writes output0 and context+1c bits3f4ccccd. Vector construction semantics, threshold units, callback invocation and physical interpretation remain unresolved. Do not infer an impact-speed threshold or damage event from this code alone.

Pass275:4functions76instructions220bytes;pass276:2functions72instructions198bytes. Selected exported bytes all match disk/live with no errors. This does not verify every caller or downstream function.

read_collision_callbacks.py retained45vehicle snapshot at paused73871.1953125:23player and22AI physical vehicles, all callback402bc6 and state5, zeroerrors or differing local rereads. Exact probe dependencies are copied into captures/collision-callback-paused-01. Current vehicles therefore select a return-zero target;this says nothing about other collision-system paths or whether this callback was invoked. State5 meaning and writers remain unknown. No collision was induced and no simulator control used.

One structured candidate retains binding and raw state together. Next distinguishing evidence is the initialization/other writer path for car+78 and the callback invocation contract, not another unchanged paused snapshot. Do not turn callback aliases into four independent telemetry quantities.


## Native flags name, initialization and load reconstruction

Pass277 follows references to the callback stubs/table:5functions1923instructions6695bytes all match disk/live PID33612,zeroerrors. map_collision_tokens.py independently verifies UTF16 labels and token-table pairs: CollideFlags=40069 at794dd0,string76749c;CollideFunction=4006a at794dd8,string767474. Parser005e1ef3 reads token40069 directly into object+78 then ORs0x200. Token4006a reads an index: when global7be0f8 is zero it bounds the index to0/1 and resolves the callback table;otherwise it stores the raw index at+74. Thus the field is a collision-flags bitmask, not an enumerated status. Do not dereference+74 without runtime/build/mode validation.

Initializer005fb0fd clears flags+78;under global7be0f8==0 it creates/stores body+5c and selects callback402bc6,otherwise body+5c is null. This is initialization evidence,not proof that no later writer changes flags. Current snapshot5 means bits0x1 and0x4 are set;their complete individual semantics remain unresolved.

Consumer005df360 repeats pair-processing branches: bit0x2 excludes a candidate; masks0x78 on both objects and0x200 on either participate in additional eligibility conditions. The special second table callback and global80a9ac can affect those conditions. Another branch tests(flags&0x81)==0,sets0x80,and builds a0x62-stride record carrying object/body/callback fields. These are local branch facts,not a complete collision eligibility formula,contact history or damage interpretation. No labels are assigned to individual bits without their full writer/consumer context.

Loader005e2411 reads serialized callback code,stored flags and original pointer,then clears the pointer and rebuilds it from table codes0/1 or special100/101;FFFFFFFF and unrecognized codes leave it null. It restores the stored flags at+78. This closes the previously untraced save-side callback reconstruction path statically;actual reload of this field and full serialization restoration remain unvalidated. Raw pointer preservation must not be used as reload identity.

The existing structured candidate is renamed to native collision flags/binding without changing its ID or increasing the count. Its previous unnamed-state observations remain historical evidence. The callback invocation contract,full bit dictionary and live flag transitions remain open.


## Point-velocity formula and threshold

Pass278 verifies helpers005e1561 (vector subtraction),005e15b5 (cross product) and005e150d (addition):3functions108instructions292bytes all match disk/live33612. Combined with previously verified005e17a0 assembly, the returned vector is body[88] + body[94] cross (point - body[30]). Existing body telemetry mappings identify linear velocity,angular velocity and position respectively;units inherit those mappings. This is point velocity for one selected body,not relative closing speed between two bodies. Intermediate float stores/x87 arithmetic preclude assuming arbitrary host arithmetic is byte-exact.

map_collision_point_velocity.py verifies stub401aa0->5e17a0 and constant77138c=49.0 against disk/live. Callback005e143c supplies context+20 as point. A zero selector takes the body pointer from context+10 and writes flags2 to object atcontext+4;nonzero selector takes body context+c and writes object context+8. The body used for the speed calculation and the object receiving flags are opposite entries in the pair record. Pair construction005df360 stores each object's body at+c/+10,corroborating this distinction. It is incorrect to label the written object's own speed as the threshold input.

For finite inputs,the branch uses squared point speed>49,corresponding to magnitude>7 in inherited m/s units. The other branch also covers unordered x87 comparisons,so it must not be paraphrased as exclusively speed<=7 for arbitrary corrupt/nonfinite input. Greater branch writes output approximately0.02 and context+1c approximately0.01;other branch writes0 and approximately0.8. Those scalar roles remain unnamed;do not label restitution/friction without the consumer contract.

This resolves the vector and threshold arithmetic,not collision invocation,contact point validity,world-frame agreement,relative impact velocity or a damage threshold. Current vehicles use callback402bc6 rather than this table callback. No new telemetry candidate is added solely for an inactive helper formula. The underlying body position/linear/angular velocity fields gain consumer evidence. Collision pair-buffer lifecycle and downstream callback invocation remain discovery leads.


## Collision work-buffer lifecycle

Pass279 follows buffer globals80a76c(pointer),80a770(count/current construction index),80a774(capacity):6functions2076instructions7741bytes match disk/live33612. Initializer005f3f40 allocates0x5fb40bytes for4000records of0x62bytes and zeroes them. Builder005f47e8 resets count to0 before rebuilding;it clears object flag0x80 and performs additional mask0x78/0x100/0x4/0x1 state transitions before calling pair construction over four collections. Returned count is therefore pass-local work state,not cumulative collision history. Some work records include a null opposite body;pair count cannot be assumed to mean train-to-train contacts.

005def40 advances the construction index and copies object/body/callback bindings into the next record;capacity can grow by3/2. 005df0b8 swaps body and callback entries at+c/+10 and+14/+18 without swapping object entries+4/+8. Pair-side mapping described in the preceding section is valid at construction,but cannot be assumed invariant through all processing stages. Destructor005f49f9 frees/clears the buffer and capacity at final reference release;count is not explicitly reset there,so a null buffer must override any stale nonzero count for availability.

Pass280:4functions433instructions1523bytes match disk/live. Caller00629dbc gates generation on global7a2df8,stores the returned pointer/count at its own+74/+78 (not vehicle collision fields),then fills per-record state and scalar+1c before calling005f952e. A separate7a2dfc branch can divert processing. This establishes post-builder mutation and phase dependence;callback invocation/solver lifecycle remain untraced. Identical numeric offsets on different object classes do not identify the same field.

read_collision_buffer.py records a bounded read-only snapshot atpaused73871.1953125:base56223236,count0,capacity4000,header rereadstable. Zero records were read;record stability is vacuous here,not positive record validation. Probe caps reads at128records,checks count/capacity and header reread,and does not dereference record pointers. Retained exact probe/read_live copies are in captures/collision-buffer-paused-01. A populated fixture and registry-qualified object links remain required before publishing these as contacts. Empty scratch state does not prove absence of prior or current physical contact.

Added one structured work-buffer candidate retaining pointer/count/capacity and bounded raw records with partial object/body/callback fields. This exposes potentially useful transient data without naming it an event stream. Unknown record fields,validity,swaps,allocation changes and processing-phase races are explicit.


## Post-builder record flags and reference caveat

Pass281 verifies005f952e,42instructions108bytes,disk/live33612equal. This routine traverses caller+74 for caller+78 records,stride0x62,and sets record dword0 bit1 when caller+44==1,otherwise clears that bit. It makes no calls and does not invoke record callbacks. The post-builder path traced so far therefore establishes record flag mutation,not contact response or callback execution. Record flags must not be confused with per-vehicle CollideFlags+78.

Pass282 caller navigation found a reference from4038c3 to629dbc,typed UNCONDITIONAL_CALL in the stored analysis database. The exact five disk/live bytes are e9f4642200: JMP rel32 to629dbc. map_collision_generation_stub.py verifies these bytes and the pointer at773298 to4038c3. Pass284 finds only that data reference,no caller function. This is an indirect-entry lead,not proof of its caller or execution timing.

Pass283 attempted a small disassembly range starting4038b8,which was not an established instruction boundary. It produced misaligned instructions and is retained only as failed navigation evidence;do not use its listing for semantics. The independently verified exact stub supersedes it. Byte equality alone does not validate a stored reference type or instruction boundary. Next useful work should identify the owning dispatch table and its consumer,or acquire populated runtime records;repeating empty paused buffers would not establish invocation.

## 2026-10-10: populated scratch buffer and dispatch owner

Current PID12888 normal Tokyo introductory ride yields25records/capacity4000 at44656.94921875,unpaused,with full header/record rereads equal and no truncation. `captures/itr-moving-collision-buffer-20261010-01` preserves exact probe/source and raw records. Follow-up object[80aa1c]=51881064 has vtable773280;slot18at773298 is4038c3,whose exact five bytes JMP629dbc. Slot/stub bytes equal disk/live. Object74/78 equals global buffer54721868/count25,with stable object/vtable reread. This resolves the dispatch table owner to the shared simulation object,not the exact invocation cadence or callback execution.

A subsequent vehicle registry has one11-car player train. None of the25record object pairs joins those car addresses;all50body slots are null. Callbacks are401dbb and403cd3. These are positive populated scratch records,not demonstrated train contacts. Unmatched objects must not be called scenery/terrain without object-type evidence,and separate observation times limit joins. No collision was induced or native callback invoked. read_collision_buffer still uses bounded raw reads.

The new collision-callbacks-20261010 export produced zero functions at undecorated stubs,duplicating historical pass274's known navigation limitation;it adds no semantic evidence and was not retried. Existing mapped targets were reused. The actual new evidence is the populated buffer and owning shared-simulation instance. Runtime record validity,type ownership and downstream invocation remain open.


## Collision object header correction, 2026-10-10

The immutable objects.json in captures/collision-object-types-20261010-01 incorrectly names object+0 `vtable`. Existing dispatcher 004a041e evidence establishes a class-table index instead. collision-object-header-review-20261010.json preserves the source hash and corrected offline interpretation: class index6, self table index8167, object ID2823, null body, callback403cd3, flags384. Raw +8/+c remain unnamed. The three observed records share this nonnull object. No pointer dereference of value6 was attempted.

A bounded follow-up captures/collision-class-six-20261010-01/class.json resolves class6 through the native table to class object117690628, method0x14 slot29, target005e234d. Its 16 live bytes 558bec51894dfcb80b0004008be55dc3 encode a constant return of0x4000b. Metadata rereads agree. This is a read-only class-method lead; target disk comparison and native type/save mapping are still required before assigning a semantic class name. The follow-up does not prove the prior object remained alive, nor does it establish terrain/scenery contacts or callback execution. Current simulator observation was unpaused at44904.57421875 (12:28:24), rather than the historical midnight fixture.

The subsequent collision-class-20261010 export verifies005e234d and registration005e1ccd:173instructions/566bytes match current disk/live. Registration global80a3a0 requests size0x7c and binds method0x14 to the constant-return target. It also binds parser method0xd to005e1ef3 and copy method0x8f to005e235d. The latter first calls generic006912c0 and, on success, resolves the source through object-table index and copies +78/+74. collision-class-methods-20261010 verifies117instructions/328bytes disk/live. Parser005e1ef3 was already interpreted in pass277; this is current-build revalidation, not new parser semantics. Class6 therefore has native kind4000b and collision-field behavior, but no world-role/scenery/terrain label is assigned. The newer checks supersede the target-byte-verification gap above.

## Callback consumer contract, 2026-10-10

Reusing pass160b rather than re-exporting reveals0062a2be as a concrete callback consumer. captures/collision-consumer-native-20261010-01 retains exact source/hash provenance;604instructions/2658bytes match current disk/live with no errors. The shared simulation vtable slot+10 at773290 points to402de2, whose five exact disk/live bytes JMP0062a2be. This establishes dispatch binding, not a live execution trace or complete caller chain.

Assembly0062a38f..0062a3e3 reads record+c/+10 and skips the record if both are null or both are nonnull. Exactly one nonnull body is required on this path. A zeroed temporary0x195-byte body substitutes for the absent side, with its position copied from record+20/+24/+28. Calls at0062a472/49c/4e8/542/55a pass ECX=record, EDX=0 for callback+14 or1 for callback+18, and a stack pointer to the selected body's +c8 field (the temporary field for the absent side). Thus the previously unnamed callback output argument aliases the body inverse-mass field on this path. A return-zero callback does not itself change that field. No other callback ABI or universal output meaning is inferred.

The two captured populated snapshots have both body fields null in every sampled record. Under this consumer's verified predicate those sampled values would be skipped; they do not establish response or callback execution. Asynchronous sampling cannot exclude a different state at invocation. The broader body-body consumer, dispatch invocation order, and physical interpretation of record+1c remain unresolved. This closes the existence and argument-layout question for one native consumer, not runtime collision validation.

## Rebuild and consumer order, 2026-10-10

005f95a5 explicitly zeroes simulation+74/+78, calls vtable+18 (00629dbc builder), conditionally calls005f8fc9 when simulation+44 is nonzero, calls vtable+1c (00629f5d), then vtable+10 (0062a2be). collision-dispatch-order-20261010 verifies210instructions/662bytes disk/live. captures/collision-dispatch-order-20261010-01/dispatch.json verifies all four relevant table entries and JMP stubs in current PID12888, with matching simulation vtable. The intervening optional helper means snapshots cannot be assigned a processing phase solely from a nonzero count.

00629f5d is an aggregate/preparation stage, not a callback invoker. It first sets body+f2 bit10 and resets body+f3 byte,+f4 byte,+f5 word,+f7 word. For each nonnull body at record+c/+10 it increments +f3 and adds record word40 to+f5, word42 to+f7, byte44 to+f4. Both-nonnull records clear body+f2 bit10 on both sides. These are bounded-width pass accumulators, not lifetime contact counts; overflow and duplicate references must be considered. Later branches use these accumulators in body resting-state decisions. Full threshold/vector semantics remain open. collision-pair-consumer-20261010 verifies233instructions/865bytes with zero disk/live mismatches/errors.

This establishes static order and raw aggregate producers without proving runtime callback execution or body-body response. The existing pass162/005f6d1e is a separate concrete callback consumer that accepts two bodies (or substitutes for one absent body) and rejects both-null;its caller/reachability and current bytes remain the next bounded question. No new candidate has been added for the newly traced body accumulators pending extraction and applicability review.

## Two-body-capable response path, 2026-10-10

collision-two-body-20261010 verifies005f6d1e, its thunk00402c43 and dispatcher005f696f:627instructions/2631bytes disk/live exact. Dispatcher tests record dword0 bit1 (mask0x1): clear selects005f6d1e, set selects005f6998. Unlike0062a2be,005f6d1e accepts two nonnull bodies and also substitutes a temporary for one missing body;both-null returns before either callback. It marks each existing body dword+4 bit0x2 before invoking callbacks. ECX is the record,EDX0/1 selects the side,stack output points to body+c8 (or temporary inverse mass). This confirms the argument layout on a second path without assigning a universal physical interpretation to callback output.

collision-response-dispatch-20261010 verifies7functions/470instructions/1502bytes,including overlaps with earlier verified caller/dispatcher;totals are not unique coverage. Optional005f8fc9 in the established005f95a5 sequence traverses simulation74/78 at stride62 and calls005f653d(record,simulation40). Only return0 calls005f696f;return2 selects005f661a instead. Therefore the two-body-capable path is statically reachable before00629f5d aggregate preparation and0062a2be one-body processing,subject to simulation44!=0,classifier return0,and record mask1 clear. The new exported005f91ff provides an additional bounded-repeat dispatch loop,whose parent caller remains untraced.

No runtime invocation trace is claimed. Classifier005f653d and alternate005f6998/005f661a branches still require interpretation;raw record flags6 alone are insufficient to infer response because body presence and the classifier also gate work. These findings supersede the earlier untraced two-body reachability note. No collision was induced, native routine called, or process memory modified.

## Response classifier arithmetic, 2026-10-10

005f653d computes point velocity for body at record+c and body at record+10 using005e17a0 at point record+20. Null bodies substitute vector83db48. Verified helper005f9b0e subtracts ECX-vector minus EDX-vector,so the difference is velocity(body+c)-velocity(body+10). Helper005f9ce9 dots that difference with record+2c;the float32 result is stored at record+3c. Direction-vector normalization/orientation and contact-point validity are not established here,so this is a projected relative point-velocity scalar,not a universal impact-speed measurement.

For finite scalar s and threshold t: return1 if s>t;otherwise return0 if s<-t;otherwise return2. With finite nonnegative t this gives negative/outside,central,and positive/outside regions,including equality in return2. x87 unordered comparisons yield return2;do not silently treat nonfinite data as a valid central state. The caller005f8fc9 routes return0 to005f696f,return2 to005f661a,and does not take either branch for return1. Record mask1 then chooses the005f6d1e vs005f6998 response variant. No velocity-based branch is proof of physical collision by itself.

collision-classifier-20261010 verifies3functions/129instructions/359bytes disk/live exact. captures/collision-classifier-context-20261010-01 observes threshold simulation+40=0.05000000074505806,mode+44=2,and fallback vector83db48=(0,0,0) in PID12888. The separate observation is not atomic with previous records and does not prove execution. Both-null records with finite direction and observed zero fallback would classify centrally;the actual alternate return2 consumer remains untraced. The constant-return collision callbacks and this classifier are distinct functions.

## Alternate response null-body guards, 2026-10-10

collision-alternate-response-20261010 verifies005f661a (classifier return2) and005f6998 (record mask1 set):422instructions/1755bytes disk/live exact. Both read record+c/+10 and return before record callback calls when both are null. Otherwise each calls+14/+18 with the established record/side/output contract,using a temporary for a missing body. This closes the immediate alternate-branch question: all three005f8fc9 response variants inspected so far require at least one body to reach the stored callbacks;the later0062a2be path requires exactly one.

Accordingly the all-null samples are populated work records without demonstrated body response. This is a code predicate applied to sampled values,not proof that they remained null during processing or that no other collision subsystem acted. Full response arithmetic and physical units for remaining scalars are not claimed. No further identical empty-body capture is needed to establish these already verified guards.

## Body accumulator access baseline, 2026-10-10

read_collision_body_accumulators.py captures body+f3/f4 bytes and+f5/f7 words through guarded train/car/body traversal. collision-body-accumulators-20261010-01 has100samples,1100body rows,11unique player cars,no read errors or failed local reread/ownership checks. All four accumulators remain0;body+f2 remains16 over10simulation seconds. No nonplayer rows were present. Added one structured raw candidate car.collision_pass_accumulators with reset semantics,modular overflow,per-side counting and incomplete applicability explicitly retained. This is access validation only,not nonzero contact behavior.
