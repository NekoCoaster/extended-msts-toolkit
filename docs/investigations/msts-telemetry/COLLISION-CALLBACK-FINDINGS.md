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
