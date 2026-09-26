# Loaded layer geometry and time windows

The user identified `C:/codex/repo/msts-unity-kb` as the consolidated environment research source. Its clean revision512f180 provides current status, supersession rules and preserved native reports. It supersedes ad hoc navigation through the older handoff folders. No knowledge-base files were changed. `unity-kb-provenance.json` records the consulted files and hashes.

The knowledge base already documents sky draw order, layer fade behavior, UV updates, satellite transforms and colour/texture rendering. Reuse those results; do not repeat their experiments merely to restate the equations. Its historical native captures used another image and some time-argument substitutions, so current telemetry work still requires supported-build address checks, guarded reads and clearly scoped runtime validation. The status page also supersedes the old claim that omitted fog distance disables native scenery fog; do not revive it from phase19.

## Current capture and native checks

`read_sky_layers.py` reads three layer headers and four edge records, with pointer/count/header rereads. `sky-layers-paused-01` remains paused at74360.5859375 and all checks pass. Layers have top radius/height800/300,660/1000,800/800, face parameter8each and edge counts1/1/2. Edges are height/radius0/1500,0/1400,and500/1400 plus240/1650. Layer1 has fade-in64800..72000 and fade-out21600..28800; other pairs are zero-initialized.

`analyse_sky_layers.py` compares the explicit USA2snow.env declarations with the captured fields. All24 scalar/array comparisons agree. These checks include authored face counts8, but the inspected parser initializes8 and does not show a handler for the top-nfaces token in its top-block loop. Thus matching8 does not prove that declaration is consumed. Preserve the stored face parameter as a native field rather than promising configurable face counts. Geometry dimensions are multiplied by loader scale; equality with this file does not establish a universal scale1.

Pass182 established parser layout. Pass184 reexports the current sky renderer006e53c0 and shader update006e1310 with callers:5functions2604instructions8791bytes,all disk/live exact. The renderer reads four timing fields and writes vertex diffuse alpha during fades. Geometry vertices are a distinct output surface: count at layer194,pointer198,stride28hex,diffuse18,UV20/24. This matches knowledge-base phase06's draw-object description (layer190). Current opacity is not simply one of the four stored times, and zero timing pairs do not establish invisibility.

The UV update uses frame delta00828fb4 and frame scroll values; a frame-index change follows a different branch from scrolling. The decompiler's inferred arguments at the call site are incomplete, so register/assembly evidence is required before composing a sampler or exact update formula. Existing knowledge-base phase04 supplies a navigation lead, not proof that every current layer's shader fields were read this turn.

## Catalogue and next action

Eleven candidates cover stored face parameter, radius,height,edge count/array,edge height/radius and four time-window endpoints. Inventory959. These are loaded metadata and structure identities, not11 independently changing outputs. Their cadence/lifecycle and applicability are explicitly shared environment state. Probe bounds32layers/256edges are conservative reader limits,not native capacities.

Next use the already-recovered vertex/shader layouts to capture actual diffuse/UV values, and distinguish paused render updates from simulation updates. Reuse consolidated fog/sky findings before adding derived meanings. No UI input, process writes, asset edits or save changes occurred. All export/capture jobs ended; the broad goal remains incomplete.
