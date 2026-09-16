# Window modes and resolutions

Enable **Enable borderless windowed mode** in NEMT.exe to remove the window frame. Uncheck it for an ordinary framed window. Apply and restart MSTS.

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
