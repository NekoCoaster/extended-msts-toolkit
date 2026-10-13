# Manager list placement survey

The five lists searched by the generic removal helper are not five proven vehicle categories. Their pointer/count pairs are at manager offsets0/4,8/c,10/14,18/1c,20/24 (hex). The physical vehicle and train lists at18 and20 already have runtime evidence; the first three need separate type and applicability validation.

Focused pass226 traces004fdc03,004fe734 and004fc186:527instructions,1772bytes,all matching disk and the restarted process's live image. In004fdc03, when object+18 bit4 is clear, bit80000 selects manager+8 if set, or manager+10 if clear. The inserted node payload is object+4 (object-table index). Successful insertion increments the corresponding count and sets bit4.004fe734 performs the same list choice through global7bdecc. Neither route assigns meaning such as “detached wagon” to the destination list.

004fc186 contains a path that removes an object and appends it to the other list when bit80000 changes, then updates that bit. Its surrounding interface/editor context and all applicability branches are not fully traced. This demonstrates that list assignment can change for an existing object; it is not proof of a vehicle coupling, creation or physics transition. The meaning of80000 remains raw. No new candidate is added solely from this unvalidated placement flag.

`read_manager_lists.py` prepares a bounded five-list survey for a loaded session. It records list counts, object table indexes, pointers, first-word class indexes, reciprocal links and selected rereads. It intentionally does not decode arbitrary members using wagon, train or body offsets. Bounds of16384nodes per list and100000table indexes are research limits, not native maxima. Same-time and stable-pointer results are not atomicity guarantees.

The first attempted observation after resuming research finds a new process,PID33612,with the supported disk hash,clock43200,player0 and manager0. The retained `manager-unavailable-after-restart-01` records `available:false`, reason `manager_null`, and `lists:null`. It is unavailable simulation state, not five empty lists or zero vehicles. Previous process7160 pointers and paused activity state must not be reused. The probe's populated-list branch has not yet been validated live; existing physical/train probes remain the validated narrow paths.

No game UI input, process writes, save changes or new activity was requested by this survey. The next useful experiment is a loaded manager snapshot, followed by class/producer validation for the first three lists; a positive detached/static fixture is still required for that coverage claim.

## Follow-up validation and rejected shortcut

`test_manager_lists.py` passes five synthetic checks: unavailable manager versus available empty lists, object-table resolution without vehicle fields, non-sentinel cycle rejection, and retention of stored-count disagreement. These test the Python traversal and result distinctions only. They do not establish that every native list member has the assumed layout, or validate the populated branch against the live game.

Pass227 examines two candidate count-incrementing append routines004463ae/0047657b and their registration callers00445d78/0047429e. All499instructions/1577bytes across four functions match disk/live. Both append object+4 to a caller-supplied pointer/count pair and are registered as method0x73 on distinct classes. This does **not** identify the supplied pair as the simulation manager's first list; treating the matching offset0/4 pattern alone as that proof would be incorrect. The first list's specific producer remains unresolved. No new telemetry candidate follows from this shortcut.

The live test attempt observed Marias Pass > Grain Train Through the Night selected in the current MSTS window. The Start action failed with `failed to activate captured window`; refreshing the returned window and attempting activation once also failed. UI input stopped at that point. The user was asked to foreground MSTS and start the selected activity, leaving its opening notebook visible. No successful load or populated manager survey is claimed from this attempt.
