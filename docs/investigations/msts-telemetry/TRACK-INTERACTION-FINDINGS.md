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

## Sound table lifecycle follow-up

0060806f allocates the16-byte train+ea state and a region table of [7c2e88]*12 bytes, zeroes it, and creates two handles for region0. 00609713 releases nonzero handles and clears them before freeing state/table storage. Exact ownership after destruction still requires pointer-lifetime checks.

00608800 iterates that same global region count. It retains region0 and the currently selected region regardless of timestamp. Other records are retained when unsigned32(timeGetTime()-record+8)<=10000; otherwise both nonzero handles are released and zeroed. The assembly uses CMP0x2710/JBE. This is a Windows multimedia timer tick, not simulation time, and subtraction wraps at32 bits. Cleanup only happens when this function executes; do not promise a ten-second wall-clock expiry during pause or when updates are gated. Exact invocation cadence remains untraced.

At its end,00608800 resets nearest-distance state+4 from train+aa. The same function derives train+aa by summing definition+400 over current cars. Thus state+4 is a search accumulator/reset value, not always an actual nearby boundary distance. It also writes state+0 from calculated train geometry; its physical interpretation remains a candidate.

The expanded probe bounds the region count at4096, reads only12-byte records and does not dereference the opaque handles. Capture sound-table-paused-01 found count10, region0 handles7065/7066, all other handles0, and all timestamps0. This agrees with default allocation but proves neither current playback nor actual expiry. The snapshot still had1804 items, zero errors, unchanged simulation time. Historic captures retain their original script versions.

Pass56 checked4 functions/1037 instructions/4407 bytes, all matching disk and live memory. Pass55 was a rejected byte-pattern lead into an unrelated dialog function; no telemetry inferred from it. New candidates are region table count, per-region handle pair and last-interaction tick, bringing inventory to766. These updates remain local after published commit285a0ff.


## Interaction distances and state predicates, 13 October 2026

005bb2bb refreshes each per-service interaction record before005bafc0 dispatches it. Record+4 receives old+8;new+8 is005babf0(service+4c,item). Record+c receives old+10;new+10 is005babf0(service+b4,item). Thus these are previous/current paired endpoint distances,not four unrelated counters. The updater uses a2000distance culling threshold,or1000for item kind10,with previous-distance sentinel and direction-trend conditions;this is work-list lifetime logic,not a restriction range.

005babf0 converts item tile/local x,z to the current origin through005bb43b (tile delta*2048 plus item local14/18). It fills the middle coordinate from endpoint+4c,then subtracts that vector from endpoint+48/+4c/+50. For finite inputs the middle component cancels,so the resulting norm is horizontal straight-line distance,not along-track distance or full3D separation.005bb54f sums three squared components;005bb4e1 rounds the sum tofloat32;005bb4fd reconstructs an approximate norm using exponent/mantissa bits and initialized table82b630. Do not replace it with exact sqrt for bit-exact reproduction. Current table contents and exceptional domains were not captured in this follow-up.

For ordinary finite values,005bafc0 selects state1 when both current distances record+8/+10 are strictly below service+128. Otherwise state0 applies when either previous endpoint distance(+4/+c) equals sentinel-1 or current first distance equals its previous value. Remaining cases select state2 when first distance decreases andstate3 when it increases. It also passes the smaller current distance to the speedpost/crossing/pickup-related handlers. These are proximity/trend predicates,not proof of exact entry/overlap/exit or a node crossing. Service+128 remains an unqualified threshold here. Existing004f5862 consumes state1;independent initialization calls can also establish retained caps.

Fresh evidence: track-interaction-update-20261013-01 verifies123instructions/384bytes;track-item-distance-20261013-01 36/101;distance-helpers71/194;distance-norm46/131;interaction-dispatch229/691. All match installed disk and PID39096,zero errors. The-1constant is separately disk/live verified in dispatcher sentinel.json. This is static native dataflow,not a live event transition or complete writer/caller survey.


## Bounded interaction-record snapshot, 13 October 2026

read_track_interaction_records.py traverses the registered item groups at80a01c and their per-service lists with cycle/node/total bounds. It retains previous/current endpoint distances,service128 threshold,and a conditional finite-value state. Root,list links,group pointers,record bytes,threshold and clock are reread;failed global guards suppress all conditional states. Equal checks cannot exclude pointer reuse or in-place mutation. No native handler is invoked.

track-interaction-records-20261013-01 contains180records at paused64965.1015625,same before/after clock,all guards pass. Kinds:96sound-region,44speedpost,40crossing. Two service pointers occur:8427664 has87records and threshold159.30001831054688;54806160 has93records and threshold144.49998474121094. All conditional states are0. This validates structural access in this fixture,not dispatch execution,an exact crossing,nonzero transitions or threshold producer semantics. Service128's writer remains unresolved:the inspected005a7821+128store belongs to a different record type and must not be used as service provenance.


## Threshold provenance and reader boundary tests, 13 October 2026

Initializer005a5eb1 passes service+128 in EDX and service+124 on the stack to thunk0040116d->005a635d at005a62d0. Helper005a635d traverses service+12c definition records,adds each resolved definition+400 length with a float32 store after each addition,and additionally adds definition+208 when byte+1e4 is nonzero and byte+1e5 mask10 is set. The complete sum is stored through EDX,therefore service+128. The second output service+124 receives a separately adjusted sum;it must not be substituted for the interaction threshold. Exact coupling-parameter label,all later writers and dynamic-consist refresh remain unvalidated here.

Fresh helper/caller verification covers377instructions/1583bytes,zero disk/live differences in PID39096. The explicit JMP thunk is independently checked in service-interaction-threshold-20261013-01/thunk.json because an unquoted PowerShell argument coerced its address during export. No missing export was counted as verification.

Seven synthetic tests in test_track_interaction_records.py pass:strict threshold equality and both endpoints,sentinel/proximity precedence,approaching/receding/unchanged states,nonfinite rejection,clock-cross suppression,changed-record suppression,and cyclic-list rejection. Tests validate extraction/model boundaries,not native runtime execution. The earlier180record snapshot is unchanged and remains all state0.


## Player and AI threshold reconstruction, 13 October 2026

read_interaction_threshold_inputs.py discovers service pointers from a fresh guarded interaction traversal,then reads cached service12c definitions without invoking006212fd. It repeats cache/list/definition/threshold/physical-train checks and clock checks;suppresses model/match output if guards fail. A null definition cache is unavailable and never resolved by calling native code.

interaction-threshold-inputs-20261013-01 at paused64965.1015625 matches both stored values exactly using float32 rounding after each native stored addition:player service8427664/train57038468 has8definitions and threshold159.30001831054688;AI service54806160/train69271584 has11definitions and threshold144.49998474121094. Every definition selects the extra208 term through the captured byte1e4/1e5 gates;player extras are0.1or0.15,AI extras about0.1. All guards pass. The physical-train join also identifies the two services in the previous interaction snapshot,without claiming atomic correspondence across captures.

This corroborates the initializer formula for positive length/extra inputs in both populations. It does not prove actual initializer invocation,negative/disabled-extra branches,live proximity transitions,or later coupling-refresh behavior. Definitions and physical bodies remain distinct objects;the service threshold must not be replaced with the simpler physical train definition-length sum.


## Threshold refresh callers, 13 October 2026

Fresh direct/thunk callers of005a635d show that service128 is not initialization-only.005adfae removes a definition record from its prior list,refreshes old service128/124 when record+c is nonnull,inserts it at a selected end of the destination service12c list,updates record+c,and refreshes destination128/124.005ae098 removes a record from its service list,inserts it into the separate list at its first argument+20,refreshes the previous service128/124,then clears record+c. These are static list-mutation refresh paths,not proof of a particular UI coupling event or timing. A snapshot between mutation and refresh can be inconsistent.

0060392e is a distinct caller:when the owning train+aa compares equal to the global constant752d0c,it sends train+aa as the primary output and a stack temporary as the secondary output,using the player train's service as input. Thus helper use alone cannot identify service128 writes. The ordinary00608800 train+aa producer remains the definition400 sum;this alternate call can populate the same train field from the helper's extra-inclusive sum. Its trigger's current constant value and runtime execution have not been independently validated in this follow-up.

service-threshold-callers-20261013-01 verifies6functions766instructions/2989bytes against disk and PID39096,zero mismatches/errors. Direct/thunk references are not an exhaustive indirect caller or writer survey. Exact coupling timing and post-change runtime threshold agreement remain open.
