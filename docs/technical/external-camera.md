# Native external camera mouse adapter

Development baseline: `fe9f238`, 2026-10-03. Prepared for release 1.2.4.

## Native evidence

Read-only inspection of loaded PID 34948 (`C:/MSTS/train.exe`, SHA-256
`2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`)
found front/rear views with mode `+0x11c` equal to 1/2 and input callback
`+0x0c` equal to `0x51a69a`. Active view is `0x7c2a88`, not render camera
`0x829224`. The original orbit entry bytes matched disk:
`55 8b ec 81 ec a4 00 00 00`.

Native keyboard processing at `0x4a8fd1..0x4a90f3` produces three float inputs:

| Address | Control | Positive direction |
| --- | --- | --- |
| `0x7c2a58` | Left/right orbit | Right arrow |
| `0x7c2a5c` | Vertical orbit | Ctrl+Down |
| `0x7c2a60` | Distance | Up (closer) |

`0x51a69a` integrates those inputs with the timestep at `0x80ace0`, using
0.7853975296020508 radians/s for orbit and 10 m/s for distance. It owns pitch
limits (approximately -85 to +20 degrees), vehicle-dependent minimum distance,
view-specific maximum distance and matrix updates. New code does not duplicate
those limits or directly write view transforms.

## Implementation

`runtime/external-camera.h` samples a focused, unpaused right-drag on the game
thread. It converts pixels/detents to native input units, adds them temporarily
to existing keyboard inputs, calls the original routine once, then restores the
inputs. Native free-look globals `0x7c2a64/68` are temporarily zeroed during this
call to avoid a second RMB rotation. Pixel scaling cancels the native timestep;
zero, non-finite, tiny or excessive timesteps reject mouse input. Pending wheel
bursts are bounded; partial notches reset on cancellation.

`runtime/external-camera-hooks.h` installs the checked orbit detour. When walking
is enabled it shares walking's existing frame/window dispatch. Otherwise it
installs its own checked frame (`0x51cfd5`) and window (`0x696c00`) detours. The
loader's supported-image and driving-scene gates apply, and `-toolset` is excluded.
Missing `[Camera] ExternalMouseControl` defaults off. The native frontend saves,
reloads and independently enables the option.

The pointer is recentered only during an eligible drag, and no initial offset is
applied. Frame/window maintenance cancels on button release, focus/menu loss,
pause, view/train replacement, capture changes and destruction. This uses XP-era
Win32 APIs and does not synthesize keyboard actions.

## Validation and live test handoff

`tests/external-camera.c` exercises both eligible modes and all other mode IDs,
frame-rate independence, first-drag behavior, wheel accumulation/direction,
restoration of native keyboard/free-look inputs, and cancellation/failure paths.
`TEST NEMT.bat --ci` includes it alongside walking and native UI regressions.
These are synthetic adapter tests, not proof of in-game mouse delivery.

A temporary DLL built from the same adapter was loaded into PID 34948 for user
acceptance. It detours the original tracking routine, adds maintenance at the
unchanged `0x51cff9 -> 0x51d1cb` call, and subclasses the game window while
retaining the existing NEMT procedure. Installed game files/settings were not
changed. It remains loaded for the process lifetime; restarting MSTS removes it.
Temporary build/probe sources, initial snapshots and installation result are in
`C:/codex/work/nemt-external-camera/`. `live-install.json` identifies its Stop
export; Stop disables the adapter on the next native frame without unloading
code still referenced by hooks.

User reported promising initial testing on the M6 machine via remote control on
2026-10-03. Smoothness remains unverified because remote input limits that test.
A complete NEMT host-test package includes the native frontend checkbox and
restart-installed runtime; it does not require the temporary probe DLL.

The user subsequently confirmed host orbit/zoom operation. That confirmation
does not individually certify every combination of walking, focus, pause and
other input transitions; synthetic regression coverage is recorded above.

## Tracking-unlocked correction

User confirmed host orbit/zoom operation, then reported that Shift+9's native
free-look mode was being overridden. Branch: `dev/external-camera-mouse`.
`CameraTracking` dispatches through `0x4a4fd5 -> 0x402cbb -> 0x515e15` and
uses active-view `+0x110` as the tracking flag. The orbit callback checks that
same flag at `0x51aa59`, calling native free-look `0x5197e6` when it is zero.

The mouse adapter now requires nonzero tracking as well as mode 1/2. Tracking
disable cancels any active drag and pending wheel input, restores the cursor,
and passes native inputs through unchanged. Re-enabling tracking starts a fresh
drag without stale movement. Regression cases cover both cameras, initial
unlocked state, mid-drag toggles, wheel/cursor pass-through and re-enabling.
The user subsequently confirmed that native Shift+9 free-look works correctly.
