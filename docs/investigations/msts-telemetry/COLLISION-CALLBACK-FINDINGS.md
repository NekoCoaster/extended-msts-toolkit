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
