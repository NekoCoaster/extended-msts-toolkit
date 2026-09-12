# Movie window rendering comparison — alpha.6

## Alpha.5 regression and alpha.6 follow-up

On the host, alpha.5 skipped directly to loading without showing the movie. The supplied startup log completed in about 2.9 seconds and contained no movie geometry record. This does not establish an open failure: the earlier record was emitted only after a successful open and only while the startup log remained active.

Alpha.6 leaves the original parent and styles intact while opening the decoder. It moves the owned-window conversion to the movie-only ShowWindow call, reached after a successful open. Keyboard recovery from alpha.4 remains unchanged. This is a comparison build, not a confirmed playback repair.

Optional startup logging now records the native ShowLogo preference, playback entry, decoder-open results, successful arrival at ShowWindow, and playback return. A small number of records can append to the existing startup.log after its normal closing point, subject to the configured size limit. They do not create a second log or replace earlier startup evidence. Logging does not change the native preference.

Static analysis shows that MSTS clears ShowLogo before opening the movie and restores it on successful cleanup. Some failure paths bypass that restoration. A disabled preference therefore needs to be distinguished from a decoder failure; alpha.6 does not silently enable a deliberately disabled movie.

## Current host test

1. Close MSTS, pull `codex/settings-cab-investigation`, run `NEMT.vbs`, verify **1.1.0-alpha.6**, and Apply with startup diagnostic logging enabled.
2. Keep the existing graphics settings. If SeparateMovieWindow was temporarily disabled for comparison, set it back to true in `NEMT/settings.ini` for this test.
3. Launch normally and report whether the movie plays or skips. Share the new startup.log, including its MOVIE lines, either way.
4. If the movie plays, test both finishing and skipping it, then check keyboard controls in an activity.

Automated checks cover opening with the original parent intact, subsequent hidden-window ownership/geometry, decoder/focus behavior, native preference return/value preservation, bounded diagnostic append after startup closes, supported hook bytes, installer persistence and runtime regressions. They do not validate actual video rendering.

## Earlier alpha.5 design (historical)


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
