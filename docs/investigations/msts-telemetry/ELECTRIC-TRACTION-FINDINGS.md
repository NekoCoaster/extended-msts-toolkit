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

## Released-brake low-speed movement

`electric-moving-01` records1182 samples over60 wall seconds, zero reader errors or unstable identities,17 simulation-time crossings. Normal UI controls resumed the released-brake Acela, applied one throttle increment0 ->0.025, then returned to idle. Brake cylinder remains0 throughout. Train speed reaches0.4140581191 m/s; this validates low forward movement only.

Force-like lead29e reaches5007.04052734 and current2c2 reaches45.5185508728. Power-like2a2 is230000 at2.5% throttle, as in the earlier braked snapshot, while the earlier braked force/current were zero. This below-cutoff observation supports the brake-cutoff interpretation, but the braked and released samples are separate tests rather than a continuous threshold crossover. It does not establish measured wheel force or electrical power consumption.

Cached limit496 changes200000..200284.578125 during movement and coasting. Of298 samples with positive throttle and stored force,211 exactly match the simplified float32 current formula `abs(storedForce)*definition1da/definition102`; maximum absolute residual is3.814697265625e-6. Current is calculated from an earlier native force return, whereas29e is a later stored shared-force quantity, and x87 rounding differs from the comparison; the small residuals are retained rather than calling all matches exact.

At the first sampled idle command, stored force/current still show the preceding positive values; they subsequently reach zero while speed remains positive. This validates command/output producer-phase separation during a transition, not a measured latency. The final time-series sample36558.82421875 has speed0.3847703934 m/s and zero throttle/force/current/power. The game is paused later at36565.16796875 (`electric-coasting-paused-01`), stored lead speed0.3771432638, zero demand/output, stable identities and released brakes. It is paused while coasting, not stopped.

`read_electric_series.py` uses the guarded electric reader; `analyse_electric_moving.py` produces `electric-moving-summary.json`. The existing sampled-gate freshness discrepancy remains unresolved. Higher-speed curve branches, reverse motion, modifier actuation, brake threshold crossover and AI traction remain open. No production integration or candidate prioritization.

## Shared-force helper: actual predicates and adjustment stages

Pass134 reexports00405f00,005f5efc and shared005f5808:432 instructions/1604 bytes match disk/live. Absolute-value helper005f5efc clears the sign bit and returns the float while preserving ECX. This makes the assembly's pointer identities materially important.

00405f00 receives the lead in ECX and obtains its engine definition separately. Its ramp branch requires definition94 bit200hex **and a positive float at car102**, not definition102. Capture `shared-force-paused-01` at36565.16796875 reads car102 raw bitsb53c0340 (about-7.004e-7) on both powered cars, while definition102 is220000 and definition10e30. Reconstructed ramp predicate is false. car102's actual semantic identity remains unknown; do not label it MaxForce or silently repair the apparent mismatch in telemetry logic. This is a paused predicate sample, not evidence of every past invocation.

For ordinary finite inputs inside the ramp branch, the helper compares absolute desired force and absolute previous stored29e. Increasing magnitude uses step=(definition102/definition10e)*supplied dt; decreasing magnitude uses step=(definition102/definition10e)*constant406031, whose disk/live value is2.0. The latter therefore does not use the supplied dt at that multiplication. The decreasing limited path multiplies by the player-controller c8 reverser in00405fed..00405ff3 and again in00406010..0040601c. Preserve this double multiplication as traced behavior; reverse/neutral outcomes have not been exercised. Unlimited/bypassed paths store the original signed input. The helper rewrites both lead29e and the shared caller's force argument (its ESP+90 resolves to caller EBP+c), then rewrites its return to005f595f, bypassing the older ramp and preceding force-denominator guard. Do not describe the skipped decompiled body as the running algorithm or assume its zero-denominator protection applies.

The shared continuation computes a normalized force magnitude using lead definition102 and distributes scaled force to eligible powered cars, with sign restored from the input. A patched0040b775 eligibility helper remains to trace. Later branches can further reduce car29e: a consist speed-condition branch; and definition8c bit80000000 with speed above definition10a. The latter applies a linear factor1-(excess*0.2) for excess up to5, then zero beyond5 (both constants verified disk/live). Thus sampled29e is a downstream per-powered-car value, and current2c2 from the earlier electric producer need not reflect all later modifications. No actual wheel/rail force measurement follows.

`read_shared_force.py` records the two powered-car states, raw predicate bits, definitions and constants without process writes. No new semantic field is invented for the unexplained car102 bytes. Next useful checks:0040b775 eligibility, powered rear-car distribution under demand, and read-only tracking of the helper predicate during movement. Existing gate freshness, reverse behavior, higher-speed branches and AI coverage remain open. Game unchanged, paused while coasting.

## Rear powered-car distribution and eligibility

Pass135 verifies0040b775 and shared caller:352 instructions/1315 bytes, zero disk/live mismatches. The helper enters with EAX=current car and ECX=engine definition. It invokes0040bad4 only if car dword0==15, engine type byte88==2 and car byte80 has bit4/8. Otherwise it returns the existing nonzero car pointer in EAX; the caller treats that as eligible. Therefore it is not a generic boolean getter. For qualifying electric cars,0040bad4 supplies the actual result; false routes to005f5c10, clearing stored29e. This rule does not test car296 bit2. Full physical interpretation of0040bad4 remains as limited by the voltage-helper findings.

`electric-powered-distribution-01` extends the guarded sampler with paired per-powered-car fields.875 samples, zero errors/ownership failures, simulation36565.16796875..36594.16796875;433 samples have positive lead force. At2.5% throttle, both identical-definition Acela power cars have exactly matching force29e and power2a2 in every sample, reaching5015.00048828125 and230000 respectively. Lead current2c2 reaches45.5909118652 while rear2c2 stays0. Lead flags296 stays2; rear stays0. Both type words are15 and flags80=93 (bits4/8 set). This corroborates shared-force distribution independently of the rear's sampled bit2, not independent rear electric-physics/current execution. A zero rear current field must not be reported as measured absence of current.

`analyse_powered_distribution.py` generates `electric-powered-distribution-summary.json`. Speed ranges0.3695989251..0.8733735681m/s in the bounded capture. Throttle was returned to idle after capture completion, and `shared-force-paired-final-01` confirms paused36615.04296875 at1.1324093342m/s, both stored force/power zero. This later speed lies outside the time-series range. Game remains paused while coasting with released brakes. No independent branch result was remotely called and no memory written.

Broader implications: identify the active lead and field update path before applying a cab channel to followers; retain zero, stale and unsupported as different possibilities. Tests with different locomotive ratings, false rear eligibility, reversed consists and AI remain open. Inventory candidate count unchanged; this adds applicability evidence, not prioritization.
