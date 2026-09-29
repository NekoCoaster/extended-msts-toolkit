# Walking and noclip: current implementation (1.2.2)

For installation, controls and INI values, see the [walking guide](../walking.md).
The [development chronology](walking-development.md) preserves earlier experiments
and superseded defaults. This page summarizes the shipped implementation.

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
