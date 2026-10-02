# External camera mouse controls

Enable **Enable TSW styled external camera mouse controls** in
NEMT, click **Apply** with MSTS closed, then start the game. This option defaults
off and is independent of walking mode and derailment camera unlocking.

In front or rear tracking view (number keys **2** and **3**):

- Hold the right mouse button and move left/right to orbit horizontally.
- Keep it held and move up/down to orbit vertically, like Ctrl+Up/Down.
- Keep it held and scroll up to move closer, or down to move farther away.
- Release right-click to stop controlling the camera and show the pointer.

**Shift+9** toggles tracking. When tracking is unlocked, MSTS's original
FPS-style right-click panning takes over; NEMT does not intercept the mouse or
wheel in that mode. Toggle tracking back on to resume mouse orbit and zoom.

Arrow Left/Right, Ctrl+Up/Down and ordinary Up/Down remain available. Zoom changes
the camera's distance from the train, using MSTS's limits, rather than its field
of view. Other camera modes retain their existing controls, including walking's
own right-drag and field-of-view wheel zoom.

Dragging recenters and hides the pointer so orbiting can continue past the screen
edge. Pause, focus loss and camera/activity changes discard pending mouse input.
The initial drag does not jump to the pointer's position. Current sensitivity is
0.003 radians per pixel and 2 metres per wheel notch; partial wheel notches are
accumulated within the current drag.

Advanced setting in `NEMT/settings.ini`:

```ini
[Camera]
ExternalMouseControl=true
```

The user confirmed host operation, including the Shift+9 free-look correction. See [implementation and evidence](technical/external-camera.md).
