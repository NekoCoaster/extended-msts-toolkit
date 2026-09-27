# Player view and render-camera candidates

Native debug producer004918e0 tests [[007c2a88]+11c] against1,2,3. For these modes it reports TRACKING ON/OFF according to uint32+110; all other modes report NOT TRACKING regardless of+110. Assembly00491a25 through00491aa7 establishes the branch. Mode names are unresolved: CamType strings found in the executable are not sufficient evidence for a numeric mapping.

Render-camera global[00829224] is separate.006b63c0 replaces it and calls outgoing/incoming virtual callbacks; it can be null.006c0290 reads+30/+34/+38 as camera position and+24/+28/+2c as forward direction for precipitation. Prior precipitation reference_core.project uses basis vectors at+c,+18,+24 and position+30 for camera-space projection. This inheritance is corroborated by current native exports and a new external read; it is not a fresh projection replay. Do not confuse view-state+38/+40 used by debug tile calculations with this render structure.

probe_camera.py uses the existing hash-gated read-only Reader. captures/camera-paused-01/camera.json records sim74548.40625, pause1, mode0, tracking0, distinct view/render pointers, and stable pointers/time across the read. Position was(546.5737915,1104.0667725,512.9185791). Basis norms differ from1 by less than8e-8 and pairwise dot magnitudes are below4e-8. Those numerical checks support a plausible orthonormal basis; they do not prove world handedness, train attachment or camera mode names.

pass61 verifies4 exported functions,5091 instructions/20246 bytes; pass62 verifies66 functions,16682 instructions/57839 bytes. Both have zero disk/live mismatches and zero read errors. The second reference export followed a broadly shared callback function006bc050 as well as the render global; only the relevant consumers above have been semantically reviewed. Export volume is not discovery coverage. That callback lead does not establish a camera getter.

Four candidates are added: mode, tracking, render position and render basis. They represent the current player view, not an AI camera per train. Further tests must switch views, track a different vehicle, rotate the camera, inspect origin shifts and reload lifecycle, and trace projection/viewport fields and input-driven updates. No UI action, game write or save was performed in this pass. NEMT remains unchanged; this checkpoint is local after285a0ff.


## Live camera-switch follow-up

Normal in-game keys2,3,4,1 changed the observed view from cab to front exterior, rear exterior, trackside and back to cab. The corresponding mode sequence was0,1,2,3,0. Tracking was1 in the three exterior samples and0 in cab. This supplies observed names for these four enum values in this installation; other modes and configurable key bindings remain untested. The derived debug label was computed from the traced native branch, not read from a visible debug overlay.

camera-transition-summary.json joins six raw camera snapshots, including the initial and final paused samples. Every read retained its pointers and simulation time within that read. Four view pointers were observed, with the original pointer restored on return to cab. The render pointer stayed fixed across all samples while its position and basis changed. Therefore a sampler must reread the view pointer and must not use render-pointer identity as a camera-mode change event.

All basis norm errors were below8e-8 and pairwise dot magnitudes below4e-8. Returning to cab restored the same basis; position differed by about0.002 native units, so exact pose equality is not a valid camera-return invariant. These post-input snapshots do not measure input latency or transition duration, and near-orthonormality does not independently establish handedness.

Final state is paused at74600.2734375 with player speed0,23 cars and zero derail flags (captures/camera-final-paused-01/consist-check.json). No save or asset edits were made. Tracking-off transitions within an exterior mode, rotation, selected-vehicle attachment, origin shifts, lifecycle/reload and other engine types remain open. No new candidate rows were needed; this pass strengthens the existing four camera rows.
