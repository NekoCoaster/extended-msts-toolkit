# Movie window rendering comparison — alpha.5

Alpha.4 restored keyboard control after both finishing and skipping the movie, but did not fix the black video in windowed mode. A subsequent fullscreen host test showed the video playing behind a centred black rectangle, approximately 640×480 in the supplied 1920×1080 image. That establishes visible decoding in the fullscreen case and points toward window layering or destination geometry. It does not establish that both display modes have identical renderer behavior.

## Targeted change

MSTS uses a child MCI window in windowed mode and a popup in fullscreen mode. It sets `MCIWNDF_NOAUTOSIZEMOVIE` and positions the movie window without explicitly updating the video's destination rectangle in this routine.

Alpha.5 converts the movie window into a borderless popup owned by the main MSTS window before opening the media. Just before showing it, the runtime centres it over the main client area, queries the movie source rectangle, and explicitly fits the destination rectangle into the movie client area while preserving aspect ratio. It requests a repaint. The original movie window size, playback loop, skip controls and cleanup remain in use. There is no new player process, always-on-top setting, codec install or graphics-wrapper modification.

The additional checked instruction site is the movie-only ShowWindow call at `0x52fe51`. It chains the executable's current ShowWindow import, including NEMT's existing window wrapper when present. The startup movie open wrapper handles ownership before the decoder opens; the main game window is not reparented.

```ini
[Startup]
SeparateMovieWindow=true
UseSystemMovieDecoder=true
RestoreMovieFocus=true
```

Apply writes `SeparateMovieWindow=true` by default. Set it to `false` and restart for an alpha.4-style comparison; Apply preserves the explicit value. The two earlier settings remain independent, and the host-validated keyboard recovery code is unchanged.

## Host test

1. Close MSTS, pull the testing branch, open `NEMT.vbs` and confirm **1.1.0-alpha.5**. Apply your chosen features. Enable **Write startup diagnostic log** for this comparison.
2. Keep the same dgVoodoo settings and test `-vm:w`. Check whether video is visible and whether the black rectangle has disappeared.
3. Repeat the fullscreen launch that previously showed video behind the rectangle. Record any change to the picture, placement or black overlay.
4. Check keyboard controls after the clip finishes and after skipping it. Switching away during playback should still work normally.
5. If rendering remains wrong, include the `MOVIE WINDOW` line from `NEMT/startup.log`, if present. It records client/source/destination rectangles and the destination-update result once at startup, without per-frame logging. If that line is absent, report that too.

## Validation boundary

Automated tests pass for real hidden Win32 window ownership, border removal, centering, aspect fitting, disabled-option bypass, movie driver/focus behavior, supported instruction sites and settings persistence. These tests do not decode or render the actual movie. This is an experimental comparison build awaiting host rendering validation, not a confirmed black-screen fix.

The [earlier movie investigation](startup-movie.md) records the failed decoder/settings comparisons and successful keyboard tests. Microsoft documents the required style handling for [SetParent](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setparent) and the [MCIWnd messages](https://learn.microsoft.com/en-us/windows/win32/multimedia/mciwnd-messages) used for source/destination geometry.
