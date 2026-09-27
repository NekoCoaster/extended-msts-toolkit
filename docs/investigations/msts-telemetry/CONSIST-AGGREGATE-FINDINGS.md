# Physical consist aggregates

Native00608800 walks the linked car chain starting train+62, updates train+66 to the last visited car, sums each definition+444 into train+9a and each definition+400 into train+aa. These are stored definition aggregates; train+9a is distinct in provenance from summing current physics-body inverse masses. Do not assume dynamic fuel/load mass is incorporated merely because a numeric total is readable.

The function also recomputes service class bits0x2/0x4 from physical car definition type2 (Freight). It recalculates train speed from per-car fields and updates additional accumulators; these need separate semantic investigation. Empty-car-chain behavior skips the body, so fields may remain retained rather than being reset to zero.

0060820c registers00608800 under numeric callback0x10 with argument1 via0060ded0. This is a callback registration, not direct evidence of frame frequency. The dispatch mechanism, pause behavior and post-coupling cadence remain unresolved. Do not describe recomputation as exclusively initialization or assume an atomic car/aggregate snapshot while moving.

Read-only probe_consist_totals.py independently accumulates each value with float32 rounding after each addition, mirroring stored float writes. Capture consist-totals-paused-01 sampled the intact23-car player at unchanged sim74525.53125. Definition mass aggregate2551687.0 exactly matched train+9a; physics-body mass sum was2551687.039209917 (small inverse-mass/rounding difference). Definition length aggregate455.2000732421875 exactly matched train+aa and the previously observed sound nearest-distance reset value. Last-car pointer agreed with the independently traversed chain. Freight class bits were4. No physical AI was available for this comparison.

Mass is consistent with the established kg physics surface; length is consistent with native metre geometry, but this checkpoint has not independently joined every car's definition field to its WAG/ENG source. Record these provenance limits. A changing consist and changes to load/resource mass remain untested.

Pass57:2 functions,720 instructions,2974 bytes, zero installed-disk/live mismatches or read errors. Raw source snapshot and dependency hashes are retained in the capture folder. The earlier pass56 verifies the aggregate producer too.

Two direct candidates added: definition mass sum and definition length sum. The existing derived physics mass total stays separate because it has a different source and potentially different load semantics. Inventory768 is still a discovery count, not768 independent verified live values. New work remains local after285a0ff.

## Installed-asset unit corroboration

Live inline UTF-16 definition names at+8 were Dash9 and US2GrainCar. The installed DASH9/dash9.eng declares Mass155t and Size3.594m/4.431m/21.8m; US2GRAINCAR/us2graincar.wag declares Mass106.747t and Size3m/3.5m/19.6m. Both masses converted from metric tonnes to kg and both third Size components converted to float32 exactly match captured definition+444/+400. Every car in this23-car snapshot uses one of those two definitions.

compare_consist_assets.py reproduces that explicitly scoped two-asset comparison and writes consist-asset-summary.json with source/capture hashes. It is not a generic asset resolver or arbitrary unit parser. This establishes kg and metres for the sampled aggregate sources and removes the previous two-definition source-join gap; it does not validate changing loads or every supported MSTS unit suffix.

Native parser00614c8e writes three Size components starting+3f8 (therefore length at+400) and numeric mass at+444;00628d09 initializes physics inverse mass as1/definition+444. Pass58 exported12 functions/9003 instructions/38377 bytes with zero disk/live differences. The general numeric unit-conversion implementation remains outside this scoped comparison; do not overstate the complete parser semantics from the decompiler alone.
