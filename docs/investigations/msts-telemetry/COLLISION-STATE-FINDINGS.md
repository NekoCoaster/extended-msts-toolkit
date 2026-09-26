# Collision-state applicability observation

An unexpected continuation after the previous red-signal failure supplied a useful off-track snapshot. Clicking OK on the failure alert resumed simulation; it did not immediately leave the activity. The next observed view showed the player and opposing train collided/derailed. Escape paused the simulation. The impact interval was not continuously sampled, so no exact collision time, causal sequence or peak impact force is claimed.

`post-red-collision-01` records the still-running aftermath; `collision-paused-01` and `collision-track-paused-01` both read paused clock73917.6015625 and origin(-12559,14766). The latter pair have matching car/body identities and stable origin. `analyse_collision_state.py` reproduces the cross-surface comparison and retains source hashes.

| Physical registry | Player400007 | AI400005 |
|---|---:|---:|
| Vehicles |23|22|
| Native derailment flag set |23|19|
| Native resting flag set |0|18|
| Both flags set |0|18|
| Nonzero angular velocity and momentum vectors |23|1|
| Maximum angular-velocity vector magnitude |0.3358801|0.1736596|
| Maximum body/track position separation, metres |69.092474|26.971919|

All45stored track section pointers still satisfy the node-array/index relation. Readable, internally consistent track references therefore do not prove that a derailed vehicle's physical position lies on that track. The difference includes the normal body-versus-track reference distinction as well as post-derailment divergence; it is not a universal correction offset. Existing physical-body and track-position candidates must remain separate, with derailment state attached to interpretation.

The18AIvehicles carrying both bits demonstrate that resting and derailed are not mutually exclusive native flags. Positive angular-vector values expand coverage beyond earlier zero-state observations, but do not independently establish angular units, coordinate frame, inertia mapping or exact integration behavior. Basis lengths/dot products are retained in the summary without asserting a new angular convention.

The running post-collision evaluation snapshot has active speed-episode state1, start73895.1875, stored limit0 and peak-adjusted-speed12.05484867, but no completed speed records and no operational-error records. This reinforces the distinction between active episode state and completed lists. It does not assign an untraced failure/error code or prove whether every collision should create an evaluation record. The speed episode started before the captured collision aftermath.

No candidate quantity was added;inventory remains1015. The normal UI actions changed gameplay only. No process writes, original-asset changes, or save overwrite occurred; the earlier saved stationary fixture remains available. The collision session was exited after preserving the evidence. A subsequent original-N2 approach is documented in `MOVING-PLAYER-ORIGIN-FINDINGS.md`; it also reached the red signal before clearance.


On the evaluation screen after exit, the UI reported one speed-limit exceedance lasting22seconds and failure due to derailment. The additional `collision-exit-evaluation-01` snapshot has active0, completed count1, total duration22.4140625 and one record with start73895.1875, duration22.4140625, limit0, peak-adjusted-speed12.05484867 and subtype0. The duration equals73917.6015625 minus73895.1875 exactly. Operational errors remain0. This demonstrates active-to-completed episode finalization around activity exit, with UI duration corroboration; it is not a new generic collision-event code. The running snapshot was taken0.2109375seconds before the final paused clock, so it does not bracket the exact finalization instruction.
