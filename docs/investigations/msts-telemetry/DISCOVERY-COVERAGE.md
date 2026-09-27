# Current discovery coverage review

Research is **active and incomplete**. This review follows the original objective without ranking candidates or selecting exports for NEMT. It supersedes the changing next-step statements in [the chronological coverage history](DISCOVERY-COVERAGE-HISTORY.md). Individual findings preserve historical observations; the generated inventory consolidates candidate metadata.

Current inventory: **1,037 candidates** (436 direct fields/structures,26derived,68cab,507configuration). Structured records may contain many values; cab/config/native records may overlap. Counts are not independently validated live quantities or proof that every extractable field has been found.

## Requirements and current evidence

| Requirement | Evidence inspected and established scope | Outstanding work |
|---|---|---|
| Independent research and preserved assets | Branch history, read-only probes, source manifest and extraction handoff. Prior native/Unity work supplies context; new runtime evidence remains distinct. | Maintain boundary through final delivery. No production integration or keep/drop decisions. |
| Session, clock and state | CLOCK, UPDATE-CADENCE, INTEGRATOR-TIME and SAVE-RELOAD-RUNTIME findings distinguish gameplay, physics and pause state. | Midnight/reset, full calendar interpretation, load-complete indicator and full restoration fidelity. |
| Player controls, instruments and engine systems | Native cab map:68channels,59found in installed declarations. Diesel, steam and electric findings separate producers and display conversions. | Extended cab caller contexts/reachability, some units and inactive cache validity. Labels alone do not establish support. |
| Trains, vehicles, physics and connections | Physical registry/lifecycle, vehicle systems, coupling and motion findings. Independent physical list matches23player+22AI connected vehicles. | Positive detached/static fixtures, identity reuse, unnamed force/default bindings and resistance interpretation. |
| Wheel and shape state | WHEEL-ADHESION findings:24locomotive wheel-node matrices plus164wagon wheel matrices cover all45physical vehicles in this scene. Ordinary rate feeds trigonometric rotation; powered phase can be ineligible; shape time can be an update marker. | Moving matrix cadence, coordinate meaning and broader shape coverage. Live hooked entries limit native-only conclusions. |
| AI services, paths, schedules and lifecycle | AI-SERVICE, SERVICE-UPDATE, AI-LIFECYCLE and AI-SYSTEM-UPDATE distinguish persistent services, abstract movement and physical appearance/removal. | Rephysicalization, reverse cases, populated station stops, driver reasons and force/brake applicability. Player controls are not AI controls. |
| Track location, topology and geometry | Track/infrastructure findings enumerate732route nodes and2970track items; two observations of one origin boundary retained. | Other origin boundaries, successful player node/speedpost crossings and broader grade/curve validation. |
| Signals, limits, switches and traffic | Signal/cab, speed-cap, infrastructure-owner and paired-monitor findings include22AI abstract-record crossings and ownership/branch changes. | Successful player signal passage, other aspects/functions and precise occupancy/authority meaning. Failed approaches are not successful crossings. |
| Activities, events, stations and evaluation | Event/evaluator, station-time and evaluation reports identify predicates, outcomes, schedule/recorded time, successor selection and cue state. | Actual outcomes, boarding countdown, departure/next-stop transitions and some evaluation writers. Null selection does not prove completion. |
| Environment and rendering | ENVIRONMENT-SELECTION, SKY-LAYER, SKY-VERTEX and SKY-CLOCK findings cover active selection, loaded layers/satellites, CPU buffers and paused render-side changes. | Inactive buffers, satellite validity, animated frame/wrap/reload behavior and weather/physics coupling. This is no longer an entirely missing surface. |
| Audio and input | AUDIO-STREAM/PENDING/NESTED and INPUT-BINDINGS/DISPATCH plus the retained short input test cover streams, queue/sample links, nested records, bindings and transient events. | Audibility, AI sound lifecycle, truncated traffic queue, peripherals and unnamed event words. Polling can miss brief events. |
| Beyond the initial examples | Serializer survey, complete header partition, object raw ranges and loader-fixup findings. Actual player reload changed23addresses while preserving tested IDs/poses. | Unnamed saved fields/subobjects, optional branches and physical-AI reload. Raw copied bytes are not a semantic schema or portable pointers. |
| Per-candidate metadata and reproducibility | Inventory has1,037unique IDs with required metadata. Current audit checks747evidence paths and126unchanged assets. Exact capture probes, byte reports and raw manifest retain provenance. | Structural checks do not prove each meaning/unit/lifecycle. Unknowns and disk/live differences remain explicit. |
| Handoff and completion | EXTRACTION-HANDOFF documents build/read-validity assumptions, raw-evidence access and reproduction. Published CHECKPOINT-VALIDATION records checks. | Access recipe is now present; the former missing-handoff statement is obsolete. Final semantic consistency and objective-wide completion audits have not passed. |

## Discovery gaps versus runtime validation

New-surface leads remain in unnamed saved engine subobjects/callback payloads, unresolved extended cab contexts, static/detached enumeration applicability, resistance/force meanings and raw action fields. Do not count serializer copies or callback aliases as independent quantities merely to grow the catalogue.

Already discovered surfaces need targeted runtime evidence: station boarding/departure, event outcomes, successful player signal passage, AI rephysicalization/reverse cases, wheel-angle/axis interpretation and reset/midnight behavior. These are not wholly absent candidate families. Further experiments should discriminate a stated uncertainty; repeating unchanged paused values does not close these gaps.

The objective is not satisfied just because the inventory is large or all evidence files exist. Completion also must not be redefined as reversing every executable byte. The final audit must demonstrate a bounded, comprehensive survey of realistically accessible gameplay surfaces, preserve unresolved leads and validate representative player/AI extraction with honest limits.

## Fixture and next work

Last capture: PID33612, paused1 at73871.1953125 after a normal-UI restart of Grain Train Through the Night/Marias Pass. UI was last observed in the exterior-view Escape pause menu;original Alerter option remains restored. Current physical count was not sampled by the monitor probe. Reobserve before input; this is historical state, not a guarantee that the user has not changed it.

The restart is earlier than the prior failed red-signal approach. Establish reliable braking before longer motion. Moving-transform captures now cover representative player/AI locomotives and wagons before/during/after motion;angle/axes/frame cadence remain open. Independently, remaining unnamed engine serialization subobjects provide further read-only discovery without advancing the simulator. Preserve assets and retained saves.

No completion or blocked audit passed. Previous wheel checkpoints were concrete progress, and further research is possible.

Safety-monitor follow-up: ENGINE-MONITOR-FINDINGS.md identifies AWS/vigilance/emergency-stop/overspeed state and expected definition links. Positive lead snapshot;trailing/AI links null. Countdown/update and configured action branches traced, including updates before enable gating;diesel interval traced to player scheduler with inherited seconds corroboration;player vigilance countdown/alarm/penalty now validated through UI-enabled capture;other monitor interventions and acknowledgement remain unvalidated. Unnamed slot57a is retained as an explicitly unnamed candidate. Opening runtime capture validates disabled overspeed input updates;vigilance timers remain unchanged,with suppressing caller gates observed after the run.

Alerter command registration/toggle semantics traced. Ctrl+numpad4 attempt did not change gates in1796samples;both suppression globals remained1. Use a different observed UI/eligibility approach for activation;do not repeat unchanged attempts.

UI-enabled Alerter test closes representative player vigilance countdown/intervention gap:1397samples,quarter-step decrements,alarm/action edges,brake pressure response and evaluation code2. Original option restored and verified after activity reload.

Wheel-matrix runtime follow-up:two280sample captures confirm moving stored matrices and paused stability for representative player/AI type4/type5 vehicles. Wagon context reread differences are retained;no exact angle/world-pose claim.

Body accumulator follow-up: guarded paused snapshot covers23player and22AI vehicles. Player forces nonzero,AI forces zero despite nonzero velocity;alltorques zero. Native resistance path adds into the shared force accumulator,so no dedicated resistance-force measurement is claimed. Moving cadence,decomposition,torque meaning and AI applicability remain open.
