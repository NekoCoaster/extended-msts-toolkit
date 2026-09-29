# Walking extension: development checkpoint, 2026-09-29

> Historical development chronology. Version 1.2.2 is now published. Earlier
> sections preserve the defaults, pending tests and release status at each
> checkpoint; they are not current setup instructions. Use the [current technical
> reference](walking.md) or [walking guide](../walking.md) for present behavior.

Status: **experimental implementation; partial live validation, not a release**. Branch
`dev/first-person`, created from `main` at `5cd5896`, in
`C:\codex\worktrees\NEMT-walking`. The main checkout and installed game files
were initially unchanged. A backed-up temporary test deployment is now in use;
its restoration must be confirmed before calling cleanup complete. No
release/version change is intended.

## Agreed behavior

- Configurable walking toggle; restore the previous native train camera on exit.
- Share NEMT's six Route Editor navigation bindings, default W/S/A/D/E/Q.
- Hold RMB to look. Walking speed proposed as 1.4 m/s; noclip 10 m/s.
- E/Q raise/lower standing eye height by 0.05 m per press while grounded mode
  is selected; in noclip they provide continuous vertical movement.
- V toggles noclip. Space starts a grounded, edge-triggered jump. Jump apex
  above takeoff is half the configured standing eye height: height 2 m means
  feet 1 m and eyes 3 m above the original ground at the apex.
- Block train keyboard and mouse/cab controls in both modes. Preserve
  existing throttle/brake settings; do not pause simulation. Enter/exit must
  handle held commands and key releases, not just suppress new key-downs.
- Extended white F5 HUD should show mode, world/tile position, eye/feet height,
  grounded/jumping state, noclip status and actual remapped controls. Must work
  with crawling disabled and coexist with crawling's existing four HUD lines.
- Terrain following is the initial collision scope. Solid scenery, platform,
  bridge and vehicle colliders are not recovered or promised yet.

## Code and checks

`runtime/walking-model.h` now supplies the integrated movement model:
metre-based movement, terrain callback with explicit failure, normalized
movement, RMB-gated look, edge-triggered height/noclip/jump, ballistic jump,
pause handling and bounded frame time. Its eye-height limits of 0.1–10 m and
look sensitivity are provisional implementation defaults, not finalized UI.

`tests/walking-model.c` covers apex, landing, held/released Space, height steps,
diagonal speed, look gating, noclip and missing terrain. All **22 checks passed**
after the execution-policy blocker was resolved. Initially, execution was blocked.
Windows Code Integrity event 3077 at 2026-09-28 22:08:44–45 confirms that
`work\walk\walking-model.exe` did not meet Enterprise signing requirements
or violated policy `{0283ac0f-fff1-49ae-ada1-8a933130cad6}`. No alternate launch
method or security-policy bypass was attempted; the same executable subsequently
ran successfully through the ordinary launch path.

`runtime/walking.h` implements guarded native camera and input adapters.
`runtime/hud.h` now renders independent walking rows. Configuration and the native
frontend preserve the opt-in enable flag, custom toggle and initial height.
Walking is not added to recommended defaults.

Current checks:

- `TEST NEMT.bat --ci`: passed; 304 GUI/installer checks, 52 frontend-model checks,
  104,984 viewport cases / 998,600 assertions, existing compatibility regressions,
  22 walking-model checks and walking-native adapter assertions.
- `tests/walking-native.c`: bounded key reads; action/held-callback masking;
  F5/Escape allowance; raw device callback gating; restoration of pre-existing
  flags; corrupt-list and removed-node handling; short-tap edge capture; ground
  failure/empty-normal handling; HUD states and custom key labels.
- `python tests/native-frontend.py`: 28 source invariants passed.
- `python tests/repository-tools.py`: 29 tests passed.
- `python tests/readiness.py tools/tcc/tcc.exe`: passed.
- Intended runtime rebuild and PE32/x86 XP-baseline import audit: passed.

Live evidence on the supported image:

- One-shot native query: camera `(-68.621185,2015.869995,-178.381927)`,
  terrain `1999.994141`, normal `(0,1,0)`. Hook restored successfully.
- Bounded detached camera test: feet `1999.993164`, eyes `2001.993164`,
  native active view changed to the custom view and returned to exact original
  `0x05b3fdf0`. Both temporary hooks restored; process remained responsive.
- Complete runtime with crawling enabled: F12 entry and return to cab; combined
  eight-row white F5 HUD; train throttle/reverser stayed zero.
- A short-tap bug was found live and fixed by buffering native press edges instead
  of relying only on frame-sampled held bits. The fix has regression coverage.
- Complete runtime with crawling disabled: F12 entry; independent four-row HUD;
  V noclip ON displayed while native wipers remained zero; E vertical flight;
  Escape pause and mouse-click resume worked.
- Fixed live jump capture: 2,715 read-only samples; eye baseline
  `2001.9931640625`, apex `2002.9930419921875`, landing at baseline. Rise
  **0.9998779296875 m** for a 2 m eye height. Throttle and reverser remained zero.
- E eye-height step: eyes changed from `2001.993164` to `2002.043213`.
- Short W tap moved Z from `-231.082016` to `-231.089020`; throttle/reverser
  stayed zero. Manual sustained physical-key and RMB-look checks were requested
  because the computer-use interface does not expose a right-button hold.
- Subsequent in-game test reports confirmed that the live feature works very well,
  supporting this NEMT integration checkpoint. This is in-game test feedback,
  not a separately instrumented assertion for every physical input combination.

Latest registry-restoration hardening and HUD world-coordinate/paused labels
were unit-tested after that live build; a final rebuilt-runtime rerun remains
before claiming those exact bytes live-tested.

Temporary installation backup: `work/walk/installed-backup-20260929/` contains
the previous DINPUT.dll, settings.ini and installation.json. The installation
record was not rewritten. Restore DLL/settings and compare their hashes after
closing the test process. Do not leave the installation record claiming ownership
of an unrecorded DLL after testing.

## Native evidence and leads

Current MSTS executable was `C:\MSTS\train.exe`, PID 20580 during inspection,
SHA-256 `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`.
MegaCoaster Explore Route, KIHA31, Mega-Start near, 10:00 Summer Clear loaded
successfully. Cab/exterior cameras were observed, then the session was paused.
Player train speed was zero. These are baseline observations, not walking tests.

- Active view pointer `0x7c2a88`; its basis starts at `+0x14`, position `+0x38`.
  Render pointer `0x829224` stayed constant across camera changes; basis begins
  `+0x0c`, position `+0x30`. Native view pointers changed between cab/exterior.
- `0x519673` is a native free-camera controller; `0x51e451` rotates a movement
  vector and `0x519fea` adds its translation. Neither is a ground query.
- `0x51cd5f` activates native views, calls lifecycle callbacks, updates renderer
  projection and global view state. `0x51d81a` allocates a 0x1a8-byte view.
  `0x51d8cd` registers callback-bearing views. ABI and ownership must be checked
  in assembly before reuse; decompiler signatures are not a safe calling contract.
- Camera distance used by AI physicalization at `0x5a58af` reads the native
  view position, not only the rendered matrix. A final render override is not a
  sufficient implementation. Audio/listener and terrain streaming also matter.
- Spotter placement `0x518aae` calls `0x530749` for a minimum camera height.
  `0x530749` calls `0x530635`, which delegates to `0x6bf060` if `0x7c2e08`
  is nonzero. **Live-validated at the sampled location.** The wrapper
  returns zero on failure; use a success-bearing query instead of treating zero
  as valid ground. The adapter calls `0x530635` with ECX=result[8], EDX=2,
  stack=float X,float Z, callee pops 8. It additionally requires a finite unit
  normal because native triangle-hole paths can return success without a hit.
- `0x5d1da7` finds nearby track, not terrain; do not use it for ground height.
- Existing shared IOM event hook is at `0x6bae0e`. Walking cannot independently
  claim that site while crawling owns it. The implementation uses crawling's
  existing callback when enabled and its own verified gateway otherwise.
  `0x6bad60` is wrapped to mask actions during dispatch, including the recurring
  callback queue; raw device callbacks are gated during unpaused driving.
  Keyboard-event suppression alone was explicitly rejected as insufficient.
- `runtime/config.h` now reads the shared six bindings when either editor swaps
  or walking is enabled and validates walking toggle/V/Space/F5 conflicts.
- `runtime/hud.h` installs at callsite `0x60c996`, now enabled for either HUD
  consumer with dynamic row count; the original end-render call is retained.

Raw read-only Ghidra exports are in ignored `work/walk/camera02`, `camera03`,
`camera04`, `terrain01`, with `.c`, `.asm`, `.bytes.tsv`, logs and indexes.
`work/walk/export.ps1` reproduces targeted exports from the existing research
project without saving changes. Revalidate hook bytes against the supported
installed image before patching: the Ghidra project has an older base-image hash.

## Remaining validation

1. Retain the baseline accepted through in-game testing; explicitly exercise focus loss and
   stop-on-release in a repeatable regression pass.
2. Exercise custom remaps/hotkey live, activity exit while walking, longer terrain
   movement, tile boundaries and scenery-hole cases.
3. Finish native/source checks after final changes, refresh source inventories,
   and validate the exact final runtime bytes if more fixes are made.
4. Restore the backed-up installed files and record hash equality. Keep any
   experimental installation opt-in and distinguish it from release history.

## FOV follow-up (after walking checkpoint c5305f0)

Requested controls are mouse wheel up/down and `-` / `=` while walking. Start
from the existing camera FOV, with requested endpoints of 1 and 359 degrees.
Steps should snap to adjacent multiples of five rather than add five to the
endpoint: `1 -> 5 -> 10 -> ... -> 355 -> 359`, and reverse on decrement.
For an off-grid starting value, select the next grid value in the requested
direction. Clamp at the endpoints. Control direction and HUD presentation remain
to be finalized with that implementation.

The original request above was superseded by the agreed **179 degree** maximum
after the projection investigation below. The native view's projection field at
`+0x84` was initially a research lead, not proof of
support for this entire range. Conventional perspective projection becomes
singular at 180 degrees and cannot represent a 359-degree view normally; inspect
MSTS's projection behavior before promising the requested upper range. Keep this
work separate from the accepted walking checkpoint. No PR or release is intended
at this stage.

### Projection investigation, 2026-09-29

Read-only export `work/walk/fov01/006b91f0.{c,asm}` confirms the native
projection helper uses `tan((angular correction + FOV) * 0.5)` as the divisor
for focal distance. Activation at `0x51cf20` passes view `+0x84` on the stack,
with viewport and center pointers in ECX/EDX; the abbreviated decompiler call
must not be treated as a one-argument ABI. A read-only sample of the running
supported MSTS process confirmed `0x755114 = 0.5`, the pixel offset at
`0x758b80 = 0.10000000149`, and current FOV `1.04719674587` radians (about 60
degrees). No process writes or camera changes were made in this investigation.

For the centered walking camera, focal distance tends to zero at 180 degrees
and becomes negative above it. Passing 359 degrees is not a genuine panoramic
view. The agreed range is a conventional **1–179 degrees**.

### Implemented follow-up

- Wheel up / `=` narrow FOV; wheel down / `-` widen it. Stops are
  `1, 5, 10, ... 175, 179`. Float roundoff near exact grid points is normalized.
- Entry copies the original native FOV without quantizing it; invalid or
  out-of-range source values fall back to 60 degrees. Only the detached view's
  `+0x84` field changes. Frame-thread activation refreshes the native projection;
  exit restores the saved native camera, including its original projection.
- Verified main-window procedure entry `0x696c00` is detoured with the same
  five-byte gateway used by the editor module, exclusively in gameplay mode.
  Wheel messages are consumed only while walking is active, focused and
  unpaused; other messages chain through the original procedure. Partial wheel
  deltas accumulate to 120-unit detents and reset on focus loss/pause/exit.
- Native keyboard edges handle `-` / `=` without repeat; both keys are reserved
  against walking remap/toggle conflicts. Native train-action isolation remains
  active. The white F5 HUD displays FOV and controls without adding rows.
- Model tests now have 104 checks including all ascending/descending stops,
  endpoints, off-grid starts and float-roundoff cases. Native adapter tests
  cover key edges, partial/multiple/reversed wheel deltas, disabled input,
  projection refresh, inactive message forwarding and HUD text.
- Automated tests and XP import audit passed. The rebuilt FOV runtime has not
  yet been deployed into the running MSTS session; actual wheel delivery,
  endpoint appearance and restoration need a live restart/test. No PR opened.

## Movement refinement follow-up

Subsequent in-game test reports confirmed that zoom works perfectly after
applying the FOV build. New movement refinements are implemented but await their own live
acceptance; do not attribute the FOV report to these newer changes.

- Base speeds: walking 3 m/s, noclip 17 m/s. Native left Shift scan `0x2a`
  multiplies by two; left Alt scan `0x38` multiplies by one half. Together they
  cancel. Sprint/slow affect horizontal movement and noclip vertical movement,
  not eye-height changes or jump apex. Windows Alt-menu activation is suppressed
  only during active, focused, unpaused walking.
- On noclip exit above terrain, retain actual previous flight X/Z velocity and
  start gravity from zero vertical speed. With 0.01-second substeps, analytically
  ease horizontal velocity toward walking input at rate 1.5/s and integrate
  displacement. Below-terrain exits still snap up. Landing clears air carry;
  unavailable terrain prevents the mode transition as before.
- Height-repeat delay is `[Walking] HeightRepeatDelayMs=500`, valid 50–5000.
  Native runtime validates it; frontend loads/preserves/writes it. Repeat period
  is 0.1 s, exponential doubling time 1 s, capped at 0.25 m per repeat. Existing
  eye-height bounds remain. Release, conflicting directions and mode/pause/focus
  changes reset the timer. The first tap is still 0.05 m.
- Cursor hiding uses `SetCursor(NULL)` and suppresses native `WM_SETCURSOR`
  while looking; no global `ShowCursor` counter changes. Restore the saved cursor
  on release/focus loss/cancel/destroy/reset, but do not overwrite a newer native
  cursor (for example one selected by a menu). Camera pause handling restores it.
- Regression coverage includes normal/slow/sprint/combined diagonal speeds,
  flight-to-fall momentum, gravity/landing, below-ground recovery, height delay,
  exponential cap/reset/bounds, cursor ownership/restoration and config round-trip.
  Full suite passed with 130 walking model checks and 306 native GUI checks.
- Apply the rebuilt NEMT to the installation and restart MSTS before live tests.
  The ongoing game session has not been modified. No PR or release is created.

## Derailment handoff correction and backtick controls

In-game test reports identified crashes on derailment during FPV and on returning from FPV after
derailment. No crash dump or matching Application event was found. Targeted
read-only decompilation identified a concrete unsafe path, but live crash-case
reproduction and verification remain required before claiming both reports fixed.

Native activation `0x51cd5f` calls the incoming view's `+0x10` callback before
updating `0x7c2a88`. In callback `0x5191dd`, the `+0x110` branch reads the outgoing
active view's `+0x9c` car at `0x51949a`, adds `0x20`, and copies 48 bytes at
`0x5194ae` without checking null. FPV deliberately zeroes `+0x9c`, so that path
reads from address `0x20`. This explains a native handoff crash without requiring
a freed camera as the cause. Raw exports are under ignored
`work/walk/active-view-readers` and `work/walk/derail-camera3`.

A verified six-byte activation detour now bridges FPV-to-native transitions:
temporarily supply a live car owned by the current train (incoming camera's car,
or controlled car at train `+0x6a`), run original activation, then remove the
temporary attachment. Outgoing callbacks remain zero, avoiding duplicate
deactivation of the saved native view. FPV resets only when native activation
actually changes the view. This covers native forced transitions as well as
explicit FPV exit. Saved return cameras must still be in the bounded native
camera list (`0x7c2ac8`, node `+8`); otherwise try the current registered cab
camera. Invalid pointers/ownership reject the handoff rather than dereferencing
them. A rejected handoff keeps FPV input isolation active.

Default toggle is now BACKQUOTE (`0x29`), migrating the old F12 default in both
runtime and frontend. Other custom hotkeys remain preserved. Keyboard actions
bound to F1–F12 and Escape are allowed, plus the named native camera actions
found in `GLOBAL/common.iom`; no hard-coded numeric-key assumptions are used.
Other train actions remain masked for the current dispatch even if a camera
action exits FPV mid-poll. The activation bridge ends FPV for successful view
selection, without first bouncing through the saved camera.

Tests cover all twelve function-key binding allowances, camera/non-camera action
classification, native callback-shaped outgoing matrix access, forced derail
handoff, return to derail view, controlled-car fallback, stale saved view,
missing ownership, rejected activation and corrupt registry bounds. These are
native adapter regressions, not an actual MSTS derailment reproduction.

### Follow-up: native action names and preserving the current view

In-game test reports showed that number-row camera selection remained blocked. The prior
camera allow-list incorrectly treated action `+0` as an ASCII text pointer.
Native registration `0x6bbac0` / `0x6bc130` stores the object returned by
`0x6bca50`; that interned-name object's `+0x10` points to UTF-16 text. The parser
now follows that layout with bounded reads and compares wide strings. Tests now
use the real object layout rather than a direct ASCII pointer. This correction
supports the native number-row and remapped camera actions without unblocking
non-camera train commands merely because they are bound to a number key.
An input-dispatch test allows number-row 2, performs the native-shaped activation
handoff, checks FPV exit, and verifies mask/device restoration afterward.
Read-only exports are in `work/walk/action-registry` and `action-identity`.

When UnlockCameras is enabled, `start_native` now installs a verified early return
at camera-only notification `0x51d4e1`, in the same transaction as the existing
camera lock removal. This applies with FPV disabled as well as enabled. The
native derail caller still updates vehicle/train flags and wakes bodies; only
forced camera takeover/setup is omitted. With the option disabled, neither
camera patch is installed and the guarded native takeover remains in effect.
See `patches.md` for exact bytes. Eighteen feature configurations and the real
native derail-routine fixture test passed. These tests do not constitute live
verification of retaining external view 2 or switching out of FPV in MSTS.

### Accepted camera fixes; height and control-panel polish

In-game test reports confirmed that the camera changes look good. The next refinement moves
Enable walking directly after Unlock camera modes in both layout and creation
(tab) order, shifting the lower controls together. Native layout checks cover
adjacent rows at 96/120/144/192 DPI with one-pixel rounding tolerance.

Q/E now snaps off-grid eye heights to the next 0.05 m boundary in the requested
direction. Held repeat uses 25 ms ticks after the existing configurable delay.
Each tick budgets 0.05 m multiplied by exponential acceleration, capped at
0.0625 m/tick (2.5 m/s). A fractional accumulator preserves the 0.05 m grid and
the existing maximum rate, giving 0.05/0.10 m applied changes at the cap instead
of off-grid values. Release/reset clears the fraction. The max eye height is now
100 m in physics, native INI validation, and frontend round-trip (10000 cm).
Jump apex remains half eye height, including at large configured heights.

Validation: full native suite passed, 380 walking-model checks and 326 GUI checks.
Coverage includes off-grid steps, 25 ms timing, every accelerated step staying
on-grid, the 100 m cap, and saved 10000 cm height. Live feel testing of these
latest refinements remains separate from the in-game test reports for camera fixes.

### 60 Hz height repeat refinement

Held Q/E repeat now uses 1/60 second ticks (about 16.67 ms), superseding the
25 ms period above. The first repeat still applies 0.05 m at the configured
hold delay. Later ticks budget 2/60 m with the same exponential acceleration
and 2.5 m/s cap. Fractional carry keeps applied heights on the 0.05 m grid;
some ticks have no visible change. The native camera frame drives these ticks,
so this is not a promise of minimum rendering FPS or a background timer.
Regression checks cover the tick boundary, grid, and equal travel at 30/60/144
FPS, including the unchanged capped rate. Live smoothness remains an in-game check.

### Final labels and FPV reset key

Control-panel labels are now exactly "Swap arrow keys with WASDQE controls in
route editor" and "Enable Walking (Experimental)". Only wording changed; the
editor key mapping remains untouched. Number-row 8 (`0x09`) is consumed by FPV
and resets the configured initial eye height plus the FOV captured on FPV entry.
Keep a separate configured height baseline because ordinary FPV exit retains
the adjusted session height. Reset preserves position, orientation, velocities
and mode; it clears height repeat/fraction and wheel remainder, and requests a
projection refresh. Native 8 behavior is untouched outside FPV. The key is now
reserved against walking movement/toggle conflicts and appears in the F5 HUD.
Tests cover exact labels, custom defaults, no held repeat, inactive/paused gates,
native event consumption and preservation of other keys.

### PR checkpoint validation (2026-09-29)

The complete native regression suite passed: 508 walking-model checks, the
walking native-adapter harness, 328 GUI/installer checks, 52 frontend-model
checks, and 104984 viewport cases (998600 assertions), plus the existing
display, input and window compatibility tests. The actual loader readiness
harness, 18 feature-configuration fixtures, 28 frontend source guards and 29
repository-tool tests also passed. Both components rebuilt with bundled x86
TinyCC and passed the XP-baseline PE import audits.

In-game test reports describe successful walking, zoom and camera-fix behavior during
development. This checkpoint adds no fresh instrumented live-game evidence;
the remaining route and tile-boundary checks above
still apply. No version bump, release tag or release publication is included.

### Requested 1.2.1 release preparation

After the PR checkpoint, release preparation added a patch-version bump and
a release tag. `VERSION` is now 1.2.1 with matching `releases/v1.2.1.md`.
The annotated `v1.2.1` tag is prepared locally on the versioned checkpoint;
it is not pushed or published as part of preparation. Pushing a `v*` tag triggers
the repository's verification and release-publication workflow. If review changes
the release commit, confirm the intended final tag target before publication.

### Post-release fixes under in-game testing

Tile-origin synchronization now tracks `0x79d118/0x79d11c` and translates walking
state and both static camera matrices by the inverse 2048 m origin delta. Native
`0x5172f9` visits only registered cameras, excluding this static FPV view. Without
the translation, each subsequent frame could trigger the same crossing again.
Tests cover positive/negative X/Z boundaries, both modes, repeated synchronization,
diagonal shifts, HUD timing and paused camera callbacks. In-game testing confirmed
that the boundary fix works.

Left Alt not slowing movement was reported in both modes. Model tests confirm
the arithmetic, but the native scan bitmap did not yield the expected in-game
result. Modifier sampling now uses the high bit of `GetAsyncKeyState(VK_LMENU)`
and `VK_LSHIFT`, only within the existing focused, unpaused input path. Tests
cover neither/either/both modifiers and release, without relying on native scan
bits. The exact native modifier-bitmap discrepancy has not been instrumented;
subsequent in-game test feedback accepted the modifier fix.

Shared tuning validation covers WalkSpeedMps/FlySpeedMps (0.01–1000),
SprintMultiplier/SlowDivisor (1–100), individual default fallbacks and defensive
zero-divisor handling in the movement model. Frontend Apply preserves the values,
runtime entry copies them into the state, and F5 displays them. Custom speeds,
combined modifiers, vertical flight, malformed settings and INI round trips have
regression coverage. Subsequent in-game test feedback accepted these refinements.

Noclip now records its normalized, modifier-adjusted vertical velocity alongside
X/Z velocity. Exiting above terrain retains it for normal ballistic integration
instead of resetting it to zero. Below-ground recovery and landing still clear
vertical velocity; horizontal easing is unchanged. Regression tests cover upward,
downward and stationary flight at 30/60/144 Hz, pitched flight, custom modifiers,
landing and below-ground recovery. All 599 walking-model checks and the full
native suite passed; subsequent in-game test feedback accepted the transition
feel and this checkpoint for commit.

### 1.2.2 release preparation

Version 1.2.2 and matching release notes package the tile-origin, modifier-input,
configurable-speed and full-velocity transition fixes above. The release tag is
prepared locally on the validated checkpoint, not pushed. After PR review and
merge, verify the final merged commit before publishing the tag; a pushed `v*`
tag starts the release workflow. In-game acceptance and automated regression
evidence remain distinct from universal route or high-speed compatibility.
