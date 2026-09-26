# Crossing and sound-region surfaces

Native dispatcher005bafc0 calls item-specific handlers with a service and a distance-derived interaction state. Exact entry/overlap/exit naming remains unresolved. This checkpoint discovers candidates, not audible playback or visible barrier validation.

## Level crossings

Handler004d7e0c reads item+8 as an index into generic object table[828108], stride8. With a linked crossing object, it combines absolute service speed, interaction state and distance with object timing/distance fields+74/+78/+7c/+80/+88. It aggregates a request at object+90: computed values0..4, including special transition3->4 and maximum-like combination for other requests. These enum values are not yet mapped to physical animation phases. Object+84 flags8/10 participate in player-specific warning logic; function004d5e90 and random/evaluation handling remain to trace. Service traffic can affect this handler without requiring a physical train; some player-warning branches do require one.

Snapshot captures/track-interactions-paused-01 has180 crossing items; every item+8 is0. Thus no live crossing request/flags were readable here. This means unavailable world linkage, not open barriers or zero traffic. Do not fabricate a state from absence. Future test needs a location with a loaded crossing, and its object-update/animation consumer must be traced before assigning state names.

## Sound regions

Handler004ef178 runs only with a physical train and nonzero item+8, with another global gate[7c32cc] clear. It uses linked object orientation when available, otherwise an angle at item+2e. Sound-region index is uint32 item+2a (unaligned). Train+ea points to a state structure: float+0 is a reference-distance candidate; float+4 is the current nearest-distance candidate; uint32+8 is the selected region; pointer+0xc leads to records of stride12 indexed by region. Record+0/+4 receive sound-system handles, +8 receives timeGetTime milliseconds during interaction states1/2. The nearest-distance comparison can replace state+4 and selected index+8. Exact reset cadence, table bounds, handle lifetime and audible behavior are unresolved; this probe intentionally does not traverse the unbounded handle table.

The paused snapshot read1030 sound-region items with region indexes{0,1,3,4,6,7,8,9};10 had loaded world objects. Player state was nonnull: reference candidate8.685937881469727, nearest candidate455.2000732421875, selected region0. These are readable retained values, not proof of current audible sound. No physical AI exists at this checkpoint, so independent AI sound state remains unvalidated.

## Reproduction and evidence

`python probe_track_interactions.py --pid 7160 --name track-interactions-paused-01` produced1210 item records, zero read errors, one physical train state, unchanged simulation time74525.53125. The capture directory preserves the reader dependencies and hashes. Script refuses an existing capture directory and uses only QUERY_LIMITED_INFORMATION|VM_READ. Original game assets were unchanged.

Pass51:5 functions,709 instructions,2587 bytes; pass52:7 functions,485 instructions,1637 bytes; all exported bytes matched disk and live memory with zero errors. The pre-dispatch callbacks004d7e01 and004ef16d are no-ops, not state-reset evidence.

Six candidates are added with scoped confidence: crossing request and raw flags (native-traced but live unavailable); sound-region item index and three per-train selection fields (paused readable, transitions untested). Follow-ups include actual crossing animation, warning semantics, audio table lifecycle and selected-region changes, plus pickup/hazard handlers already located. This checkpoint remains local pending publication to PR9.

## Pickup and hazard follow-up

Pickup handler004dcc7f receives a physical train, not a service pointer. Dispatcher005bafc0 calls it only for interaction state1 with service+158 nonnull. It iterates train cars through+62/+a8; each vehicle definition+7d4 supplies intake records. Intake type+0 must match the linked pickup object's+90. Intake distance tolerance+8 and linked object's speed bounds+88/+8c are compared against geometry-derived distance and train speed+92. Stricter bounds set item+2c bit8; broader bounds set bit0x10. Both write the candidate car pointer at item+34. Actual transfer/remaining capacity is not established by this eligibility scan.

Before scanning,004dcc65 clears bits8/0x10 with maskffffffe7. It does not clear candidate pointer+34. Thus a pointer alone is not evidence of present eligibility; account for scan timing, flags and object lifetime. The actual refill command, resource quantities and pickup enabled state still need discovery.

Hazard handler004d3a19 likewise receives a physical train. It resolves the item+8 world-object index and returns if absent. It uses the first or last car according to train speed sign. Conditional branches write world+0xb0 to5,7 or9 and latch byte+0xcc to1; state+0xac is compared against9. These numeric states are not yet identified as animation names. A branch copies world+c0 to+bc. The called helper004d5e90 reads a locomotive-system-dependent control field (+378 or+1d4); naming that control requires checking its producer and locomotive enum, particularly before assigning AI meaning from the shared controller wrapper. Hazard response reset and animation consumption remain untraced.

Capture pickup-hazard-paused-01 expands the probe to1804 items:1 pickup,593 hazards,180 crossings,1030 sound regions. Zero errors; simulation time unchanged at74525.53125. Pickup item1545 has world index0, eligibility flags0 and candidate pointer0. All593 hazards have no loaded world object. This validates absence/readability only, not a hazard reaction or pickup operation. Original track-interactions-paused-01 and its script copies remain preserved.

Pass53:5 functions,493 instructions,1651 bytes; pass54:8 functions,654 instructions,2207 bytes. All exported instructions match disk and live memory with zero errors. Five further candidates bring inventory to763; all preserve explicit live-validation gaps. No NEMT integration, gameplay writes or field prioritization occurred.

Publication note: this report and its standalone probes are included in the current research-branch checkpoint. Earlier local-only notes above describe the stages before publication. Raw captures/native exports remain local and are listed in local-evidence-manifest.json.
