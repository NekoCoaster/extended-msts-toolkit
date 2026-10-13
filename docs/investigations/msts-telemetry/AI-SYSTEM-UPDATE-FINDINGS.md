# AI vehicle-system update boundary

The traced locomotive/brake scheduler is explicitly called with the player train. In pass137/005f9285.asm,005f9475 loads the integrator step from object+10 and005f9478 pushes it;005f9479 loads ECX from global007c2ac0 (the established player-train pointer), then005f947f calls00403076, the thunk for00607bd0. The decompiler omits this register-level object identity and must not be used to infer that each enumerated train receives the call.

Scheduler00607bd0 accumulates time at train+8a and processes intervals at+8e, dispatching005f5630 when lead+6a is nonzero. The dispatcher selects steam/electric/diesel/other by engine-definition+88. The already traced engine path reaches shared005f5808, whose tail calls brake updater005db099 through00402379. The newly established player pointer narrows the applicability of this evidence: it does not validate independent AI locomotive or brake simulation.

Pass138 identifies the integrator caller0062924c and a data reference at00771460 to its thunk00403cdd. Its post-integration car motion writes are skipped when car+84 bit2 is set, consistent with the previously captured physical AI motion. Existing pass84/85 establishes the separate service motion path005a7337 and follower copy00636475. These are complementary paths, not proof that all AI system fields are always zero or immutable.

Verification against the installed disk image and live PID7160: pass136110 instructions/394 bytes; pass137252/825; pass138918/3369; all zero byte mismatches and read errors. Pass136 repeats the dispatcher baseline; the new object-identity evidence is pass137. Only exported instruction ranges were checked. No gameplay transition or new AI field sampling occurred in this investigation, and no memory writes were made.

Extraction rule: keep structurally available brake/force fields as candidates, but mark AI freshness and simulation semantics unvalidated. Neither a readable pressure nor a zero current/force is enough to infer actual AI braking or traction. Next evidence should pair service speed/target/acceleration and physical-car brake/force fields over a moving AI observation, then trace any differing writers or initialization. Other indirect callers, alternate modes and AI initialization are not exhaustively excluded by direct cross-references.

## Paired moving AI observation

New read_ai_systems.py pairs service registry and physical car fields, checks service backlinks/chain links and rechecks car owner/definition/body. It uses the existing exact executable hash gate and query/read-only access. Each capture preserves its script versions. The paused Acela control sample passed all eight-car checks before switching through the UI to Marias Pass / Grain Train Through the Night.

ai-systems-moving-01:567 samples, no errors, player only,187 clock crossings. ai-systems-moving-02:1097 samples, no errors,318 clock crossings, simulation73856.3046875..73903.4375. AI400005 appears with22 cars in1075 samples; speed14.95923996..24.81072235m/s. Service speed and target span14.95924282..24.81071854, acceleration candidate-9.53668118..0.57212251. That acceleration range is not independently verified physical acceleration. Stored car acceleration remains0. AI powered fields29e/2a2/2c2 remain0; brake force22c/cylinder230 remain0; reservoirs224/228 and pressure234/238 remain90. Flags84 include2,6,1048578,1048582.

All train service/chain checks pass, but3390 AI car observations fail the combined owner/definition/body stability check. This check cannot identify which condition changed; body-buffer swaps are a possibility, not a diagnosed cause. The stable subset contains20260 AI car observations (1884 powered); brake-force/cylinder and all three powered fields remain0 in that subset too. Sequential reads are never atomic. Counts include paused observations, not independent physical update counts.

During this capture the player passed the red signal and the UI displayed Activity failed - ignored red light. The final666 samples are paused at73903.4375; AI observations span410 distinct simulation times. Thus this is an initial moving/physicalization observation followed by a failure-alert pause, not120 seconds of uninterrupted gameplay and not a successful signal-clear run. No assertion that installed compatibility settings suppressed the failure is warranted. ai-systems-alert-final-01 preserves the resulting state; no save was overwritten. Next run should brake the player before the signal while continuing the AI observation.

This corroborates that the sampled AI physical fields do not express changing traction even while service-driven speed changes. It does not prove the fields never update in other AI states, nor that pressures are simulated or that there was no physical braking. Keep candidates and their applicability limitations, without retention decisions.

## Service acceleration and target-capped integration

analyse_ai_acceleration.py excludes paused samples and retains the first observed service state per scheduler timestamp. Across48 timestamps in ai-systems-moving-02, all47 eligible consecutive one-second speed predictions exactly match the next stored service speed after final float32 rounding. One sequential registry-versus-physical-associated service read differs, explicitly counted; no atomic snapshot guarantee follows.

For positive travel sign,005a41c2 uses v=abs(service138), a=service140 and target=service13c. When a is zero, speed remains v. Otherwise it computes reach=abs((target-v)/a): if reach<=dt, final speed is target; otherwise final speed is v+a*dt. Distance uses trapezoidal integration until reaching the target and constant target speed for the remaining time. It clears the intermediate acceleration on reaching the target, then later driver decisions can write a new acceleration and target. Therefore stored140 is a control input for the next kinematic interval, not the derivative of every displayed physical-train speed sample.

The most negative captured state is index295 at simulation73888.5703125, scheduler time73888, speed15.5313653946m/s, target14.9592428207m/s and acceleration-9.5366811752m/s^2. Its implied target-reach time is0.05999178995s. The next one-second scheduler state matches the target exactly; applying that acceleration for a full second would be wrong. This explains the integration effect of the large value, not which specific profile restriction generated it. Reverse travel, target distance reconstruction and arbitrary nonfinite states remain untested.

Pass139 reexports005a41c2 and direct caller context:1185 instructions/5084 bytes match disk/live with no errors. ai-acceleration-summary.json contains all observed scheduler states and comparison residuals. This is a service-kinematics validation, not proof of physical force, passenger comfort acceleration or all AI branches.


## Physical train mode and car force-gate writer, 13 October 2026

0060ceee writes the low argument byte to train+5a, walks train+62 then car+a8, and sets car+84 mask0x2 only when the full integer argument equals1; all other arguments clear that mask. Thus a byte value1 alone is not universal proof that the full argument was1. Inspected ordinary callers use1 or3. The routine does not modify body+4 mask0x2.

005a58af physicalization passes1 via thunk004011b8 to service+158 at005a5a6e, before setting service+134=1. In0062924c, body kind1 with car+84 bit2, body+4 bit2 and nonnull car+1f8 calls the setter with3 on [car+1f8]+158, then tests the car flag again before continuing post-integration writes. This supplies a static route out of the simplified mode; the meaning/producer of body+4 bit2 and actual runtime transition remain open. 006353fc also passes3 when train+5a equals1 before its subsequent train-list reconstruction. Do not equate all non1 modes with player ownership or call the whole car+84 word an AI flag.

Whole recognized-instruction scalar84 scan retained in force-mode-offset-scan-20261013-01 found613lexical matches. The scoped write filter exposed previously unexported0060ceee. force-mode-writers-20261013-01 verifies two functions295instructions/1225bytes, including00633893 whose inspected car+84 write sets mask4, not mask2. force-mode-callers-20261013-01 verifies five functions1605instructions/6079bytes. All checked bytes match current disk and PID39096 with zero mismatches/errors. Static references do not prove exhaustive callers or execution.

Read-only force-mode-state-20261013-01 captures19cars at paused64965.1015625 with the same before/after clock, zero errors and zero per-car guard failures. Player train400000 has8cars, owner mode3, car flags128, body flags0; AI train400001 has11cars, owner mode1, car flags2, body flags0. All have a nonnull service pointer. This corroborates the mode/flag correspondence for two current trains, not a live transition, universal mode enum, independent AI force simulation or solver cadence. Root/identity rereads cannot make sequential snapshots atomic.


## Body override writer and reset connection, 13 October 2026

The prior collision response analysis already resolves one body+4 mask2 producer:005f6d1e reads bodies from record+c/+10 and ORs2 into each nonnull body flag word before invoking the side callback. Dispatcher005f696f selects this response when record mask1 is clear, subject to the separately documented classifier and simulation gates. It can mark one existing body as well as two; the flag alone is not a two-train collision, damage, derailment or currently active contact indicator. This is one known writer, not an exhaustive writer inventory.

Placement00628d09 clears the entire body+4 word at00628d5c after checking both definition+8c masks80 and40, then may set mask1 for an activity condition. Consequently the field is neither immutable nor a lifetime collision counter. Combining this with0062924c and0060ceee gives a static route: response sets body mask2; a qualifying kind1 car still carrying car mask2 and a service pointer can cause its service train to switch to mode3 and clear linked-car mask2. Cross-routine runtime order, body swapping, and actual execution are not established by this connection.

Fresh copies in captures/body-mode-override-native-20261013-01 verify response, dispatcher and placement:826instructions/3332bytes match disk and PID39096 with zero mismatches/errors. Current paused19car snapshot from force-mode-state-20261013-01 has body flags0 throughout;it is negative current-state evidence,not a mode-transition test. No collision was induced.
