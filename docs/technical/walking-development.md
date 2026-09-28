# Walking extension: development checkpoint, 2026-09-29

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
- Block train keyboard, mouse/cab and joystick controls in both modes. Preserve
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
look sensitivity are provisional implementation defaults, not user-approved UI.

`tests/walking-model.c` covers apex, landing, held/released Space, height steps,
diagonal speed, look gating, noclip and missing terrain. All **22 checks passed**
after the user resolved the execution-policy blocker. Initially, execution was blocked.
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
  stayed zero. Sustained physical-key and RMB-look checks were requested from the
  user because the computer-use interface does not expose a right-button hold.
- The user subsequently reported that the live feature works very well and
  approved this NEMT integration checkpoint. This is user-reported acceptance,
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

1. Retain the user-accepted live baseline; explicitly exercise focus loss and
   stop-on-release in a repeatable regression pass.
2. Exercise custom remaps/hotkey live, activity exit while walking, longer terrain
   movement, tile boundaries and scenery-hole cases. Physical joystick behavior
   is covered structurally by the common dispatcher, not yet by hardware testing.
3. Finish native/source checks after final changes, refresh source inventories,
   and validate the exact final runtime bytes if more fixes are made.
4. Restore the backed-up installed files and record hash equality. Keep any
   experimental installation opt-in and distinguish it from release history.

## Next feature: FOV adjustment (not in this checkpoint)

Requested controls are mouse wheel up/down and `-` / `=` while walking. Start
from the existing camera FOV, with requested endpoints of 1 and 359 degrees.
Steps should snap to adjacent multiples of five rather than add five to the
endpoint: `1 -> 5 -> 10 -> ... -> 355 -> 359`, and reverse on decrement.
For an off-grid starting value, select the next grid value in the requested
direction. Clamp at the endpoints. Control direction and HUD presentation remain
to be finalized with that implementation.

The native view's projection field at `+0x84` is a research lead, not proof of
support for this entire range. Conventional perspective projection becomes
singular at 180 degrees and cannot represent a 359-degree view normally; inspect
MSTS's projection behavior before promising the requested upper range. Keep this
work separate from the accepted walking checkpoint. No PR or release is intended
at this stage.
