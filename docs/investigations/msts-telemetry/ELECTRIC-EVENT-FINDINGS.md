# Electric event receiver discovery

This is read-only native tracing and a paused live routing/value snapshot. Audio playback, event consumption and event lifetimes are not yet validated. Receiver handles must not be exposed as stable identities across sessions.

## Routing

Electric producer005ee01f uses lead+4b6 and+25c as registry handles, not pointers. It calls005ef10a with ECX=handle, EDX=method slot0x82 and the event number on the stack. The wrapper resolves object=[registry+handle*8], class handle=[object], class=[registry+classHandle*8], method index=[class+64+slot*4], callback=[class+1064+index*4]. It then invokes the callback with ECX=object, EDX=event number. A null receiver or null callback returns0. The research probe only reads this route; it never executes a callback.

Live Acela at paused36164.390625 resolves handles6226 and6166 to objects56543476 and53935848. Both have class handle67. Slot0x82 selects index8/callback00533c4d. The two receiver roles are not yet independently identified as cab/exterior sound, so retain source offsets rather than inventing role names.

## Retained discrete events

00533c4d ORs an event bit into object+20 for event numbers below33, using shift(event-1)&31; otherwise it ORs object+24 using shift(event-33)&31. Ordinary IDs1..32 and33..64 therefore have separate masks. Native code does not range-check0 or values above64: these alias existing bits through the x86 shift mask. Do not treat arbitrary IDs as an unbounded event set.

These stores combine repeated occurrences into one bit. They contain neither timestamps, order nor occurrence counts. The clearing/consumer path remains untraced, so calling them an event log or inferring that every set bit is recent would be incorrect. Paused values for+4b6 receiver are12589056/12288; for+25c receiver12597252/0. This demonstrates readable retained masks, not per-event runtime validation.

Static electric producer branches include throttle change event0x10, signed reverser change0xf and train-brake change0x11, each guarded by retained globals/flags. Full event-name mapping and sampling loss remain open. Native paired sends to two receivers must not be mistaken for two independent user actions.

## Scalar values

005ef172 is the analogous two-argument method dispatcher. Actual scalar producer calls use method slot0x85, not0x83. Slot0x85 resolves index11/callback00533d3b, which copies the pointed value into object+28/+2c/+30 for scalar IDs1/2/3 respectively. Other IDs perform no store and still return1. All six scalar fields read0 in the paused idle Acela snapshot; nonzero transitions remain untested.

The electric producer initially forms scalar1 from throttle times native constant752274; scalar2 from current-source/definition+1da capped above at1 and scaled by that constant, with a lead+84 bit8 override to0; scalar3 begins from lead+47a. Calls to0040b948 occur on some paths before receiver dispatch and remain untraced. Therefore do not assume both receivers always receive identical raw throttle/current values or attach final physical units yet.

The initially inspected slot0x83 resolves00533ca0, which copies three words to object+58/+5c/+60 and sets object+1c bit0x10. It is not the scalar method used here. Its broader meaning is still unresolved; no position semantics are claimed from three adjacent values alone.

## Evidence and continuation

Pass112 verifies wrappers and shared brake propagation:425 instructions/1579 bytes. Pass113 verifies005dbcea:207/894; it emits brake-related events but supplies no direct electric traction-bit writer, leaving the gate discrepancy unresolved. Pass114 verifies callbacks00533c4d/00533ca0:56/154. Pass115 verifies00533d3b:29/78. All have zero disk/live instruction mismatches for PID7160.

`read_electric_event_routes.py` uses the exact-image Reader, player type guard, conservative handle/index bounds, immutable captures and context rechecks. Captures electric-event-routes-paused-01/-02 and electric-event-values-paused-01 preserve progressive probe versions. These probes are non-atomic, and research bounds are not native capacity claims. Next trace receiver consumers/clears,0040b948 and lifecycle, validate nonzero scalar/control transitions, and determine AI receiver availability before claiming general audio/event telemetry coverage.

## Broadcast helper and nonzero scalar validation

Pass116 traces0040b948 (48 instructions/159 bytes) and pass117 traces0040b870 (15/41), both with zero disk/live instruction mismatches. The helper begins at player train+62, advances via car+a8, and dispatches scalar IDs to each qualifying car's+4b6/+25c receiver handles. Its filter requires dword[car]==0xf. For engine-definition type2 it additionally calls0040bad4 and skips that car if the helper returns0. Other engine types pass this particular filter. Rejected cars are skipped by adding0x61 to the helper caller's return address, taking execution from0040b964 to0040b9c5. The previously decompiled unconditional body is therefore misleading.

After traversal,0040b948 changes its own return address using a table at0040b9e8, indexed by scalar ID minus1. IDs1/2/3 return to005eec06/005eecb7/005eed05 respectively, bypassing redundant-looking original sends in005ee01f. These are verified disk/live table values in electric-event-helper-table.json. The scale at752274 is100.0, also verified disk/live. The electric branch copies the provided scalar unchanged. A diesel-type branch for scalar2 divides by100, but register/pointer behavior in that branch needs separate review and runtime evidence; no diesel equivalence claim is made here.

At paused36178.3515625 after THROTTLE(3%), both lead receivers' scalar1 values are2.5. The paired traction snapshot has raw controller throttle0.025000000373, speed0, brake cylinder29.096672, current0 and force0. This validates scalar1 as throttle percentage for these two electric receivers in this installed build. Scalar2 and3 remain0 and gain no nonzero validation from this experiment. Returning to idle gives both scalar1 values0 at paused36193.43359375. The train is left paused, stationary, idle, forward, pantograph up and brakes applied.

The two event masks are identical across these separated snapshots, including after throttle changes. This does not prove that no events occurred or that clearing never runs; the snapshots cannot observe intervening set/clear cycles. No event counts or timing are inferred. Full consist broadcast behavior, rejected-car freshness, receiver clearing and AI applicability remain open.
