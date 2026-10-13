# Physical registration lifecycle

The independent list now has traced insertion and removal evidence. These paths qualify availability; they do not establish a universal load-complete indicator or positive detached/static-vehicle coverage.

In `0063258f`, the wagon setup first searches the manager's physical list by object+0x50 ID. If found, it returns. Otherwise, when object+0x18 bit4 is clear, it appends object+4 (the object-table index) to manager+0x18 through `0068ff80`. On success it increments manager+0x1c and sets bit4. This happens before the later definition/shape, track, connection and system setup in the same routine. That setup includes a failure path through `006334c0`. Thus membership and bit4 can precede completed initialization. They must not replace ownership/body/link checks.

`0068ff80` allocates or recycles a 12-byte node and inserts it at the circular list's tail, setting node+8 to the supplied index. This confirms that node+8 is an object-table index, not the vehicle ID at object+0x50. Object+4 equals the independently traversed index in all 45 observed vehicles.

The wagon teardown `006334c0` cleans resources, restores object+0x10 from +0x194 and dispatches parent method0x12 through `00691410`, using the class index in global80a7b8. The captured parent class index13 resolves to method target005e22f7. That routine performs further cleanup and dispatches method0x12 through parent index at7c0188. Captured index4 resolves to004fdd43. These are observed metadata plus traced dispatcher behavior, not invoked native calls.

`004fdd43` tests object+0x18 bit4, requests removal using object+4 and the supplied manager, then clears bit4. The removal helper004b6472 searches five manager lists at offsets0,8,10,18,20 (hex), paired with counts4,c,14,1c,24. On its first matching node+8 it calls00690040, decrements that list's count and stops. If none matches, it returns without decrement. The caller still clears bit4 after the request. Consequently a cleared bit is not independent proof of a successful removal, and counts need not identify a completed coherent snapshot during transitions.

`00690040` reconnects neighbors, clears node+8 and either adds the node to a shared free list (up to50 retained nodes) or releases it. Node addresses may therefore be reused without a new allocation. This is not a live-observed reuse event or a proof that every vehicle follows the same complete cleanup path. Other manager lists are new investigation leads; they are not yet decoded as static-vehicle registries.

The read-only `physical-registry-lifecycle-paused-01` captures clock73904.5 at both endpoints. Manager+1c is45 before and after, matching45 enumerated vehicles. All45have raw object flags4, bit4 set, self-index agreement and stable registry/class/body checks. Membership still equals the23player+22AI connected vehicles. This corroborates a stable registered state only: no insertion/removal, count change, detached object or bit transition was sampled.

Native evidence: insertion caller0063258f reuses verified pass217. Focused pass222 checks four functions,201instructions,680bytes; pass223 checks004fdd43,66instructions,209bytes; pass224 checks004b6472,83instructions,254bytes. All match disk/live with no read errors. Pass225 checks the unlink helper; see its byte-verification JSON for exact scope/counts. These checks cover exported instructions, not every indirect dispatch or entire gameplay pipeline.

Exploratory pass219 included an unrelated numeric-rounding function006347ba from an adjacent address and does not support lifecycle claims. Broad caller exports in pass220/pass221 were navigation; the focused pass222 supersedes them for byte-check claims. The exporter now supports `-NoCallers`, successfully exercised by passes222–225, to avoid broad generic-helper caller expansion. Default caller behavior is unchanged.

Two distinct stored candidates are added: manager physical-list count and object registration bit. Neither is an exporter validity promise. No game input, process write or save/asset change occurred; original capture files were retained and the enriched probe used a fresh directory.
