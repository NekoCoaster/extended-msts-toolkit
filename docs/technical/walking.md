# Walking and noclip: implementation prepared for 1.2.3

For installation, controls and INI values, see the [walking guide](../walking.md).
The [development chronology](walking-development.md) preserves earlier experiments
and superseded defaults. This page describes the branch prepared for 1.2.3, with historical validation checkpoints labelled below.

## Ownership and input

`runtime/walking.h` owns a static detached camera, installed only after the normal
driving-scene readiness gate. It is deliberately absent from MSTS's owning camera
list. Native camera activation is guarded against stale views and the outgoing
car-pointer assumption used during derailment-camera transitions.

While active, train-driving actions and raw device callbacks are gated. Escape,
function keys and native camera-selection actions remain available; number-row
8 is consumed for FPV reset. Accepted native view changes exit FPV. Modifier
sampling uses the high bit of `GetAsyncKeyState` for left Shift and left Alt
within the focused, unpaused input path. Held RMB pans and hides the cursor;
release, focus loss, pause or exit restores it.

## Floating origin and terrain

Positions are local to the native origin at `0x79d118/0x79d11c`, not immutable
world coordinates. Native rebasing at `0x5172f9` visits registered cameras only.
The adapter tracks origin changes and translates walking state and both static
camera matrices by the inverse tile delta times 2048 m, exactly once per change.
Synchronization runs before movement, after the native camera callback, before
activation handoff and before HUD coordinate formatting.

This fixes the repeated tile-crossing runaway seen in 1.2.1. F5 derives world,
tile and tile-local positions from the synchronized state. Native terrain queries
reject missing or invalid triangle normals. Grounding is terrain-only: there are
no scenery, bridge, platform or train collision capsules.

## Movement and tuning

`runtime/walking-model.h` implements normalized movement and bounded time steps.
`runtime/walking-settings.h` shares tuning validation with runtime configuration
and the frontend. Defaults are 3 m/s walking, 17 m/s flying, Shift multiplier 2
and Alt divisor 2. Invalid tuning values fall back individually; zero divisors
never reach division. NEMT preserves valid custom values on Apply.

Noclip records all three velocity components after direction normalization and
speed modifiers. Exiting above terrain retains vertical velocity for ballistic
motion under gravity (9.81 m/s²); horizontal velocity eases toward walking input.
Below terrain, exit snaps to ground and clears inherited velocity. Landing clears
vertical velocity and carried horizontal momentum. Space jumps to half the
current eye height when grounded.

Height adjustments use a 0.05 m grid and 60 Hz repeat budgeting after a configurable
hold delay; rendered updates remain limited by game frames. FOV uses five-degree
stops bounded to 1–179°. Reset restores configured initial height and entry FOV.

## Evidence and limits

The 1.2.2 checkpoint passed 599 movement-model checks, 338 GUI/installer checks,
the native adapter and existing compatibility suites, readiness/source guards,
repository-tool tests, XP-baseline import audits and packaging checks. Boundary
tests cover both axes/directions/modes, repeated and diagonal shifts, HUD timing
and paused callbacks. Vertical carry tests cover 30/60/144 Hz, pitched flight,
custom modifiers, landing and below-ground recovery.

In-game test feedback confirmed tile crossing and accepted the movement
refinements. These reports are distinct from automated evidence, and do not
certify every route, long-distance traversal or extreme configured speed.

## Unreleased flashlight prototype

`runtime/flashlight.h` uses the native cone-light factory at `0x69b0f0`:
x86 fastcall `(type=2, flags=0x21, parameter-block-on-stack)`, callee pops four
bytes. The object is 0x90 bytes, with vtable `0x828868`. Parameter update is
fastcall `(object, float[12])` at `0x6a0ab0`; release is fastcall `(object)` at
`0x6a01d0`. Supported-image hashing, displaced-instruction checks and vtable
checks gate use. Consumer-derived offsets alone were not treated as an ABI.

At the start of `0x6a1920`, the flashlight takes its position and forward vector
from render camera `0x829224`. This already reflects the walking camera's native
floating-origin synchronization. The light remains in the renderer's enabled
list and uses native transforms/culling. An existing native cone selection is preserved; the flashlight claims the slot only when empty. Renderer shutdown `0x69fdd0`
drops retained references before native list destruction, preventing double
release and address-reuse confusion on the next activity.

The terrain functions cache CPU-lit vertices. Hooks at `0x6f1560` and `0x6f17d4`
mark patches intersecting the current light-range footprint dirty (flag 0x100) before and
after drawing. The second mark ensures a patch is rebuilt without the flashlight
when subsequently visited, even if it was out of view when the light switched
off. Other patch flags are preserved; distant patches keep their cache. These
callbacks use the existing gateway to preserve general registers, flags and
x87/SSE state. World direction at object +0x70 is explicitly initialized because
terrain with no additional-light list may omit the native +0x24 transform call.

L uses the existing focused/unpaused native input event edge. Repeat keydown does
not retrigger it. Native L actions are consumed only during FPV when the key is
available. A custom movement/FPV-toggle collision disables the flashlight alone.
Exit resets it off; pause/focus loss prevents toggling without clearing the beam.

### Historical initial-probe validation

Validation: native regression suite (including 599 walking-model checks and 346
GUI/installer checks), flashlight lifecycle/input/cache tests, 28 frontend source
guards, 29 repository-tool tests, readiness harness and PE32/XP import audit.
Midnight Marias Pass live native probe visibly lit the grassy hillside and tracks;
an L-off comparison restored dark terrain. This probe shares the light helper
and gateway approach but is not the final installed DINPUT build or F5 UI proof.

The first Frida per-render callback probe crashed while the user looked around,
with access violation at `0x6e84af` in environment-colour calculation. Windows
retained no dump. The later terrain-observer attempt was created after the crash
and did not attach. Cause is unresolved; no crash-fix claim is made. The revised
probe installs native gateways then detaches Frida, and records exception context.
Longer movement/look-around validation is pending. Shadow occlusion, every
scenery material, train-headlight coexistence and activity reload are not yet
certified by live tests. Do not release this prototype on automated results alone.

The shared `flashlight-settings.h` validates `FlashlightRangeM` and
`FlashlightAngleDeg` identically in runtime and frontend. Startup defaults are
45 m / 70 degrees full angle; the adapter converts full angle to native
half-angle radians. Live bracket (scan 0x1a/0x1b) and comma/period (0x33/0x34)
events change angle/range by 5 within 10-150 degrees / 5-1000 m. The terrain
footprint follows range changes. Session tuning survives FPV exit but is never
written automatically to disk. INI round-trip, invalid fallback, key repeat,
pause/focus gating, custom-key collisions and adjustment limits are tested.

The user reported initial success with the revised Marias Pass probe, with
limited testing over TeamViewer. A further native probe revision adds the
settings and live keys in that existing process; the complete DINPUT runtime
and extended F5 text still need restart/deployment validation.

Brightness: `;` / `'` decrease/increase FPV flashlight brightness by 5 percentage points. `[Walking] FlashlightBrightnessPct=100` sets startup brightness (0-100; default 100). Live adjustments are session-only; F5 shows the current percentage. Zero emits no light but keeps the flashlight enabled; L releases its selected beam slot. Custom walking bindings take precedence. Brightness scales the warm RGB colour without changing range or angle.

## Integrated locomotive-plus-FPV terrain lighting

The native selected cone remains owned by MSTS when a locomotive beam is present. New checked gateways at `0x6f1e41` and `0x6f220b` cover both terrain vertex generators and add the FPV contribution only when it is not already the selected beam. The callbacks preserve flags, registers and x87/SSE state. They use a render-thread snapshot of FPV position, direction, RGB, range and angle; no light-list traversal or process-memory read occurs per vertex. Camera updates refresh the snapshot, and exit/shutdown/invalid-camera paths disable it.

Only patches intersecting the flashlight range are dirtied, before and after generation. The retained dirty flag also clears old illumination after motion, range reduction or switch-off when an old patch next draws. The native locomotive continues managing its own lighting. Contributions saturate RGB and preserve alpha; they are added after native colour quantization, so small rounding differences remain.

The earlier standalone probe demonstrated simultaneous terrain beams, but this integrated build still requires restart-based live validation. Tests cover both vertex layouts, selected-light exclusion, native selection preservation including later train takeover, alpha/saturation and cone/range rejection. This integration supports the native selected beam plus FPV; it does not create AI sources or implement arbitrary multi-light scenery shading.

## Experimental object-lighting extension

Four fast material shaders use one selected cone even though the generic shader can loop through the active-light list. Checked gateways after diffuse-colour output at 0x69e0f4, 0x69d7fb, 0x69e5c1 and 0x69e9b5 add FPV light only when the native selected light is different. They preserve alpha, specular/fog output and texture coordinates. The first two paths use vertex normals; the latter two follow native non-normal shading, and the final path modulates by source vertex RGB. Emissive/unlit shaders and the generic multi-light path are not modified.

Per-object position/direction must be computed with the inverse camera/object matrix at 0x82898c: camera-space FPV light position (0,0,0.15), direction (0,0,1), matrix rows 0..8 and translation 12..14. The material's +0x114 matrix is not a suitable forward local-to-world transform; an earlier probe using it produced no valid additions. The integrated callbacks use the existing frame snapshot, without per-vertex list scans or ReadProcessMemory. A diffuse linear cone/range contribution is added to packed RGB with saturation; this is an approximation to the native fast shader response and does not add specular reflection or shadows.

Live probes confirmed calls to a normal-based path and additions in the non-normal scenery path, with zero recorded read errors. The initial camera faced away from the train, and its tested vertices remained outside the cone. At that initial checkpoint, track and locomotive surface coverage had not been visually confirmed; subsequent track validation is recorded below. The temporary hooks were disabled and removed after testing; restart-based integrated validation remains required. Unit coverage includes transform translation/rotation/origin shifts, back-face/cone/range rejection, disabled-state handling, vertex tint, alpha and saturation.

## Alternate track shaders (2026-10-02)

In the loaded midnight Marias Pass view, the visible tracks used 0x69ef50. Function 0x69eae0 temporarily switches material-table slots 5/6 from 0x69d3a0/0x69d930 to 0x69eb10/0x69ef50. A snapshot of the table outside the track draw misses this switch. Diagnostic whitening of all fifteen ordinary shaders affected trains/scenery but not tracks; tracing the final vertex-buffer submission at a visible track pixel identified the alternate shader. No final-buffer interception is retained in NEMT.

Two additional checked gateways run after native diffuse/specular output: 0x69f704 (`8b8688010000`, state in ESI, resume 0x69f70a) and 0x69ef25 (`8b9188010000`, state in ECX, resume 0x69ef2b). Modes 4/5 use the same frame snapshot, inverse camera/object transform and selected-light exclusion as the other object hooks. These native track shaders apply cone diffuse without a Lambert normal factor; the additional beam follows that convention. Applying the normal factor made the beam excessively weak on grazing track surfaces. Native specular, fog, alpha and UVs remain untouched. The added beam still uses the existing approximate linear cone/range response.

A bounded native live probe visibly illuminated rails, sleepers and ballast alongside the locomotive beam. L off/on removed/restored the additional illumination without extinguishing the distant native beam. No crash occurred during this run. The integrated DLL needs a fresh MSTS launch; this is not broad route coverage or long-term stability proof. Unit tests exercise both register conventions, selected-beam exclusion, disabled state and preservation of alpha/specular/UVs. Walking installs sixteen base hooks plus an optional input hook; the 1024-entry claim registry and transaction boundary tests accommodate this count.

## Final controls and review preparation (1.2.3)

The user confirmed expected scene illumination after the track work. The shared
range ceiling is now 1000 m (default 45 m retained); runtime and installer use the
same validator. The terrain footprint follows the configured range, so large
values increase cache-refresh work without extending native draw distance.

Six adjustment keys arm independent timers only on accepted initial key edges.
The camera update ticks them using frame time capped at 100 ms. Initial delay
uses HeightRepeatDelayMs; subsequent five-unit adjustments repeat every 100 ms.
Release, missing held state, pause/focus loss, FPV exit or a binding conflict
cancels the timer. Native repeated keydown events do not multiply the repeat
rate. L retains edge-only toggle semantics.

Shift-Z is allowed by preserving the native action name ToggleFrameRate, not
by whitelisting the Z key. Read-only inspection of the loaded activity confirmed
Z binds ToggleFrameRate with modifier mask 0xff08 and VigilanceToggle with 0xff00.
The latter remains masked. The native modifier/event bookkeeping continues to
run, so display toggling retains its normal key combination.

Tests cover all six repeat keys, cadence, configurable delay, cancellation and
limits; installer persistence at 1000 m and invalid 1001 m fallback; native
light parameters at 1000 m; both track register conventions and selected-light
exclusion; and display-action allowance while train actions remain blocked.
The shared hook transaction test now runs in TEST NEMT.bat and CI. New controls
have automated native coverage but still need a fresh-launch live check.
VERSION and release notes prepare 1.2.3. Publish only after PR approval, merge
and verification on main; no release tag is created on this feature branch.

Local review validation passed: 52 frontend-model checks; 104,984 viewport
cases / 998,600 assertions; 350 native GUI/installer checks; 599 movement-model
checks; native walking/light/repeat/input and hook-transaction regressions;
28 frontend source guards; 29 repository-tool tests; readiness checks; and
frontend/runtime PE32 Windows XP import audits. The 142-file release package
was built without changing the source manifest. Runtime SHA-256:
`980861b12758dabee5c5abef74598c77b2c3440674b68c5661f4b18f46c45379`.
