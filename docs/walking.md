# Experimental ground walking

This development build adds an opt-in **Enable walking** checkbox. It is not a
released feature. Stop and secure the train before walking: the simulation and
the train's existing throttle/brake settings continue while train input is blocked.

Enable the checkbox, apply the settings and restart MSTS. After an activity has
loaded and run for approximately five seconds, press **F12** and release all keys
and mouse buttons to enter walking mode. Press it again to return to the previous
train camera. A cab/passenger/head-out start is offset 3 m sideways to avoid
starting inside the train mesh. Entry requires usable terrain at that location.

| Default control | Action |
| --- | --- |
| W / S / A / D | Walk forward / backward / left / right at 1.4 m/s |
| Hold right mouse button | Look around; release it to stop looking |
| E / Q | Raise / lower eye height by 0.05 m per press |
| Space | Jump from the ground; maximum rise is half the current eye height |
| V | Toggle noclip flight at 10 m/s; E/Q become continuous vertical movement |
| F5 | Cycle to the extended white HUD for walking status and controls |
| Escape | Pause/resume through the native menu |

Holding Space does not repeat jumps. A 2 m eye height gives a 1 m jump: feet rise
from ground to 1 m and eyes from 2 m to 3 m. Noclip does not jump; leaving noclip
requires valid ground and currently snaps the feet to that ground.

Keyboard movement shares the six existing `[Editors]` `RE_CAM_*` bindings even
when the editor's arrow-key swap option is disabled. Modifier combinations are
reserved; use the configured physical keys without modifiers for walking.

To customize the hotkey and initial eye height, edit `NEMT/settings.ini` while
MSTS is closed. The control panel preserves these values when applying settings:

```ini
[Walking]
Enabled=true
ToggleKey=F12
EyeHeightCm=200
```

`EyeHeightCm` accepts 10–1000. Q/E changes last for the current game session;
they do not overwrite the saved initial height. The hotkey accepts the same
physical-key names as the editor bindings, for example `F11`. The walking toggle,
six movement keys, V, Space and F5 must not conflict. Invalid runtime configuration
is rejected, so keep a backup before hand-editing. Escape/modifier keys are not
valid walking bindings.

The extended F5 rows show walking/airborne/noclip status, train-input blocking,
world X/Z, tile and tile-local position, feet/eyes Y, eye height and actual remapped
controls. Walking's HUD does not require the crawling feature. When both features
are enabled, their rows are displayed together.

## Current limitations

- Ground detection uses MSTS terrain triangles. There is no scenery, platform,
  bridge or train collision capsule; the walker can pass through those objects.
- This is not yet a release-ready compatibility claim. Long-distance/tile-boundary
  traversal, physical joystick hardware, multiplayer and arbitrary routes still
  need validation. See [development evidence](technical/walking-development.md).
- Both modes block native train actions, including held callbacks, and gate raw
  device callbacks during driving. F5 and Escape remain available. Entry/exit wait
  for keyboard and mouse release to avoid transferring held train commands.
- Focus loss and pausing stop walking input and mouse capture. The game simulation
  itself follows MSTS's normal pause/background behavior.
