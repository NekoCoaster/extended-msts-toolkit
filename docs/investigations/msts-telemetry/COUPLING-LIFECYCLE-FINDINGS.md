# Player coupling and loose-stock separation

Completed 2026-09-28, independent research only. This closes the representative player/loaded-loose ownership transition experiment, not the major telemetry goal.

## Experiment and observations

Marias Pass > Setting Out Westbound Pickup, yard_one.act, PID33612, executable SHA256 2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843. Normal UI controls moved the GP38-2 back past the turnout, selected the five-car siding, approached at low speed, coupled, stopped, then detached through F9 Train Operations. Process probes used QUERY_LIMITED_INFORMATION | VM_READ only.

The final capture has2397samples,0read exceptions,nominal0.25s wall interval over600s. Two separate preliminary maneuver captures each have720samples/0exceptions. Their streams are not joined across gaps. The first reverse probe lacks origin fields; do not infer world motion across rebases from that stream.

| State | Player chain | Outside train chains | Target owners |
|---|---:|---:|---|
| Before contact | 1 | 39 | 0 |
| Coupled | 6 | 34 | 63073680 |
| Detached through F9 | 1 | 39 | 0 |

The stored physical-list count remains40 in every final-capture row. Five target IDs200057..200061 retain their object addresses through both edges. Player ID200000/address63322752 and train ID400000/address63073680 persist in this run. Target end63653204 gains link63322752; player gains reciprocal link63653204. Both links return to0 on separation; the five-car internal chain remains linked. This directly validates ownership and chain membership independently from physical-object existence. Do not treat null ownership as invalid vehicle telemetry.

Sample brackets (simulation seconds, not native event timestamps):

- Coupling: row1600 at40276.53125/end40276.53515625 -> row1601 at40276.62109375.
- Separation: row1785 at40340.64453125/end40340.6484375 -> row1786 at40341.0.

Target turnout54015008 was selected to branch0/node112203216 in the paused target snapshot. Player subsequently entered that node. Original player branch was112890136; connecting vector112890200 required backing past the turnout before selecting the target branch. G/Shift+G operate relative to the engine; do not blindly reuse coordinates or maneuver durations after reload.

## Read validity and limits

Stable registry roots/counts alone are insufficient: rows240,911,1011,1614,1814 contain39readable cars instead of40 and outside counts briefly drop by1. These do not demonstrate physical removal. There are845full-read clock crossings,8unstable car subreads,142unstable body-pointer subreads,0origin reread changes and0root reread changes. The detail-only same_sim_time flag does not cover the later registry/track reads. Reject or qualify incomplete/racing snapshots.

Body addresses alternate during play even while object identity persists. Do not cache a body pointer as vehicle identity or claim body-address retention from object retention. Transition endpoint ownership/link evidence is corroborated by subsequent persistent states and the six-vehicle then one-vehicle F9 display. No exact coupler force/slack, collision callback invocation, activity completion, AI coupling, remote loose-stock lifecycle or save restoration is established here.

## Reproduction and retained evidence

Run `python analyse_coupling_transition.py` in the canonical research directory. It checks both chain transitions, target owners and object-address retention and writes coupling-transition-summary.json. See capture_coupling_transition.py and each capture's copied readers/metadata for the exact read-only probe.

- captures/yard-coupling-maneuver-01/samples.jsonl: final ownership sequence.
- captures/yard-reverse-approach-01 and yard-forward-return-01: preliminary movement captures.
- captures/yard-reverse-turnout-01/topology.json: running, not same-clock.
- captures/yard-reverse-stopped-topology-01/topology.json and yard-target-turnout-01/topology.json: paused topology.
- captures/yard-final-save-01: new save copy, all save hashes and final paused snapshot.

Final paused snapshot40371.26171875,speed0,one player engine,39loose vehicles. Idle,Forward,train brake released,independent brake25%. New save C:/MSTS/saves/USA2/yard_one_28092026_012813.sav (154215bytes,SHA256 9e474fed0fd5313c658e4386e5b84a340c509875d3dfe2095fec5595d31dd3b9); UI confirmed success, restoration untested. Both retained grain saves remain hash-identical. Simulator left in Escape pause menu. All addresses are session-local.
