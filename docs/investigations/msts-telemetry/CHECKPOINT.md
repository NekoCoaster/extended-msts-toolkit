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

Current inventory has 193 direct-read candidates/structures, 16 derived candidates, 68 native cab channels (59 declared in installed cab files) and 473 configuration leaf paths, totaling 750 entries. This is **not** a count of confirmed independent live values. Pointers are useful extraction/identity metadata, static configuration is not dynamic telemetry, cab declarations are not proof that every field is simulated, and derived candidates still need validation.

## Test scenario and installation

The user's preselected process was PID 7160 at `C:\MSTS\train.exe`. Always rediscover the PID before reuse. It was on the route/activity selection screen; the selected activity was started normally.

Installed activity: `ROUTES/USA2/ACTIVITIES/evegrain.act`, displayed as **Grain Train Through the Night**, Marias Pass. The activity header says StartingSpeed 0, but `SERVICES/EveGrain.srv` specifies 11.176 m/s (25 mph). The actual initial cab displayed 25 mph, throttle N2; the first paused memory sample had throttle 0.25, reverser 1 and native control type 2. Do not use the header alone to predict starting motion.

Runtime player consist: 23 vehicles (two powered vehicles). The configured consist is `Dash921gran.con`. AI service `EveGrain (Traffic)` uses `2 x Dash 9, 20 Intermodal`, matching the observed 22-vehicle AI train. The later scheduled `EveGrain (Traffic01)` uses `D9gds`; its scheduled offscreen activation has now been observed, while creation of its physical train remains untested. The activity text's 30 grain cars and rain do not match this installed initial state: the runtime shows snow and the consist is smaller. Preserve these discrepancies; do not change assets to make them agree.

Disk executable SHA256: `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`. Clearing only the PE LAA flag produces `1b041ecf4b2d2a7306218efa1d7418fd87dc21dc4b2d00056cb5749084fe55a4`, the widescreen image recognized by current NEMT source. The reused Ghidra database is the original `69218fce876298c684a2140c7d3925a452c47bb10037ffd8c491f65c5c0c6e7a` image. Existing NEMT `docs/investigations/widescreen-background.md` documents a 108-byte original/widescreen difference. The offsets work in this live image, but byte-level validation of all newly traced functions is still outstanding; do not claim identical binaries.

The running installation already enables IgnoreRedSignal, PreventActivityEnd, EnableCrawl, CounterTilt and UnlockFPS. These settings were not changed. After derailment the capture is modified by the pre-existing NEMT runtime; it is not a stock-MSTS physics validation. The source repository at `C:\codex\repo\NEMT` remains clean at `5cd5896`.

## Direct findings

[Track-item findings](TRACK-ITEM-FINDINGS.md) identifies all 2,970 live item kinds and verifies stored platform, siding and speed-post payloads against the route file. Dynamic behavior and effective restriction semantics remain open.

[Infrastructure findings](INFRASTRUCTURE-FINDINGS.md) enumerates all 732 route nodes with validated route IDs, resolving earlier disconnected/ambiguous coverage. It also records 78 service-linked track-presence records and seven signal/service associations; reservation semantics remain unverified.

[Track topology findings](TRACK-TOPOLOGY-FINDINGS.md) adds a 726-node connected runtime graph, 246 readable junction selectors and 718 derived route-node matches. Disconnected components and switch transitions remain open.

[Track geometry findings](TRACK-GEOMETRY-FINDINGS.md) maps current section length, radius, angle, width, skew and flags for player and offscreen AI. Four geometry definitions match installed assets; straight-grade and nominal-curvature formulas remain explicitly derived candidates.

Latest checkpoint: [AI lifecycle findings](AI-LIFECYCLE-FINDINGS.md) records 539 samples, zero read errors, physical removal of the first AI and scheduled offscreen activation of the later AI. The first AI eventually retained positive speed with stationary track position; subsequent [scheduler tracing](SERVICE-UPDATE-FINDINGS.md) found its update gate disabled and last-update clock stopped. The precise deactivation trigger remains unproven. Game is paused at 74525.53125, player intact and stopped.

[Vehicle-system findings](VEHICLE-SYSTEM-FINDINGS.md) adds per-car pressure, requested brake force, coupling-force candidates and inertia. Session metadata is in captures/session-header-running-01/session.json; header parser offsets are relative to activity+4.

[Activity event findings](ACTIVITY-EVENT-FINDINGS.md) matches the three loaded location events to ACT definitions. Runtime activation/completion transitions and operational evaluation counters remain unverified.

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
