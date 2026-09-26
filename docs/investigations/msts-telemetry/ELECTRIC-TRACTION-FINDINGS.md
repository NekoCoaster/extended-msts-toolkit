# Electric traction producer checkpoint

This checkpoint identifies native producers and preserves one stationary Acela snapshot. It does not validate moving electric traction, dynamic braking or AI electric control. No game writes or native calls were used.

## Type distinction and instruction evidence

Engine-definition byte+88 uses2 for electric and3 for diesel. Electric controller wrapper kind and player-control global use3. These are separate enums. The current Acela definition54496112 reads2 while its controller kind is3. Dispatcher005f5630 sends electric through00402a40 to005ed2f0; diesel through004011a9 to005ea220. Pass105 and the diesel-specific helpers in pass106 must not be described as electric evidence. The shared005f5808 routine remains relevant to both.

Pass107 verifies005ed2f0:637 instructions/2464 bytes. Pass108 verifies005edc90,005edfc9 and005ef04b:231 instructions/833 bytes. Both have zero database-versus-disk or disk-versus-live instruction mismatches in PID7160. Exact-image assumptions remain mandatory.

## Gate, demand and stored values

Electric lead+296 bit0x2 gates the initial calculations in005edfc9 and005edc90. Its writers include pantograph handling, a006107a0 condition still unresolved, and route flags+3c with the previously traced00406d2c consist helper. It is a native calculation gate, not a universal overhead-wire contact detector.

005edfc9 returns controller throttle+8c times engine-definition+fe when this bit is set, otherwise zero. The returned value is a calculation input to shared005f5808, not an independently stored measurement of delivered power.

005edc90 computes a speed-dependent force-like limit from definition+fe/+102/+106/+13e. It stores that limit at lead+496 and a copy of throttle at lead+492, then multiplies them. When the gate is false it sets its local result to zero but skips both stores: cached+492/+496 can therefore be stale. Do not equate them to current delivered output. The piecewise curve remains in pass108; its complete unit mapping and boundary behavior have not been independently tested.

The routine optionally calls005eef48 when player controller+394 is nonzero; that modifier remains untraced. It then multiplies by signed reverser controller+c8. If definition+63c exceeds native epsilon753e38 and brake-cylinder lead+230 exceeds definition+640, it zeros the result. The electric outer update computes lead+2c2 as abs(this returned result)*definition+1da/definition+102, unless the denominator is below epsilon, in which case it stores zero. Unlike the inspected diesel path, the electric current source is thus downstream of reverser and this brake cutoff. It remains upstream of shared005f5808 distribution/physics, and the existing cab current display can select a separate dynamic-braking source. Do not call this stored value measured net electrical current or delivered wheel force.

## Guarded paused read

`read_electric_traction.py` requires player type3, wrapper kind3 and definition type2, plus the existing exact-image Reader. It preserves raw source fields and checks context after reading. `captures/electric-traction-paused-01/traction.json` has stable paused time36104.00390625, speed0, gate true, optional modifier0, throttle0, signed reverser1, cached throttle0, cached limit200000 and current source0. Brake cylinder29.096672 exceeds definition cutoff15 with enable1. Definition values are+fe9200000,+102220000,+106200000,+13e13,+1da2000. This baseline agrees with idle output; it cannot independently prove cutoff behavior because throttle is already zero.

Next distinguish throttle demand, the brake cutoff and power-gate changes with controlled runtime transitions, then trace modifier005eef48 and shared output redistribution before interpreting delivered output. Preserve zero, unavailable and stale as distinct states. AI applicability is still untested.

## Stationary control transitions and freshness correction

Five snapshots summarized by `analyse_electric_traction.py` in electric-traction-summary.json have stable context, no clock crossing and zero speed. They are separate observations, not a continuous timing trace.

At36116.69140625, throttle and cached throttle are0.025000000373, cached limit200000, reverser1, modifier disabled. Cylinder29.096672 remains above cutoff15. Stored lead+2a2 is230000, while force+29e and current+2c2 are0. The power-like source equals throttle*definition+fe even while the force/current path is cut. It must not be described as measured power delivery. These values support the native brake-cutoff interpretation, but a below-threshold comparison remains needed.

After the visible PANTOGRAPH(DOWN) action, snapshot36131.65625 shows+2a2 now0 while throttle and cached throttle remain0.025. After THROTTLE(0%), paused36143.73046875 shows controller throttle0 but cached throttle still0.025 and cached limit200000. A same-time separate voltage snapshot confirms pantograph0, consist condition false and derived voltage0. The sampled lead+296 bit0x2 nevertheless remains set in both traction snapshots. Thus the static branch's use of that bit does **not** make a later sample of it a cache-validity indicator. The writer/timing responsible for this discrepancy has not been established; do not explain it away as an atomic read failure, because the idle mismatch is preserved while paused.

Raising the pantograph at idle and pausing again gives36164.390625: cached throttle refreshes to0, limit200000, force/current/power-like values0. The train is left stationary, paused, forward, idle, pantograph up and brakes applied. Original captures retain their initial `traction_gate` label; it means only the sampled bit. The inventory now explicitly disclaims freshness inference from that bit. No candidate was dropped or prioritized.

## Additional native tracing

Pass109 (92 instructions/302 bytes) resolves005eef48 as a high/low force cap. When definition+630 and+62c are both positive, it compares electric controller+3ac to+3a4: equality selects definition+102 times+62c as a cap, otherwise+102 times+630. It clips only values at or above the selected cap. The already mapped ACCELERATE_HILO source is+3ac. Enable+394 is0 in these captures, so this is static producer evidence, not runtime actuation validation.

The other pass109 function006107a0 is called with ECX=lead+53a, not the lead base. It returns nonzero when that subobject+4 and its pointed object+3c's+20 are nonzero; its physical meaning remains unresolved. Do not read lead+4/+3c as these inputs.

Pass110 (811 instructions/3609 bytes) exposes another return-address rewrite:00405f00 stores the adjusted force into lead+29e and into the caller's force argument at its ESP+90, then rewrites its return target to005f595f. It bypasses the apparent older ramp code between005f5826 and005f595f. The decompiler alone is insufficient to describe shared005f5808. Ramp arithmetic, units and conditions need a dedicated assembly review before deriving delivered force.

The other pass110 function005ee01f compares electric controller values with retained global values and emits numbered calls to005ef10a/005ef172, including throttle, reverser, brakes and pantograph-related branches. This supplies a concrete lead for the requested input/audio-event surface, but event semantics and receiver lifetimes remain untraced. Pass111 (119 instructions/499 bytes) traces005f5d09's trailing-unit steam/diesel propagation and finds no electric bit writer there. All three passes have zero disk/live instruction mismatches. None resolves the sampled gate-bit discrepancy yet.
