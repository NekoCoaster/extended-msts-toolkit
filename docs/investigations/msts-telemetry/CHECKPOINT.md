# MSTS telemetry discovery — independent research

Status: **active, incomplete**. This workspace is separate from NEMT. No production code, game assets, installation settings, or executable have been edited. In-game controls and activity restarts are part of testing. Do not rank candidates or make keep/drop decisions yet.

## Deliverables so far

- `inventory.json`: flat candidate inventory with applicability, type, units, extraction method, source evidence, lifecycle and limitations. `INVENTORY.md` is its compact readable index.
- `source-manifest.json`: hashes for the 126 installed asset files inspected in the first discovery sweep.
- `read_live.py`: external read-only process sampler. Uses only QUERY_LIMITED_INFORMATION and VM_READ. No Frida, code injection, debugger attachment, remote function calls or process writes.
- `inspect_registry.py`: bounded train-registry discovery probe.
- `captures/`: original samples and exact reader copies. `capture-summary.json` is reproducibly produced by `analyse_captures.py`.
- `runtime-provenance.json` and `installed-settings-observed.ini`: tested image and pre-existing installation configuration.
- `pass01b` through later numbered passes: targeted native decompiler/assembly evidence. `pass01` is a retained failed export, not evidence of successful decompilation.

Current inventory has 295 direct-read candidates/structures, 19 derived candidates, 68 native cab channels (59 declared in installed cab files) and 507 configuration paths (474 leaf paths and 37 paths with direct values beside children, with four shared paths), totaling 889 entries. This is **not** a count of confirmed independent live values. Pointers are useful extraction/identity metadata, static configuration is not dynamic telemetry, cab declarations are not proof that every field is simulated, and derived candidates still need validation.

Latest test leaves Acela Express paused at36104.00390625 on Northeast Corridor Explore Route, stationary, throttle idle, forward direction and pantograph control up. Steam and preferred diesel evidence are preserved in separate captures.

## Test scenario and installation

The user's preselected process was PID 7160 at `C:\MSTS\train.exe`. Always rediscover the PID before reuse. It was on the route/activity selection screen; the selected activity was started normally.

Installed activity: `ROUTES/USA2/ACTIVITIES/evegrain.act`, displayed as **Grain Train Through the Night**, Marias Pass. The activity header says StartingSpeed 0, but `SERVICES/EveGrain.srv` specifies 11.176 m/s (25 mph). The actual initial cab displayed 25 mph, throttle N2; the first paused memory sample had throttle 0.25, reverser 1 and native control type 2. Do not use the header alone to predict starting motion.

Runtime player consist: 23 vehicles (two powered vehicles). The configured consist is `Dash921gran.con`. AI service `EveGrain (Traffic)` uses `2 x Dash 9, 20 Intermodal`, matching the observed 22-vehicle AI train. The later scheduled `EveGrain (Traffic01)` uses `D9gds`; its scheduled offscreen activation has now been observed, while creation of its physical train remains untested. The activity text's 30 grain cars and rain do not match this installed initial state: the runtime shows snow and the consist is smaller. Preserve these discrepancies; do not change assets to make them agree.

Disk executable SHA256: `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`. Clearing only the PE LAA flag produces `1b041ecf4b2d2a7306218efa1d7418fd87dc21dc4b2d00056cb5749084fe55a4`, the widescreen image recognized by current NEMT source. The reused Ghidra database is the original `69218fce876298c684a2140c7d3925a452c47bb10037ffd8c491f65c5c0c6e7a` image. Existing NEMT `docs/investigations/widescreen-background.md` documents a 108-byte original/widescreen difference. The offsets work in this live image, but byte-level validation of all newly traced functions is still outstanding; do not claim identical binaries.

The running installation already enables IgnoreRedSignal, PreventActivityEnd, EnableCrawl, CounterTilt and UnlockFPS. These settings were not changed. After derailment the capture is modified by the pre-existing NEMT runtime; it is not a stock-MSTS physics validation. The source repository at `C:\codex\repo\NEMT` remains clean at `5cd5896`.

## Direct findings

[Evaluation findings](EVALUATION-FINDINGS.md) identifies live speed-episode storage and its40-record cap, separate from teardown-only report summaries. Nonzero violation transitions remain untested.

[Clock findings](CLOCK-FINDINGS.md) resolves separate elapsed/day-time accumulators and identifies live NEMT timing patches; internal calendar/clock components are retained with untested lifecycle limits.

[Camera findings](CAMERA-FINDINGS.md) adds player view mode/tracking and render-camera position/basis from native consumers and a live cab/front/rear/trackside/cab switch test. Lifecycle and transition timing remain untested.

[Track-item findings](TRACK-ITEM-FINDINGS.md) identifies all 2,970 live item kinds and verifies stored platform, siding and speed-post payloads against the route file. Dynamic behavior and effective restriction semantics remain open.

[Infrastructure findings](INFRASTRUCTURE-FINDINGS.md) enumerates all 732 route nodes with validated route IDs, resolving earlier disconnected/ambiguous coverage. It also records 78 service-linked track-presence records and seven signal/service associations; reservation semantics remain unverified.

[Track topology findings](TRACK-TOPOLOGY-FINDINGS.md) adds a 726-node connected runtime graph, 246 readable junction selectors and 718 derived route-node matches. Disconnected components and switch transitions remain open.

[Track geometry findings](TRACK-GEOMETRY-FINDINGS.md) maps current section length, radius, angle, width, skew and flags for player and offscreen AI. Four geometry definitions match installed assets; straight-grade and nominal-curvature formulas remain explicitly derived candidates.

Latest checkpoint: [AI lifecycle findings](AI-LIFECYCLE-FINDINGS.md) records 539 samples, zero read errors, physical removal of the first AI and scheduled offscreen activation of the later AI. The first AI eventually retained positive speed with stationary track position; subsequent [scheduler tracing](SERVICE-UPDATE-FINDINGS.md) found its update gate disabled and last-update clock stopped. The precise deactivation trigger remains unproven. The later bounded pause/resume test left the game paused at 74548.40625, player intact and stopped; see UPDATE-CADENCE-FINDINGS.md.

[Vehicle-system findings](VEHICLE-SYSTEM-FINDINGS.md) adds per-car pressure, requested brake force, coupling-force candidates and inertia. Session metadata is in captures/session-header-running-01/session.json; header parser offsets are relative to activity+4.

[Activity event findings](ACTIVITY-EVENT-FINDINGS.md) matches the three loaded location events to ACT definitions. [Evaluator tracing](ACTIVITY-EVALUATOR-FINDINGS.md) now identifies mutable activation, trigger latch/reversal and event-outcome result flags. Actual firing transitions and operational evaluation counters remain unverified.

[Environment findings](ENVIRONMENT-FINDINGS.md) adds read-only precipitation, wind, lighting and fog observations from the current paused snow/night scene; weather-to-physics coupling remains unproven.

[Track position findings](TRACK-POSITION-FINDINGS.md) documents 45 readable vehicle track records, section links and the native 2048-m tile/origin conversion. Dynamic origin-crossing verification remains open.

See [AI service findings](AI-SERVICE-FINDINGS.md) for the separate service registry, loaded future traffic, identity strings, driver speed/target/acceleration and lifecycle candidates. Latest checkpoint leaves MSTS paused and NEMT unchanged.

Earlier checkpoint: [Signals and cab findings](SIGNALS-AND-CAB-FINDINGS.md) establishes a same-head native aspect 0-to-7 transition, traces all 68 base cab names, verifies diesel pressure dynamics and documents the corrected current-unit interpretation. `signal-transition-01` finished with 958 samples and zero read errors. `detail-summary.json` contains normalized legacy-current values; original captures are unchanged. That checkpoint left the game paused at simulation time 74000.0546875, player stopped before the cleared signal; the subsequent lifecycle run is documented above. See that checkpoint for byte-level verification of 14 traced functions and remaining limitations.

1. Native train selection at `0x60cd5c` walks a circular list at `[[0x7bdecc]+0x20]`. Node +8 is an index into the generic object table `[0x828108]` with 8-byte stride; the first word of that table entry is the object pointer. Validate each object as a train before use. The table itself contains many object types and must not be treated as a train-only array.
2. The list yielded player train ID 400007 and AI train ID 400005 in the first run. Both had valid vehicle-owner backlinks at car +0x98 and body-owner backlinks at body +0x11d. Cars use +0xa0/+0xa8 connections. These IDs and pointers are session-local until reuse/lifecycle tests establish stronger identity.
3. The AI train's body velocity and train +0x92 speed changed coherently (about 18.46 to 21.26 m/s in `ai-running-01`), independently of the player (about 6.32 to 9.66 m/s). Raw trace contains complete body samples for both consists.
4. Both trains point at the same controller wrapper at train +0x72. **Do not export that wrapper's throttle/brake/reverser as independent AI controls.** AI service/driver state at train +0xe6 needs tracing separately.
5. Physics position underwent a large common coordinate reset during normal movement. Values are local simulation coordinates, not stable global XYZ. Tile/origin mapping is required before absolute position, long-distance displacement, acceleration from position or geographic location is advertised.
6. Track monitor at `[0x809f1c]` is a circular linked list with entry pointer at node +8. Native debug function `0x5aefb1` explicitly labels entry +4 Dist, +8 Rad, +0xc Grad and +0x10 Des Vel. Type labels come from the pointer table at `0x79f898`; this is evidence for names, not proof of units or full event semantics.
7. Read type labels: NON, SIGNAL_POINT, SIGNAL_POINT_STOP_AND_PROCEED, SIGNAL_POINT_FAILED, TRAINS_POSITION, DESTINATION_POINT, CURVE_CHANGE_POINT, JUNCTION_POINT, GRADIENT_CHANGE_POINT, HAZARD_POINT, SPEED_LIMIT_CHANGE, STOP, PATH_REVERSE, PATH_END, PATH_JUNCTION_WRONG.
8. The red-signal monitor `0x5864ee` examines type 1/2, desired velocity zero, distance below a threshold and referenced object's +0x1c bit 0x2000, then sets controller failure bit 0x100 at +0x378. Do not call raw signal flags a decoded aspect yet. The existing bypass can clear failure state before an external sampler sees it.
9. Same-time and stable-pointer checks expose sampling races. For example `ai-running-01` crossed a simulation step in 26/178 samples despite zero read failures. External read success is not atomic simulation-state consistency. Capture timing and validity must accompany future telemetry.

## Runs and honest limitations

- `initial-briefing`: one paused sample, valid 23-vehicle graph and player controls.
- `first-running`: 181 samples, initial pause then motion; no read failures. Registry sampling was added later, so this run has no AI registry data.
- `paused-red`: three identical-time paused samples.
- `registry-paused`: proof of two registered train objects and 45 readable vehicle bodies; includes asset-directory strings.
- `ai-running-01`: 178 samples, both trains moving and subsequent pause, no read/registry failures. Contains coordinate-origin jump.
- `ai-pass-braking`: 472 samples, **unsuccessful clean-pass test**. The player reached the red-signal alert before braking, continued with the installed bypass, then collided/derailed near the approaching AI. Retain as abnormal-state evidence only. Player derailment count rose to 23; AI registered consist count changed from 22 to 6. Detached/unregistered cars may exist outside the registry traversal; these are not yet enumerated. Train speed and actual body speed diverged strongly after derailment.
- `clean-ai-pass`: completed 477 samples over about 240 wall-clock seconds. One initial null-address sample during the loading/briefing transition was logged as an error; 476 complete samples and zero registry errors followed. The player stopped about 0.6 miles before red. Both consists remained on rails, the AI passed the cab, and the UI changed from Stop to Clear. `captures/clean-ai-pass/ai-passing-signal-clear.png` preserves that visual comparison. This verifies the gameplay scenario, **not yet an extracted aspect transition**: the captured signal-entry desired-velocity/flags did not track the visible clearance. Further trace the live aspect and whether this global profile is cached or reused between service contexts. Of the complete samples, 124 crossed a simulation step. The activity was then left paused through Escape, with the player intact and emergency brake still applied. No save was created.

The first run was exited without saving. Activity evaluation displayed derailment at 1 minute 55 seconds, two minor operational errors and two speeding events totaling ten seconds. These UI-observed evaluation fields are additional candidates, not yet decoded runtime counters.

## Reproduce safely

Launch MSTS normally and load the preferred activity. Rediscover its current PID. Research scripts reject unknown disk image hashes. Run a fresh capture name (existing directories are rejected):

```powershell
python C:\dev\Codex\2026-09-10\msts-telemetry\read_live.py --pid <PID> --name <new-name> --seconds 30 --interval 0.25
python C:\dev\Codex\2026-09-10\msts-telemetry\inspect_registry.py --pid <PID> --name <new-name>
python C:\dev\Codex\2026-09-10\msts-telemetry\analyse_captures.py
python C:\dev\Codex\2026-09-10\msts-telemetry\build_inventory.py
```

Use Escape and the visible pause menu for long analysis work. The attempted Pause key did not establish a persistent pause in the first run. On restart wait for the operations-notebook briefing, close its X, then apply Backspace while actually driving; a key sent during loading/briefing is not evidence that the brake was applied. Verify brake-pipe/cylinder and speed on screen. Brake early, not at a short remaining distance. Do not leave the player moving while performing decompilation or lengthy analysis.

`export.ps1` reuses the prior Ghidra project read-only. Quote address arguments: PowerShell interprets an unquoted value such as `0041e196` numerically, causing the retained pass01 failure. The exporter now reports invalid addresses explicitly. It follows thunk references one level and does not save database changes. Cab dispatchers have decompiler warnings and a shared assembly helper at 0x422f06; inspect instructions/jump tables rather than trusting the malformed high-level switch reconstruction.

## Full remaining scope — not a completion claim

- Expand signal validation beyond the now-observed same-head Stop-to-Clear transition: other aspects, multiple heads, speed heads, failures, AI iterators and lifecycle.
- Decode stable global/tile coordinates, track node/section/index, path direction/progress, gradient/curvature and vehicle/train length. Test origin shifts rather than smoothing them away.
- Trace AI service identity/name, timetable and scheduled spawn/despawn, driver target/desired speed, signal response, waiting reason, route/path reservations, authority, occupancy and switch state. Validate absence versus unavailable versus zero.
- Establish independent AI controls/physics depth and locate static consists, detached cars and unspawned services. Do not infer these from the active player/AI list.
- Map all declared cab channels to source fields and units for diesel, steam and electric, including pressures, brake controllers, wheel slip, engine RPM, traction/dynamic braking, fuel/water/coal, boiler/firebox/injectors, pantograph/voltage, gear state, alerter and displays. Explore channels present in the binary but absent from installed cabs.
- Trace car-level braking propagation, coupler slack/forces/breakage, friction/adhesion, resistance and forces, load, wheel/axle animation and true versus derived motion. Validate on-rail and lifecycle behavior; isolate the abnormal NEMT-modified run.
- Trace all signals and switches, speed restrictions, traffic/track occupancy, timetable/station/platform data, operational permissions and activity events/objectives/failures/evaluation counters.
- Reuse existing precipitation/sky evidence for time/calendar/season/weather, precipitation intensity/type, visibility/fog, wind/clouds/lighting and location dependence. Add runtime exposure and provenance instead of claiming static ENV configuration is the live state.
- Inspect input/action, audio-event and camera/UI state surfaces where extractable; inventory event timing and sampling limits. No candidate is discarded for being peripheral.
- Expand discovery beyond installed file declarations: native parsers/serializers, debug/HUD producers, vehicle/service/object lifecycle and save-state schemas. Identify supported, stubbed, computed and unavailable values.
- Measure representative update cadence, pause behavior, reset behavior, sample consistency and collection overhead. Test alternate engine types, loading/restarting and later traffic. Keep explicit coverage boundaries.
- Refine the flat inventory into individually meaningful telemetry candidates with specific source/units and evidence per row; remove parser artifacts or merge duplicate declarations only when they describe the same data point. This is cleanup, not keep/drop prioritization.
- Produce a final evidence-backed report and NEMT handoff only after the above discovery coverage has been reviewed. No implementation/integration into NEMT is authorized by this research phase.

[Steam debug findings](STEAM-DEBUG-FINDINGS.md) maps additional generation/use, stores, smoke and warning fields, with a positive paused read and explicit rate-unit/producer gaps.

[Electric cab findings](ELECTRIC-CAB-FINDINGS.md) records13 raw source mappings, a negative type-gate test, voltage helper control-flow caveats and an invalid CAB_SWITCH mapping correction.

[Electric traction findings](ELECTRIC-TRACTION-FINDINGS.md) separates the calculation gate, potentially stale cached throttle/force limit and current-source producer, with a guarded paused Acela baseline. Moving electric validation remains open.

[Electric event findings](ELECTRIC-EVENT-FINDINGS.md) traces two registry-backed receivers, retained event bitmasks and three scalar slots. These do not provide a complete event history; clearing, playback, AI applicability and nonzero scalar transitions remain open.

[Receiver list findings](RECEIVER-LIST-FINDINGS.md) records20 live receiver identities, loaded labels,48 declared streams and bounded player-car associations. Eleven unmatched receivers remain without verified ownership.

Brake checkpoint: passes128–130 trace the brake dispatcher, caller and pressure sound-event references. Five additional candidates preserve the retained reference, directional latches and shared timers. Eight paused Acela cars were read without writes; pressure propagation and active event transitions remain untested. See VEHICLE-SYSTEM-FINDINGS.md and read_brake_state.py. This checkpoint remains local after published66f5bd1; discovery goal remains active.

Brake transition follow-up:1740 samples and13920 exact per-car pressure/force comparisons on Acela, with rising sound-reference/latch transition. Pipe values match across cars; six cylinder differences cannot establish propagation timing under sequential reads. Full release/falling events and AI brake tests remain open. Details: VEHICLE-SYSTEM-FINDINGS.md and brake-adjustments-summary.json.

Reservoir mapping:23 native brake parameter labels are bound to loaded definition offsets, enriching existing configuration candidates. Two current reservoir-pressure candidates added; configuration pressure defaults are explicitly separated from live pressure. See brake-parameter-map.json. Latest research remains local after66f5bd1.

Brake selector checkpoint:889 candidates, with separate selected mode and within-mode fraction. Acela loaded ranges confirm prior adjustments stayed in holding mode; release requires raw handle below0.2. Paused reconstruction matches stored mode1000hex. pass133 matches disk/live. This extension aftere695189 is local; full-release/AI and broader scope remain open.

Release attempt brake-release-01 retained1739 samples, zero errors, all mode1000hex: mouse operation increased holding demand; downward drags ineffective; keyboard decrement did not refill pipe. Native holding branch explains this. Release/falling validation is still open. Game paused36372.03515625, stationary, raw brake handle0.8365. Use deterministic keyboard decrement next, not repeated ineffective drag.

Confirmed Acela release: brake-release-02 plus separate settling capture observe holding/hold-lapped/release modes, falling latch/timer and eight cars settling cylinder0/pipe110 PSI. A12.93s observation gap prevents exact settling-time claims. Game paused36515.296875, stationary idle, brakes released. Inventory889 unchanged; existing evidence strengthened. Next moving electric traction/cutoff and AI brake coverage; full objective remains open.

Electric moving checkpoint:1182 samples, zero errors/unstable identities, speed0..0.414m/s with released brakes and2.5% throttle. Force/current become positive; idle outputs settle to zero during coasting. Prior braked comparison supports cutoff semantics without proving a continuous crossover. Game paused36565.16796875, idle/released brakes, still coasting at stored0.377m/s. Findings remain local aftere695189. Full scope and unresolved gate freshness remain open.

Shared-force checkpoint:pass134 and read_shared_force.py resolve ramp predicate car102 versus definition102, asymmetric ramp timing and downstream per-powered-car force adjustments. Both paused powered cars fail the actual ramp predicate; no new semantic meaning assigned to car102. Inventory889 unchanged; current and shared force are not universally interchangeable. Game unchanged paused36565.16796875. Next powered-car eligibility/distribution, with remaining scope intact.

Paired electric checkpoint:875 samples, zero errors, matching force/power on two Acela powered cars, but rear current stays0 and bit2 stays clear. Eligibility helper135 traced; lead-specific semantics must not be assumed on followers. Game paused36615.04296875 at1.1324m/s, throttle idle/released brakes, both stored force/power0. Inventory889 remains; AI, differing ratings and broader scope remain open.

## AI update applicability checkpoint

AI-SYSTEM-UPDATE-FINDINGS.md records the scheduler call005f947f explicitly receiving player train007c2ac0. The engine/brake chain cannot establish AI brake freshness; separate service motion remains distinct. Pass136-138 instruction ranges match disk/live. Inventory stays889 with367 evidence paths and126 unchanged original asset hashes. No gameplay interaction in this turn, no running tool jobs. Next: paired moving-AI service and per-car brake/force sampling in evegrain, plus alternate writer/initialization tracing. Broader discovery remains active; latest published checkpoint is9f9d445 and these new findings remain local.

## Paired AI vehicle systems runtime checkpoint

read_ai_systems.py and analyse_ai_systems.py now pair services with physical brake/force fields. Moving captures567+1097 samples had no read errors; second observes22-car AI400005, changing speed but zero sampled brake force/cylinder/traction/power. Stable subset corroborates zeros; combined stability failures remain explicit. Failure alert after player passed red signal froze final666 samples at73903.4375; game remains at that alert, no save overwritten. Do not describe this as successful signal clearance or uninterrupted120-second gameplay. Details in AI-SYSTEM-UPDATE-FINDINGS.md. Inventory889,370 evidence paths,126 asset hashes unchanged. All capture jobs finished. Next dismiss alert/inspect available continuation and brake player before proceeding, or restart preferred activity and brake early; retain observations and trace AI initialization/alternate writers. Latest remote9f9d445; new work remains local.

## AI acceleration interpretation checkpoint

Existing moving capture yields48 scheduler states and47 exact target-capped one-second speed predictions. Sharp negative service140 value reaches target in approximately0.06s, not a full second; specific driver-profile cause untraced. ai-acceleration-summary.json and AI-SYSTEM-UPDATE-FINDINGS.md preserve data/formula/limitations; pass1391185instructions5084bytes disk/live exact. Inventory889,372 evidence paths,126 unchanged asset hashes. No UI input; game still at prior red-signal failure alert. No running jobs. Next restore a controlled activity run with early player braking, trace AI profile-change cause and continue broader infrastructure/system discovery. Findings after9f9d445 remain local.

## Service efficiency sources checkpoint

Inventory890 (296direct,19derived,68cab,507config),376 evidence paths,126 asset hashes unchanged. SERVICE-EFFICIENCY-FINDINGS.md resolves baseline204/effective208 selection and selected-record34 override; installed004069aa changes baseline lower clamp to0.005 by return rewrite, override skips clamps. Paused three-service sample baseline/effective0.75 with null selected records; parser binding remains open. Pass140/142/143 disk/live exact;pass141literal scan exploratory. No running tool jobs or UI changes, game remains paused73903.4375 at failure alert. New findings after published9f9d445 remain local. Next restore controlled activity with early player braking, pursue AI/infrastructure transitions and unresolved source bindings; full discovery remains active.

## Ordered service-record discovery checkpoint

Inventory891 (297direct,19derived,68cab,507config),379 evidence paths,126 assets unchanged. SERVICE-EFFICIENCY-FINDINGS.md now describes service30 list, progress selector005a51ad and paired-track-item length helper005a55e4. All three live lists empty; selected/previous null. No populated timetable interpretation claimed. Pass144/145 disk/live exact. read_service_records.py and immutable service-records-paused-01 preserve extraction. Need a populated passenger-stop activity and loader trace for schedule semantics; this is an additional candidate surface, not complete schedule extraction. No UI actions, no running jobs, game still paused73903.4375 at failure alert. Publication remains9f9d445;891 local findings pending coherent checkpoint. Full broader research goal active.

## Service-file and station-stop loader checkpoint

Baseline Efficiency now bound to SRV token40411/service204 with constructor default0.75. Ordered service30 records are28-byte StationStop records:0PlatformStartID,14DistanceDownPath,1cuint16SkipCount,24default efficiency. Activity merge/timestamps still open. Native labels match disk/live;pass147-149 verified. Morning in Maryland installed activity is chosen next nonempty test candidate:platforms962/1510,efficiencies0.75/0.289063. Asset hashes preserved in service-token-map.json. Inventory891,383 evidence paths,126 original assets unchanged. No gameplay input; failure alert remains73903.4375. All tools finished. Further loader/live validation and full broader discovery scope remain; new findings not yet published after9f9d445.

## Populated station records live checkpoint

Morning in Maryland loaded;PID7160paused28809.5703125stationary/brakes applied. Player two records,AI lists empty. Platform/SkipCount/efficiency matches confirmed;first record selected0.75,second0.289063populated but effective transition untested. Distances differ slightly from assets;record04/0c match declared arrival/departure numerically only,08and1e suggest mutable state needing writer tracing. maryland-record-comparison.json preserves exact deltas and assets. Inventory891,386evidence paths,126original hashes unchanged. All jobs terminal. No save overwrite. Next station timestamp/state writers and boarding/selection transitions; remaining full goal intact. Publication remains9f9d445;pending local findings after it.

## Station event-time checkpoint

Inventory893 (299direct,19derived,68cab,507config),388evidence paths,126asset hashes unchanged. STATION-TIME-FINDINGS.md maps player record08 arrival and10departure clock writes;08also copies scheduled04 under special branches, so not universal actual arrival. No departure transition yet. Native path callback rebuilds record14distance, explaining a possible source of observed differences without claiming complete numerical reproduction. Pass150-152disk/live exact. No UI action;game remains Maryland paused28809.5703125. No running tools. Next schedule loader and controlled boarding/departure observation; broader scope remains active. New local results after9f9d445 pending publication.

## Scheduled station-time mapping checkpoint

Inventory895(301direct19derived68cab507config),390evidence paths126assets unchanged. Record4scheduled arrival,c scheduled departure now traced from labelled tokens through005a1656 and merge005a102e. Matching platform+skip first,distance +/-1fallback;both Maryland entries match schedule. Dispatch data disk/live verified,pass1532600instructions9458bytesexact. Scheduled4/c distinct from recorded8/10. No UI changes or running jobs;Maryland paused28809.5703125. Next controlled station-state transition and publication of coherent pending AI/station findings;full broader discovery scope stays active. Latest published9f9d445 remains unchanged.

## Station cue transition checkpoint (latest local)

Inventory898 (304direct19derived68cab507config),394evidence paths,126original asset hashes unchanged. Published checkpoint651591a on draft PR9 contains the earlier895 candidates; this new station observation remains local pending the next coherent publication. `read_station_series.py` and `analyse_station_series.py` preserve2343 samples across baseline and two overlapping captures,0errors. First stop flags changed0x22->0x62 across scheduled departure28811 while speed, boarding timer and recorded departure remained0. Native branch identifies a departure-cue dispatch-attempt latch, not actual departure or proof of audible cue. Candidate boarding fields are native-traced but only sampled at zero. Intended departure test did not move the train; cab drag attempts ineffective, one brake key reduced67% to65%. See STATION-TIME-FINDINGS.md and station-transition-summary.json.

Pass1541080instructions3996bytes has0disk mismatches but5live instruction-range mismatches in extra caller00586293; directly used station processor, dispatcher and selection advance match. No blanket byte-equality assertion. GamePID7160 remains Maryland paused28919.865234375, stationary, brakes applied, first stop selected0.75; no save overwritten. All tool jobs terminal. Next capture departure/next-stop selection with reliable keyboard controls, then nonzero boarding countdown; AI stops and broader full discovery remain open. This is progress, not completion or a blocker.

## Station successor and inventory consolidation checkpoint

Pass1555functions930instructions3184bytes match disk/live.00690280 selects first record for null input,otherwise the next record after the first matching identity;empty/end/missing identity return null.005a5254 preserves previous38 and clears cue bit40 on the new selection. Null alone does not establish route completion. Offline five-case model in station-successor-model.json is explicitly not a live transition. Three service inventory entries now remove stale empty-list/unknown-loader caveats;898candidates,396evidence paths,126original hashes unchanged. No UI input or gameplay modification,all jobs terminal. Last observed game state remains paused Maryland28919.865234375;live departure/boarding still open. Local work after published651591a remains pending next coherent PR9 checkpoint. Full discovery goal active.

## Coupling geometry checkpoint (latest local)

Inventory900 (304direct21derived68cab507config),402evidence paths,126original hashes unchanged. COUPLING-GEOMETRY-FINDINGS.md and read_coupling_geometry.py establish native solver endpoints and externally derived nonnegative endpoint distance,not signed slack. Paused capture28919.865234375 finds9player cars8connections,approximately0.14942..0.15048m gaps,all pair checks stable,no physical AI. Stored1a0 is norm-derived magnitude for current-to-a8 connection;full runtime force reconstruction not validated. Spring helper's disabled damping branch leaves its output unwritten;captured blocks enable damping,so do not generalizezero for disabled mode.

Pass156/158/159 disk/live equal;pass157 has3live instruction-range differences only in additional caller006283c0 entry. Used transform/spring helper ranges match. Native writer0062ad6a remains known patched. No UI input,game writes or save overwrite;game paused unchanged and all export/capture jobs terminal. Next bind spring configuration and endpoint velocity,then dynamic compression/tension/AI observations;station departure/boarding and full broader goal remain open. Published651591a/PR9 still895;new900candidate work remains canonical-local pending publication.

## Coupling velocity checkpoint (latest local)

Inventory902 (304direct23derived68cab507config),405evidence paths,126original hashes unchanged. Native endpoint velocity is linear plus angular cross displacement; connection separation rate projects following-minus-current velocity along following-minus-current endpoint direction. Paused9-car/8-pair sample captures near-zero residual rates and zero angular velocities,not dynamic validation. Existing immutable capture scripts preserved. See COUPLING-GEOMETRY-FINDINGS.md for formulas and exact limits.

Pass160 failed because an unquoted PowerShell address parsed as Infinity;logs retained. Quoted pass160b completes with6live instruction differences only in two known patched caller entries;direct helpers match. Pass161 fully matches. All jobs terminal,no UI or gameplay changes,game verified paused28919.865234375. Next requires moving and nonzero-angular samples rather than further paused-zero captures;spring token binding,station tests and broad remaining goal stay open. PR9 publication still651591a/895;local902 checkpoint not yet published.

## Moving body-state consistency checkpoint (latest local)

Reused immutable vehicle-motion captures in analyse_motion_differences.py. MOTION-DIFFERENCE-FINDINGS.md documents moving AI/player orientation changes while stored angular velocity is zero;AI3875eligible changed-forward pairs (2266same-clock),player restart2881 (2339same-clock). Player restart position-derived versus stored velocity median discrepancy3.862m/s persists in same-clock subset;cause unresolved. These observations qualify six motion candidates and prevent claiming reconstructed native endpoint velocity equals actual endpoint trajectory velocity. Exact endpoint validation is impossible from these old captures because definition400/414 were omitted.

Inventory remains902,407evidence paths,126original hashes unchanged. No raw capture or game/UI changes;all analysis jobs terminal. Next capture complete body/definition/track inputs during movement and resolve coordinate/integration timing;station and wider research goals remain open. Last observed game remains paused Maryland28919.865234375. PublishedPR9 still651591a/895;local902 research pending coherent publication.

## Motion time-base and AI reset checkpoint (latest local)

Wall-time reanalysis leaves player-restart velocity discrepancy median3.930m/s (simulation-time3.862),so changing elapsed-time fields alone does not solve it. Pass16210functions1829instructions7111bytes match disk/live. AI005a7337->00636475->00628d09 path rebuilds track body placement and clears angular momentum;subsequent005fd74f multiplies body64 inertia by body58 momentum into body94. This explains a native route to changing orientation with zero angular velocity. Exact execution frequency/alternate player paths remain unproven. angular-reset-provenance.json confirms current reset vector zero and all9944archived AI angular momentum/velocity observations zero.

Inventory902,409evidence paths,126original hashes unchanged. No UI/game writes;verified pausedMaryland28919.865234375,all jobs terminal. Next needs complete moving body/definition/track capture and player coordinate/integration investigation,not another clock-substitution or paused-zero check. Station tests and broad goal remain active. Local findings after651591a remain pending publication to PR9.
