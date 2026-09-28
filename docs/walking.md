# Experimental ground walking

This development build adds an opt-in **Enable Walking (Experimental)** checkbox,
immediately below **Unlock camera modes during derailment**. It is not a
released feature. Stop and secure the train before walking: the simulation and
the train's existing throttle/brake settings continue while train input is blocked.

Close MSTS, open the updated NEMT, enable the checkbox, click **Apply**, and restart
MSTS. Restarting MSTS alone does not install an updated runtime. After an activity has
loaded and run for approximately five seconds, press **backtick (`)** and release all keys
and mouse buttons to enter walking mode. Press it again to return to the previous
train camera. A cab/passenger/head-out start is offset 3 m sideways to avoid
starting inside the train mesh. Entry requires usable terrain at that location.

F1–F12 remain available during FPV. Native camera-selection actions (including
remapped camera keys) switch directly out of FPV into the selected view when
MSTS accepts the selection. Automatic native camera changes, including the
derailment camera, also end FPV. A rejected selection leaves FPV active.
With **Unlock camera modes during derailment** enabled, the automatic derailment
camera takeover is suppressed: the current native camera or FPV/noclip stays
active. When that option is off, the normal native takeover still applies.

| Default control | Action |
| --- | --- |
| W / S / A / D | Walk forward / backward / left / right at 3 m/s |
| Hold left Shift / left Alt | Double / halve movement speed (both together: normal speed) |
| Hold right mouse button | Look around; release it to stop looking |
| E / Q | Raise / lower eye height by 0.05 m; hold to repeat with acceleration |
| Space | Jump from the ground; maximum rise is half the current eye height |
| V | Toggle noclip flight at 17 m/s; E/Q become continuous vertical movement |
| Wheel up / = | Zoom in (decrease FOV) |
| Wheel down / - | Zoom out (increase FOV) |
| Number-row 8 | Reset configured eye height and entry FOV without leaving FPV |
| F5 | Cycle to the extended white HUD for walking status and controls |
| Escape | Pause/resume through the native menu |

Holding Space does not repeat jumps. A 2 m eye height gives a 1 m jump: feet rise
from ground to 1 m and eyes from 2 m to 3 m. Noclip does not jump. Leaving noclip
requires valid terrain: above it, gravity pulls the feet down while horizontal
flight momentum eases toward walking input (about 0.46 seconds to halve the
velocity difference); below it, feet snap up to ground. Landing ends the carried
momentum. Existing terrain-only collision limitations still apply.

Normal / slow / sprint speeds are **3 / 1.5 / 6 m/s** on foot and
**17 / 8.5 / 34 m/s** in noclip, including vertical flight. Modifiers do not
change jump height or Q/E eye-height step sizes. Diagonal movement is normalized.

In ground mode, Q/E initially snaps eye height to the next 0.05 m boundary
(for example, 2.03 m becomes 2.05 m upward or 2.00 m downward). After a 500 ms hold
(configurable below), it repeats at 60 Hz (about 16.67 ms). Repeat travel accelerates
exponentially from 2 m/s to a 2.5 m/s cap; fractional travel is carried between
repeats so every applied change remains a multiple of 0.05 m. Some ticks therefore
make no height change. Updates run with the game camera: this does not force a
minimum rendering frame rate, and slower frames collect the due ticks.
Release, direction changes, pause/focus loss,
and mode changes reset the acceleration. Holding both height keys cancels it.
Eye height remains bounded to 0.1–100 m. The cursor is hidden during RMB look and
restored on release, focus loss, pause or leaving walking mode.

FOV starts from the current camera angle (normally about 60 degrees) each time
walking is entered. Both walking and noclip support the range **1–179 degrees**,
using stops `1, 5, 10, ... 170, 175, 179`. Off-grid angles step to the next stop
in the selected direction. Each physical `-` or `=` press changes one step;
holding a key does not repeat. Wheel input accumulates partial detents and handles
multiple detents. Zoom is disabled while paused or unfocused. FOV is session-only,
and leaving walking restores the original train camera and its projection.
Very wide angles produce extreme perspective distortion; 180 degrees is excluded
because the native perspective projection becomes singular there.

In FPV (including noclip), number-row 8 is reserved for reset instead of native
camera selection. It restores `[Walking] EyeHeightCm` (normally 2 m) and the FOV
captured when entering FPV (normally about 60 degrees). Position, orientation,
velocity and noclip status are preserved; height-repeat acceleration and partial
wheel input are cleared. Outside FPV the key retains its native meaning.

Keyboard movement shares the six existing `[Editors]` `RE_CAM_*` bindings even
when the editor's arrow-key swap option is disabled. Left Shift and left Alt
modify speed; the walking controls remain usable while they are held.

To customize the hotkey and initial eye height, edit `NEMT/settings.ini` while
MSTS is closed. The control panel preserves these values when applying settings:

```ini
[Walking]
Enabled=true
ToggleKey=BACKQUOTE
EyeHeightCm=200
HeightRepeatDelayMs=500
```

`EyeHeightCm` accepts 10–10000. Q/E changes last for the current game session;
they do not overwrite the saved initial height.
`HeightRepeatDelayMs` accepts 50–5000 milliseconds and is preserved when applying
settings in NEMT. Missing values default to 500 ms. This sets the initial hold
delay, not the subsequent fixed 60 Hz repeat interval.
The hotkey accepts the same
physical-key names as the editor bindings, for example `F11`. The walking toggle,
six movement keys, V, Space, F5, `8`, `-` and `=` must not conflict. Invalid runtime configuration
is rejected, so keep a backup before hand-editing. Escape/modifier keys are not
valid walking bindings.

The old default `F12` automatically migrates to `BACKQUOTE` when applying this
build (and is interpreted as backtick by the runtime). Other explicitly configured
hotkeys are preserved; a custom function-key toggle takes precedence over that
function key's normal action. The literal backtick is also accepted in the INI.

The extended F5 rows show walking/airborne/noclip status, train-input blocking,
world X/Z, tile and tile-local position, feet/eyes Y, eye height and actual remapped
controls, plus the current FOV and zoom controls. Walking's HUD does not require the crawling feature. When both features
are enabled, their rows are displayed together.

## Current limitations

- Ground detection uses MSTS terrain triangles. There is no scenery, platform,
  bridge or train collision capsule; the walker can pass through those objects.
- This is not yet a release-ready compatibility claim. Long-distance/tile-boundary
  traversal, physical joystick hardware, multiplayer and arbitrary routes still
  need validation. See [development evidence](technical/walking-development.md).
- Both modes block native train driving actions, including held callbacks, and gate raw
  device callbacks during driving. Function keys, camera-selection actions and Escape remain available. Toggle entry/exit wait
  for keyboard and mouse release to avoid transferring held train commands.
- Focus loss and pausing stop walking input and mouse capture. The game simulation
  itself follows MSTS's normal pause/background behavior.
