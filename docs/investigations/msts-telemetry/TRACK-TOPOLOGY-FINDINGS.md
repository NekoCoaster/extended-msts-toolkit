# Track topology and junction selection

Read-only investigation at paused simulation time 74525.53125, player intact; no switch operation or process writes.

## Distinct native layouts

Native kind at node+0 distinguishes vector segment (1), junction (2), and end (3). Vector records have inline endpoint pointer/direction pairs at +8/+0xc and +0x10/+0x14. Junction/end records instead hold input count +0xc, output count +0x10 and pin-array pointer +0x14. Each endpoint pin occupies eight bytes: linked node pointer then direction byte. Reading a vector as an endpoint produces invalid pointers; `read_topology.py` branches on kind and bounds traversal.

Junction +0x50 is the branch selector consumed by native `0x5b2fc5`. When entering through the input side, it selects pin `input_count + selector`; when entering from an output side it chooses input pin zero. This establishes the selected connection in this traversal path, not switch reservations, occupation, blade animation, route permission or a universal straight/diverging enum.

Pass32 exported traversal plus caller: 746 instructions / 2678 bytes all matched disk and live memory, zero errors. This is targeted instruction verification only.

## Live component and route comparison

`captures/topology-route-map-paused-01/topology.json` contains 726 nodes reachable from the three loaded service track positions: 406 vectors, 246 junctions, 74 ends. All links were reciprocal, all 246 selected connection indexes were within bounds, and simulation time stayed unchanged. This is not a transition test.

Installed `ROUTES/USA2/marias.tdb` has 732 nodes: 408 vectors, 246 junctions, 78 ends. `analyse_topology.py` independently finds connected components of sizes 726, 3 and 3. The two small components are IDs [287,290,296] and [370,371,372]. Thus the six-node difference is consistent with disconnected track. Their runtime objects were not located by this connected traversal, so full route runtime enumeration is still incomplete.

Geometry signatures (first section definition, tile, position within 0.005 m, section count) and connectivity yielded 718 unique derived node IDs. Eight runtime nodes remain ambiguous due to duplicate geometry and insufficient distinguishing adjacency. Two mapped junctions have partially unresolved neighboring IDs; those checks are reported as partial, not passed or mismatched. All fully resolved pin comparisons agree. `topology-summary.json` preserves source hash, mapping, ambiguity candidates and limitations.

Derived service track IDs in this route build: player 305, first AI 310, later AI 281. These IDs are inferred from assets and graph evidence, not found as a native integer field. Do not reuse the mapping across route edits or activity reloads without validating identities again.

## Follow-up

[Infrastructure findings](INFRASTRUCTURE-FINDINGS.md) subsequently locates all 732 registry nodes, validates all route IDs and resolves the eight ambiguous matches and disconnected components. The observations above describe the earlier connected traversal.

## Remaining validation at this checkpoint

Observe a real switch change, identify all topology object registries and stable native TDB IDs, resolve the eight ambiguous nodes, and locate disconnected components. Reservation/occupancy and authorization fields remain separate open investigations. A valid pointer graph or selected branch alone does not establish them.
