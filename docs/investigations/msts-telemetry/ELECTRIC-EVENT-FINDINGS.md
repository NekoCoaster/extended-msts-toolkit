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

## Receiver class and lifecycle investigation

`event-receiver-references/references.tsv` locates callback registration00533916. Pass118 traces its class handle global7c2e54 and object-size argument0x74. Registered methods include slot8->00533b8f,9->00533c22,0x82->00533c4d,0x83->00533ca0,0x84->00533ce7,0x85->00533d3b and0x86->00533d89. This identifies callbacks without scanning unrelated classes.

Pass119 shows00533b8f initializes scalar+28/+2c/+30 to0, several other fields to0, +4c to float1000000, +54 to1 and+70 to0, then delegates slot8 through the handle at object+4. It does not directly clear+20/+24 in its inspected body.00533c22 delegates slot9 through that same handle.00533d89 stores its argument at+70; its meaning remains unidentified.00533c3d returns0x40042. These facts do not establish the inherited initialization or destruction behavior; parent dispatch remains untraced.

`event-class-references/references.tsv` links class use to005425b9. Pass120 traces allocation of each receiver's definition+10, per-stream state+14 (definition stream count at+10,28 bytes per runtime stream versus32 bytes per definition stream), and indexed trigger state+18 (definition+0c count times4). This is lifecycle evidence for further discovery, not a validated stream/state telemetry schema.

Pass121 traces initialization00542a4e. Trigger type0xb schedules state values using GetTickCount plus selected seconds times1000. Type0xc initializes other trigger slots, including counters. These use Windows tick time, not the already mapped simulation clock; pause behavior and wraparound handling in the consumer are untested. Definition/runtime arrays and random-selection behavior still need bounds and format validation before generalized live extraction.

005414b8 clears receiver+1c bit0x2. Its optional0053af3e call is gated by global7c32d0. Pass122 traces this wrapper to0053af56; pass123 shows Win32 tree-view message updates for receiver/stream entries. This is a debug UI path, **not** the event mask consumer. It must not be used to infer clearing cadence or sound playback. `event-update-references/references.tsv` records incoming references for the next targeted search.

Pass118:149 instructions/494 bytes;119:118/348;120:283/1173;121:358/1154;122:10/24;123:310/1452. All inspected instruction spans match disk/live PID7160. The game remained paused during this static investigation. No event clearing, new runtime transition or complete audio lifecycle is claimed. The five receiver inventory candidates are retained with the same unresolved lifetime caveat.

## Processing and selective mask clearing resolved

Pass124 traces0053f153 (2028 instructions/6988 bytes, zero disk/live instruction mismatches). It traverses the receiver list through `[7c32f0]+14a`, obtains GetTickCount once for the processing pass, examines stream/trigger definitions and conditionally dispatches trigger actions. Global7c32cc can skip the entire function body. Receiver+1c bit0x200 selects a different teardown-related path and skips the normal final updates described below. Per-stream interlocked guards can skip processing of individual streams.

At00540b06 onward, the normal final path clears dirty bits0x10/0x20, copies+34 to+48 and+38 to+4c, copies scalar1/2/3 from+28/+2c/+30 into previous-value fields+3c/+40/+44, and stores the pass's Windows tick at+50. It then clears only accumulated event-mask bits: receiver+20 &= ~local_mask_low and+24 &= ~local_mask_high. This is not an unconditional reset of either event word and not an event history.

For enabled discrete trigger type0, the tested event bit contributes to the clear mask when present, even if the action pointer is null; callbacks require a non-null action. Disabled discrete triggers also contribute clear bits. Assembly at0053fe3d subtracts3 for the disabled upper-word case, whereas enabled upper-word handling subtracts0x21. This installed-code discrepancy is real in the compared instructions and is not normalized away in the findings. Trigger selection, stream locking and this discrepancy can affect which bits remain. A set bit is therefore not proof of a recent or successfully played event, and absence is not proof that no event occurred between samples.

Type5/6 threshold triggers compare previous scalar1+3c and current+28 for upward/downward crossings;7/8 use scalar2+40/+2c;9/10 use scalar3+44/+30. These previous values refer to receiver processing, not necessarily the previous physics update or external sample. Type0xb compares the stored unsigned tick deadline against the current Windows tick; wraparound behavior is not claimed safe. Type0xc uses elapsed unsigned tick difference from receiver+50 in its accumulation.

Two read-only paused captures (`electric-event-processing-paused-01` and`-02`) keep simulation time36193.43359375 and pause1 unchanged, while both receivers' last-processing ticks advance from370735578 to370748359, a12781ms difference. Both contexts are stable; previous/current scalar values stay0, and the event masks remain unchanged. This confirms receiver processing can continue while this game is paused. It does not measure processing cadence or demonstrate individual set/clear transitions. Receiver flags are1024 and1282, both with0x200 clear.

Four additional candidates preserve the three previous scalar values and the last-processing Windows tick. Full trigger/action semantics, stream playback state, direct event set/clear timing, receiver removal and AI applicability remain open. The last-processing timestamp is a wrapping uint32 Windows uptime value, not a simulation timestamp or wall-clock date.
