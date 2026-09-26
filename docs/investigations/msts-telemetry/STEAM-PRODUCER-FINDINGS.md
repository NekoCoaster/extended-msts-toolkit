# Steam producer tracing checkpoint

The first destination-offset scan (`TelemetrySteamWrites.java`, `steam-writer-scan/steam-offset-writes.tsv`) returned configuration writes, not the runtime steam producers. It only tests literal destination displacements and is not an exhaustive writer search. Runtime functions commonly form an inner pointer `lead+0x2c2`, so steam generation at lead+316 is accessed as inner+54. Identical offsets in definitions and locomotive instances are not equivalent fields.

## Generation and persistence

Function0060384a forms this inner pointer explicitly at00603856. For ordinary finite boiler-water values (lead+2da) at least -0.029999999329447746, it writes:

`generation = min(definition[1fe] * energy_output[306] * definition[1f6], definition[1fe])`

The branch stores at006038ed/00603925 (inner+54). Below that water threshold it instead decreases lead+342 by the supplied time argument. If this counter becomes negative and global809e38 is zero, it sets lead+296 bit8 and sets generation to0. Otherwise it leaves the previous generation value unchanged. Thus a readable nonzero generation value is not unconditional evidence of fresh recalculation under every state. The global's meaning, counter initialization and full failure semantics remain unresolved; this evidence alone does not name bit8 a boiler explosion.

## Pressure and rate arithmetic

Function00603340 consumes generation minus usage (inner+54 minus+50), multiplies by definition-dependent factors and the supplied time argument, then divides by3600 before adding to boiler pressure. It also divides by2 earlier in that expression. This is consistent with hourly rate conversion, but rate mass units and the caller's time argument still need tracing before declaring lb/hour as verified. The ordinary final pressure clamp is40 to1.2 times definition+21e. A nonzero809e38 adds a second clamp from0.65 times that definition to definition minus0.25. Do not infer the global's player-facing option name yet.

## Exhaust warning

Function00604450 clears lead+296 bit0x100 and sets it only when cylinder rate lead+31a is strictly greater than engine-definition+216 (finite ordinary values). This establishes the warning producer, improving the previous debug-label-only mapping. Other computations in this function transform an output value and blower-related values; they are not yet fully named.

## Further entry points

Pass93 also captures00603d5d (injector selector0/1; successful transfer adds the same amount to water mass+2ce and subtracts it from tender mass+2de; failed settings can still drain tender water) and00604243 (regulator characteristic). These need detailed branch and helper review before new telemetry semantics are asserted. Pass92 includes0060586f, which compares controls and feeds notification events; it is not the principal physics producer.

Pass92:3 functions,983 instructions/4166 bytes, zero disk/live mismatches. Pass93:4 functions,633 instructions/2341 bytes, zero disk/live mismatches. These checks prove the inspected instruction bytes match this image, not that every branch executed during the earlier steam capture. Gameplay remained paused throughout this static investigation. Candidate count remains851; this checkpoint strengthens existing candidates and identifies the next physical-unit/cadence checks.

## Update scheduler, coal consumption and injectors

Pass94 traces the generation caller00602bf0; pass95 follows the engine dispatcher005f5630; pass96 locates scheduler00607bd0. This scheduler adds its incoming delta to train+8a, then while that accumulator is strictly greater than train+8e, calls the engine dispatcher with train+8e and subtracts that interval. Equality does not enter another iteration. Thus the steam producer argument is the train update interval, not necessarily the current render-frame delta. The train-type dispatcher forwards it unchanged. Snapshot `captures/steam-update-paused-01/steam-debug.json` observes interval0.25 and remainder0.177272379 at paused36268.28125. This is a configured quarter-unit step; the upstream seconds timebase and actual running frequency still need direct confirmation. AI use of this scheduler is not established.

Function00603691 writes coal-burn candidate lead+32e, then updates fire mass as `max(fire_mass - interval*burn_rate/3600, 0)`. The native label and mass-unit evidence support a pounds/hour interpretation if the upstream interval is seconds; retain that condition until the timebase is closed. Function0060392e subtracts `interval*usage/3600*0.699999988079071` from water mass with a floor of approximately-0.1 times definition+24e. This extra coefficient makes naive steam-rate-to-water-loss equivalence invalid.

Injector helper0060435c is substantially absent from its decompilation: assembly is required. It selects a table value at7a2620 using the unsigned EDX argument capped16, applies the caller's scalar and a boiler-pressure power transform, then a controller-range interpolation, and multiplies by interval/360 (constant753d84). The result is a per-update transferred amount, not a persistent rate slot. The caller00603d5d adds it to water mass and subtracts it from tender mass. Native arithmetic does not justify interpreting an injector control fraction as flow.

The caller writes lead+2ee or+2f2 to1 on its successful working branch and0 on failure. Both read0 in the paused snapshot. These two working states are separate from steam-injector control settings; successful transitions have not yet been tested. Early returns/failure flags in the outer steam update can preserve old values, so consumers must retain session/update validity information.

Pass94:3 functions/429 instructions/1499 bytes; pass95:5 functions/747 instructions/2663 bytes; pass96:3 functions/110 instructions/394 bytes. All checked instruction ranges match disk and live with zero errors. These passes overlap earlier functions and must not be summed as independent coverage. Four new candidates expose the train update accumulator/interval and two injector working states, bringing the inventory to855.

## Runtime timebase and coal-rate validation

`sample_engine_cadence.py` and `analyse_engine_cadence.py` preserve a40-wall-second capture at nominal20ms sampling (`captures/steam-cadence-01/samples.jsonl`). It includes1980 samples, zero errors, zero context changes,26 cross-clock-step reads and492 paused samples. MSTS elapsed clock advanced30.101318359375 seconds; simulation-object+54 advanced30.121734619140625. The difference is retained, not rounded away: physics stepping, asynchronous reads and existing UnlockFPS timing patches prevent exact clock equality.

The train engine interval stayed0.25. There were121 observed fire-mass decreases, each consistent with one quarter-second burn update. Maximum absolute error against `new_burn*0.25/3600` was0.00006054772271lb, within half a float32 mass ULP at these magnitudes. Total fire mass fell1588.030151 to1580.917969lb. This is strong runtime corroboration of an effective seconds timebase and coal-burn rate in lb/hour for this installation and stationary test. It does not validate all rate channels, stock timing, arbitrary engine configurations or exact atomic frame relationships. Final separate paused capture is36307.70703125; the gap after the timed capture is not sampled.

Pass97 shows005f9285 passes simulation-object+10 to00607bd0 with **the global selected player train**, not each enumerated AI. Its loop advances object+54 by the same step. Pass98 shows0062924c invokes that loop with its own incoming delta. The simulation object's observed vtable773280 has its+4 slot at773284 pointing through thunk4016bd to0062924c. Ghidra misidentifies that thunk reference as a call and does not define it as a function; pass99/100 therefore do not close the virtual dispatch caller. Runtime cadence resolves the practical seconds/coal-rate question without claiming that static chain is fully traced.

Pass97:3 functions/252 instructions/825 bytes and pass98:3/918/3369 match disk/live. Pass101 was an exploratory false lead through default-definition/animation consumers; its00405694 entry has3 live mismatching spans, while00637dc4 matches. This unrelated patch has not been attributed and must not be included in claims that all exports match. Pass99 repeats0062924c and pass100 exports no functions; neither is new independently verified coverage. Read-only reference discovery is preserved in TelemetryReferences.java and simulation-object-references/references.tsv.
