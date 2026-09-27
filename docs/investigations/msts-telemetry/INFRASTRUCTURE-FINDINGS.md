# Complete route registry, track presence and signal associations

## Registry coverage and identity

Read-only snapshot `captures/infrastructure-paused-01/infrastructure.json`, simulation time 74525.53125, remained paused throughout. The circular list at [0x80a10c] contains database objects, not track nodes. Each database's +0 is a node-pointer array; +0xc is its inclusive last index. Native `0x5b9443` traverses this arrangement. Item collection is database+0x20, with pointer array +0 and count +8.

The one loaded database yielded all 732 nodes: 408 vectors, 246 junctions, 78 ends. Table index+1 matched every TDB node ID. `analyse_infrastructure.py` checked all node kinds and pin targets/directions, plus first geometry signature and section count for every vector. Zero discrepancies; the complete asset ID set was present. All 718 earlier geometry-derived matches agreed. This resolves the eight previous ambiguous runtime nodes and reaches the six nodes in disconnected track components. Those earlier capture limitations remain historically accurate but are no longer the current enumeration limit.

Registry indexes provide a route-build-specific join, not proof of an embedded stable native ID or persistence across edited assets/reloads. Null slots and database lifecycle must still be handled in general readers.

## Track-presence records

Vector node+0x2c is a circular list of abstract car-position records. Native `0x5d04d3` removes a supplied record and clears/frees an empty list; service cleanup `0x5a80e6` calls it for records in the service's per-car list at +0x12c. These structures differ from instantiated physics vehicles.

Observed records: +0 track-node backlink, +4 distance candidate, +8 configuration reference, +0xc service pointer. All 78 node backlinks agreed and all service pointers matched loaded services:

| Route node | Service | Records |
|---|---|---:|
| 305 | Player (0) | 23 |
| 281 | Later AI (3) | 55 |

The later AI still had no physical train instance. The inactive first AI (2) had no observed presence records. This supports a service-level representation of track presence independent of physics instantiation. It does **not** yet establish track-block occupancy, whole-train overlap extents, detached-vehicle coverage or the position reference used for each car.

## Signal association

The database item registry yielded 292 kind-zero signal objects. Seven had nonnull service+0x24 associations: four to the player and three to later AI. All seven references joined to the service registry. The remaining 285 were null. Null is not equivalent to clear aspect or permission to proceed.

Native `0x5c4ecf` requires an existing association to match the supplied service before clearing it. On success it clears signal flag bits 0xe000 and the service pointer. `0x5bfdf0` visits the database signal items to release those belonging to the departing service. Acquisition logic, exact reservation meaning and dynamic state transitions remain open; the inventory deliberately calls this a service association.

Other observed item kinds/counts: 2/1, 3/100, 4/593, 6/226, 7/180, 8/545, 9/3, 10/1030. Their subtype names and payloads remain to trace; do not infer names merely from counts.

## Verification and rejected interpretations

Pass35 exported 120 functions because the global registry has many references. The central checks used only the relevant registry and cleanup functions. All 19,067 exported instructions matched disk; one live call mismatch in 0x494850 is the previously observed installation hook. Registry traversal 0x5b9443, list removal 0x5d04d3 and signal release 0x5c4ecf individually matched live bytes without errors. This is not a claim that the live installation is stock MSTS.

The first investigated cleanup call 0x5bc576 initializes a path iterator; it is not itself a reservation-release operation. The investigation followed the separate cleanup chain instead. No switch was thrown, service changed, process memory written or NEMT production code edited.
