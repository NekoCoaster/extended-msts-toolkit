# Environment telemetry checkpoint

26 September 2026. Reuses local native precipitation/terrain research; the prior Unity reconstruction is not treated as runtime telemetry evidence. No hooks, injected calls, asset edits or gameplay input were used in this checkpoint.

## Current environment access

Assembly in render caller 0x4902e2 passes [0x7b6d60] as ECX to 0x53314d. That environment contains precipitation at +0x34 and wind at +0x38. This establishes an external read-only access path without attaching to the precipitation update callback used in older research.

`read_environment.py` captures bounded particle/wind state, fog and lighting. The capture preserves its exact reader copies and executable hash. Environment pointer and simulation time were unchanged during the sample; this is not a guarantee of atomic render state.

## Observed paused state

At simulation time 74000.0546875, environment=53830764, precipitation=54467888, wind=54467212. Flags=5: snow bit 1 plus screen-inhibit bit 4. Texture frame count=4; density/capacity/count/allocated records all 4096; volume radius=60, relative height=30, fall-speed parameter=15, reset=0. These confirm the loaded snow effect despite activity prose describing rain.

Particle flag histogram: 3779 records with flags9, 71 flags5, 225 flags1, 11 flags7, 10 flags3. All have active bit1; 3779 also have culled bit8. Do not equate the other 317 records with actual draw calls without observing render submission. World versus screen coordinates depend on flag0x20. Density denotes allocation count, not precipitation per second or meteorological intensity.

One wind layer was readable: height ceiling100000, base direction(1,0,0), base speed3 and probability parameter0.2, plus current jitter values. Four vortex slots were reported active. Some angular-parameter slots have extremely tiny values; retain raw values and investigate update/validity before interpreting them as meaningful angular speeds. Wind effect state is not proven to be a train-force input.

Ambient RGB=(0.0627451,0.0627451,0.1254902); directional RGB=(0.08235294,0.08235294,0.18823531); incoming light direction=(0,-0.38306496,-0.92372102). Colours are native encoded numerical values, not a verified linear-light colour-space conversion. Fog start=3000, end=100000, scale approximately1/(end-start). Current fog values need checking against the active render path and ENV selection before making a visibility-distance claim.

## Inventory and boundaries

Pass15 compared 3707 instructions / 15494 bytes: zero disk differences, one live call difference at 0x494bc1 in broad caller 0x494850, matching the previously recorded service-research observation. The precipitation update/loader and render orchestrator instructions exported in this pass matched live memory. The patch origin remains unknown.

`environment-fields.json` contributes 34 flat candidates covering precipitation, particle state, wind layers/vortices, fog and lighting. Existing field types, units, extraction paths and limitations remain attached in inventory.json. Per-particle telemetry is a possible surface; no decision to retain or discard it has been made.

Inherited sources: ../msts-precipitation/SPECIFICATION.md and ../msts-precipitation/terrain-research/TERRAIN-SHADER-SPEC.md. New native evidence is in passes15/16 and current read in captures/environment-paused-01/environment.json. All code-verification results are preserved separately rather than assuming the entire live binary equals the analysis image.

Next: active ENV file identity and seasonal selection; session date/weather enums; changing environment/lighting values; wind-slot validity; sky/cloud/satellite/fog producers; any coupling to physics adhesion/resistance. Current readings cover one paused snow/night scene only. MSTS remains paused; NEMT is unchanged.
