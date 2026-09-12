# Cab needle test — 1.1.0-alpha.1

This development build adds an opt-in needle correction. It is not the stable release and does not add in-game settings controls. The correction has passed local x86 adapter and geometry tests; visual results on a live simulator remain unverified.

## Install and compare

1. Pull branch `codex/settings-cab-investigation`, close MSTS, then run its `NEMT.vbs` installer and apply the existing selected options. The form title must show `1.1.0-alpha.1`.
2. In the installed `NEMT/settings.ini`, set the following existing section (do not add a duplicate section):

   ```ini
   [Cab]
   CorrectNeedleAspect=true
   ```

3. Launch MSTS normally with `-vm:w`, using the existing widescreen-patched executable. Enter a stock Acela cab at 1280×720 or 1920×1080. Allow at least five seconds of unpaused driving after the scene loads; this is the normal native readiness gate.
4. Watch the speedometer and pressure needles as their values change. Their pivots should stay fixed and their tips should follow the instrument scales without changing shape unexpectedly. Compare the same cab/resolution after restarting with `CorrectNeedleAspect=false`.
5. If the first comparison succeeds, check a 4:3 resolution, day/night cab textures, a second locomotive, and a cab already manually adapted for widescreen. Also end and restart an activity and change resolution.

Report the cab name, resolution, whether it was manually adapted for widescreen, and the visible difference. Matching screenshots at a similar gauge reading are particularly useful. An unchanged 4:3 view is expected.

Set `CorrectNeedleAspect=false` and restart to disable this experiment. Reapplying this installer preserves the field. Existing clean/supported executable bytes are never changed by the toolkit.

## Implementation and limits

The adapter redirects four calls in the single-quad rotated-texture builder. It checks the builder's return address and the renderer's caller through the verified frame chain before applying the correction. Other callers go directly to the original rotation routine. This needs neither a thread-local scope nor a persistent entry/exit record, so an interrupted render cannot leave a stale enabled scope.

The wrapper converts the already-scaled XY offset back to cab coordinates, calls the original trigonometric rotation, then scales the result to screen coordinates. It preserves the original pivot placement, texture coordinates, Z component and return pointer. Equal scales, invalid scales and non-simulation modes bypass the correction. Segmented needle textures are outside this experiment.

Installation checks the two frame prologues and connecting calls, then claims and changes all four rotation calls through the shared transaction. The registry capacity is now 64, allowing this feature alongside all existing features. No file writes occur per needle draw.

The executable fixtures verified the call chain, thunks and four-byte callee stack cleanup. `tests/cab-native.c` executes the production machine-code adapter for 100,000 corrected calls and six bypass cases with synthetic original frames. These are local acceptance checks, not measurements from a running MSTS scene.
