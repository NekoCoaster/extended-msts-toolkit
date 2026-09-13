# Editors and tools

NEMT detects `-toolset` separately from the simulator. The main game's borderless setting does not remove editor or launcher borders. Game timing, crawling and movie overrides are also bypassed in tools mode.

Three independent options are available in the control panel. Apply changes with MSTS closed, then restart Editors & Tools.

| Option | Behavior |
| --- | --- |
| Resizable editor windows and fullscreen | Resize or maximize Route, Activity and Cab Editor. Press **Alt+Enter** in the main viewport to enter borderless fullscreen; press it again to restore the previous window. |
| Move Route Editor tool windows freely | Removes MSTS's magnetic alignment of floating tools. |
| Fix Route Editor slowdown without nearby sounds | Keeps the audio device active with a silent buffer while Route Editor runs. No sound source needs to be placed in the route. |

Route Editor recreates its rendering surfaces and camera projection at the new size. Wider windows reveal more of the world while preserving the vertical field of view. Resizing settles after the drag ends; floating tools remain above the viewport.

Cab Editor centers its 4:3 cab canvas and fits it inside the window without changing its proportions. Unused space is white. Mouse selection follows the fitted image. The cab's original bitmap resolution still limits its detail when enlarged.

Activity Editor keeps its map centered at the same scale. Its right panel and bottom pair normally remain outside the main window. Each group folds inside independently when it would extend beyond the current monitor's usable area. When both fold, the right panel occupies the right edge and the bottom pair sits at the lower left. The map uses the remaining space. A small window may grow to accommodate the original fixed-size controls; very small displays cannot accommodate every native control without overlap.

The settings are stored in `NEMT/settings.ini` beside the game:

```ini
[Editors]
ResizableViewports=true
FreeToolWindows=true
SmoothIdleAudio=true
```

Missing settings default to false. The corresponding installer switches are `-EditorWindows`, `-FreeEditorTools` and `-SmoothEditorAudio`. Like the other installer switches, they describe the requested configuration; include any other features you want to keep enabled when applying settings from the command line.

See [implementation and validation](technical/editors.md).
