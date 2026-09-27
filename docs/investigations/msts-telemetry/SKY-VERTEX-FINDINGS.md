# Sky buffer telemetry and paused animation

The current sampler follows the consolidated knowledge base's CPU vertex layout: layer draw object190, satellite draw object1b1, count+4, vertex pointer+8, vertex stride28hex, position0,diffuse18,secondary1c,UV20/24. Pass184 assembly confirms006e53c0 passes layer+24 or satellite+45 as shader context, vertex count in EDX and vertex pointer on the stack to006e1310. This resolves the misleading high-level call signature. It does not establish GPU visibility or submission completion.

## Retained failed experiment and correction

`sky-vertices-paused-01` completed61samples,all failed the original shader index guard; it contains no valid vertex snapshots. Diagnostic reads found satellite0 had one allocated frame but selected indexFFFFFFFF. Pass185 shows006e1070 explicitly initializes selected+0c toFFFFFFFF before loading frames. The correction preserves the raw index and does not dereference an unavailable current-frame record. It does not relabel the value as frame0 or silently discard the satellite.

The corrected preflight captured one valid sample. `sky-vertices-paused-02` completed61samples with zero read errors. Both captures preserve their different script copies; original evidence is unchanged. The analyzer also handles an all-error series with null clock/read ranges instead of crashing or claiming zero-duration success.

## Observed paused behavior

All61samples have pause flags1 at both ends and dayclock74360.5859375 unchanged. Stored delta00828fb4 remains nonzero,0.0080172000..0.0152434995. Complete read windows peak at0.001148300seconds; this is not a controlled performance-impact result.

Three layers have41,41,73vertices and two satellites4each. Layers0/2 change UVs in every one of60adjacent sampled pairs; layer1 and both satellites do not. The three layer shader+8values and satellite1's value increase2571.04541015625..2601.05615234375. Satellite0 stays0 with selectedFFFFFFFF. All other selected indices remain0; all frame counts1. Layer0first-vertex V moves13.3553237915->13.5054426193; layer2 moves13.8553667068->14.0054855347. Positions,diffuse andsecondary words are unchanged across this sample window.

Five shader-header rereads changed during collection. Structural/vertex-buffer identities remained stable. Thus pause does not make render data atomic, and same gameplay clock cannot certify coherent animation state. The observed advancement supports a render-side timebase distinct from the paused dayclock, but exact producer cadence, timer reset and wall-time equivalence are not proved.

Satellite0's retained first-vertex V is approximately1.68e-43, while its current-frame index is the parser sentinel. This is a validity warning: allocated memory and plausible geometry do not prove a meaningful initialized UV or current draw. Do not derive visible texture placement from it. Similarly a nonzero light pointer or retained diffuse white is not evidence that the satellite is active.

## Fields and boundaries

Twelve candidates add vertex count/array, local position, diffuse/secondary words, UV, shader frame count/duration/clock/current index/frame array and current-frame scroll pair. These are shared CPU sky buffers. Some describe loaded configuration, some mutable state, and some may remain stale when an object is inactive. The single current-frame record is read only when its index is in bounds. Rereads do not exclude ABA or changing vertex payloads.

Pass185 exports5functions1800instructions6109bytes,all disk/live equal. Parser selected-index initialization is established; update006e1310 branches between frame replacement and scrolling and uses delta00828fb4. Full clock producer/reset and complete animated-frame semantics remain open. Existing knowledge-base colour/fog rules are reused as context, not revalidated by unchanged colours at one night-time clock. No game controls, writes, asset changes or save changes occurred. All tool jobs ended. Inventory971;broader discovery remains incomplete.
