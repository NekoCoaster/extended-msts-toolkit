# Collision-object callback and unnamed state

SaveCollobj005e2534 serializes callback binding car+74 and state car+78. Earlier SAVE-OBJECT-SURFACE-FINDINGS.md left both meanings open. This follow-up identifies a readable structured surface without assigning collision/damage labels to numeric state.

map_collision_callbacks.py verifies the two entries at7a09b0 and four five-byte stubs against disk/live PID33612, including repeated live reads. Save codes0/1 map403cd3->5e1414 and4035f3->5e143c;100/101 map402bc6->5e1428 and401dbb->5e1400. Codes are serializer encodings, not object state values. Pass274 exported zero functions because the stub addresses lacked function definitions; retained as negative evidence. Resolving the rel32 targets permitted pass275 to export allfour targets.

Targets5e1400/5e1414/5e1428 return zero without modifying object state. Target5e143c selects a context pointer, calls401aa0 (decompiler resolves5e17a0), then calls5e14dc, which computes the sum of squares of a three-float vector. A comparison against77138c selects behavior: the greater branch writes output bits3ca3d70a, selected object+78=2 and context+1c bits3c23d70a;the other branch writes output0 and context+1c bits3f4ccccd. Vector construction semantics, threshold units, callback invocation and physical interpretation remain unresolved. Do not infer an impact-speed threshold or damage event from this code alone.

Pass275:4functions76instructions220bytes;pass276:2functions72instructions198bytes. Selected exported bytes all match disk/live with no errors. This does not verify every caller or downstream function.

read_collision_callbacks.py retained45vehicle snapshot at paused73871.1953125:23player and22AI physical vehicles, all callback402bc6 and state5, zeroerrors or differing local rereads. Exact probe dependencies are copied into captures/collision-callback-paused-01. Current vehicles therefore select a return-zero target;this says nothing about other collision-system paths or whether this callback was invoked. State5 meaning and writers remain unknown. No collision was induced and no simulator control used.

One structured candidate retains binding and raw state together. Next distinguishing evidence is the initialization/other writer path for car+78 and the callback invocation contract, not another unchanged paused snapshot. Do not turn callback aliases into four independent telemetry quantities.
