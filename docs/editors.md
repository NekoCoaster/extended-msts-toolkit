# Editors and tools

NEMT detects `-toolset` separately from the simulator. The main game's borderless setting does not remove editor or launcher borders. Game timing, crawling and movie overrides are also bypassed in tools mode.

The verbose startup/loading details and optional startup log also work in Editors & Tools.

Five independent options are available in the control panel. Apply changes with MSTS closed, then restart Editors & Tools.

| Option | Behavior |
| --- | --- |
| Resizable editor windows and fullscreen | Resize or maximize Route, Activity and Cab Editor. Press **Alt+Enter** in the main viewport to enter borderless fullscreen; press it again to restore the previous window. |
| Move Route Editor tool windows freely | Removes MSTS's magnetic alignment of floating tools. |
| Fix Route Editor slowdown without nearby sounds | Keeps the audio device active with a silent buffer while Route Editor runs. No sound source needs to be placed in the route. |
| Swap arrow keys with WASDEQ controls in route editor | Uses configurable camera keys and moves their original shortcuts onto the corresponding arrow combinations. |
| Remove Route Editor mouse-panning limit | Keeps mouse-drag camera rotation responsive after MSTS's invisible pointer reaches its screen bounds, on both axes. |

Route Editor recreates its rendering surfaces and camera projection at the new size. Wider windows reveal more of the world while preserving the vertical field of view. Resizing settles after the drag ends; floating tools remain above the viewport.

Object selection and placement follow the mouse across the enlarged viewport. The red compass stays centered at the top.

The mouse-panning option fixes a native MSTS problem: its camera uses an invisible mouse position that stops at the edges of the screen. This feels like an angle limit even though the Route Editor's free camera has no such angle clamp. NEMT uses relative mouse movement while the camera-pan button is held, so you can keep turning horizontally or vertically. It retains the native sensitivity, regular cursor coordinates and object-drag behavior. This option works independently of resizing and camera key swaps.

Cab Editor centers its 4:3 cab canvas and fits it inside the window without changing its proportions. Unused space is white. Mouse selection and native cursor positioning follow the fitted image, including fullscreen instrument selection. The cab's original bitmap resolution still limits its detail when enlarged.

Activity Editor keeps its map centered at the same scale. Its right panel and bottom pair normally remain outside the main window. Each group folds inside independently when it would extend beyond the current monitor's usable area. When both fold, the right panel occupies the right edge and the bottom pair sits at the lower left. The map uses the remaining space. A small window may grow to accommodate the original fixed-size controls; very small displays cannot accommodate every native control without overlap.

With resizable editor windows enabled, scroll up over Activity Editor's map to zoom in and down to zoom out. Zoom uses the same steps and limits as the native zoom buttons. Scrolling over floating tools and panels retains their normal behavior.

The settings are stored in `NEMT/settings.ini` beside the game:

```ini
[Editors]
ResizableViewports=true
FreeToolWindows=true
SmoothIdleAudio=true
SwapArrowKeys=true
UnlimitedMousePan=true
RE_CAM_FORWARD=w
RE_CAM_BACKWARD=s
RE_CAM_LEFT=a
RE_CAM_RIGHT=d
RE_CAM_UP=e
RE_CAM_DOWN=q
```

Missing feature switches default to false. The corresponding installer switches are `-EditorWindows`, `-FreeEditorTools`, `-SmoothEditorAudio`, `-SwapEditorKeys` and `-UnlimitedEditorPan`. Like the other installer switches, they describe the requested configuration; include any other features you want to keep enabled when applying settings from the command line.

## Camera key swaps

Enable the swap checkbox, then edit the six `RE_CAM_*` values in `[Editors]` to customize it. Missing bindings use the defaults above. Apply preserves custom bindings; restart the editor after changing them.

With the defaults, W/S move forward/backward, A/D move left/right and E/Q move up/down. Up/Down/Left/Right take over the original W/S/A/D commands; Ctrl+Up and Ctrl+Down take over E and Q. For example, Up becomes the original W wireframe shortcut. A displaced command still requires its usual editing mode.

Shift retains faster camera movement and the displaced shortcuts' Shift modifier. Ctrl+letter commands such as Ctrl+S remain available. Ctrl+Up/Down consumes Ctrl when invoking the displaced E/Q command. Ctrl+Left/Right retains native rotation; Alt shortcuts retain their normal behavior. Swapping applies only while the Route Editor viewport has keyboard focus, leaving text fields, palettes and dialogs alone.

Values are case-insensitive physical key names: A–Z, 0–9, F1–F12, Space, Tab, Enter, Backspace, Home, End, PageUp, PageDown, Insert, Delete, Minus, Equals, Comma, Period, Slash, Semicolon, Apostrophe, Backquote, LBracket, RBracket and Backslash. Other physical keys can use a DirectInput scan code such as `0x47` for numpad 7. Names follow MSTS's physical US keyboard positions. Use six distinct keys; arrows, modifier keys, Escape and scan code zero are reserved. An invalid enabled binding rejects configuration rather than installing an ambiguous swap.

See [implementation and validation](technical/editors.md).
