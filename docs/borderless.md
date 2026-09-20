# Window modes and resolutions

Enable **Enable borderless windowed mode** in NEMT.exe to remove the window frame. Uncheck it for an ordinary framed window. Apply and restart MSTS.

Choose a display using the dropdown beside the checkbox. Primary display
(automatic) follows Windows' primary display. A saved display that is disconnected
falls back to the primary display; its choice remains saved for reconnection.
This selects window placement, not the rendering GPU or game resolution.

For a display wider or taller than 2048 pixels, NEMT suggests **Enable
High-res support**. Apply and restart MSTS. The integrated fix
changes only process memory and adds no separate DLL. It leaves an existing
local `D3DIM700.dll` or `ddraw.dll` in charge; an unknown file is not proof that
high resolutions work. The form includes the widescreen guide and upstream
project links. See [implementation and validation](technical/display-options.md).

The checkbox reads **Optional** up to and including 2048 pixels in both
dimensions, or **Recommended** when either dimension is larger. If an existing
D3D wrapper is detected, the checkbox explains this and is disabled. The
previous separate status line has been removed.

This setting applies to the simulator. `-toolset` keeps its native launch arguments and window borders; use the separate [editor options](editors.md) for resizing and Alt+Enter borderless fullscreen.

| Launch | Borderless enabled | Borderless disabled |
| --- | --- | --- |
| `train.exe` | Centered borderless window | Ordinary window |
| `train.exe -vm:w` | Centered borderless window | Ordinary window |
| `train.exe -vm:w,1280,720,32` | Borderless 1280×720 window | Framed 1280×720 window |
| `train.exe -vm:1280,720,32` | Fullscreen | Fullscreen |

Use resolutions supported by your installation and display. Existing windowed shortcuts work with either checkbox state. While NEMT is installed, launches without a display-mode argument default to windowed mode.

An explicit fullscreen resolution takes precedence over the checkbox. A smaller borderless window stays centered at its selected size; it is not automatically stretched to fill the monitor. Resolution changes also recenter the window.

If dgVoodoo is installed, see the [recommended window settings](dgvoodoo.md).
