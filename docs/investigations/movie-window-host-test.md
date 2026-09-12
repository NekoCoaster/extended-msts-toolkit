# Movie window rendering comparison — alpha.6

> Historical investigation: alpha.8 removes all experimental movie rendering changes. Use the [current movie options](../startup-movie-options.md) for setup.

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

## VM comparison — 12 September 2026, alpha.6

The host log reported `ShowLogo=0`; MSTS skipped before calling the movie playback routine. This is distinct from the original black-picture issue. No crash or forced termination was reported before the host skip, so the origin of the disabled preference remains unproven.

In the development VM, ShowLogo was already 1. The first launch still skipped because the registry installation path was C:\MSTS, whose GLOBAL\startup.mpg retained its .bak suffix. Restoring the file in both that location and the designated C:\codex\derail\MSTS test installation allowed playback. No registry value was changed. The test executable remained byte-for-byte unchanged.

Normal launches used train.exe -vm:w from the designated test directory. No Frida was attached. The VM graphics wrapper used d3d11warp with pass-through disabled; these results do not establish behavior on the hardware host's different rendering backend.

| Decoder option | Separate window | Observation |
| --- | --- | --- |
| Original | Disabled | Visible Kuju animation in the original bordered movie window |
| System | Disabled | Visible Microsoft logo in the original movie window |
| System | Enabled | Visible ACES image in the owned popup; the underlying main window remained black |

The final combination opened successfully at 750 ms, applied the destination rectangle successfully at 765 ms, returned from playback with the saved movie procedure cleared at 12,875 ms, and reached the main event loop at 14,265 ms. These are fresh alpha.6 measurements. Initial black captures were insufficient: the clip opens with dark frames, and capturing only the main window does not establish what the owned popup displays.

The keyboard recovery code remained enabled. This comparison tested startup and menu return, not keyboard controls in a driving activity; the earlier host validation remains the evidence for that behavior. The movie files are left enabled for continued testing.

The native registry preference is the DWORD ShowLogo under the 32-bit HKLM\SOFTWARE\Microsoft\Microsoft Games\Train Simulator\1.0\HWRenderer key (shown beneath WOW6432Node on 64-bit Windows). A host reset to 1 should be performed with MSTS closed. Compatibility registry virtualization can provide a per-user override; if the runtime still reports 0 after resetting the machine value, inspect that override rather than changing unrelated settings.

## Host follow-up and output binding — alpha.7

Resetting ShowLogo to 1 restored host movie playback, but only audio was audible. All four combinations of SeparateMovieWindow and UseSystemMovieDecoder still produced a black picture. The separate-window setting changed the outline to a thin white underline; this is not evidence of video output. The supplied alpha.6 log showed ShowLogo=1, successful system decoder open at 1,688 ms, source 640x480, destination assignment success at 1,719 ms, and normal playback return at 11,000 ms. It did not identify the decoder's display-window handle.

Alpha.7 queries that handle using MCI_STATUS / MCI_DGV_STATUS_HWND, assigns the finalized movie window using MCI_WINDOW / MCI_DGV_WINDOW_HWND, and queries again. The assignment occurs after a successful open and any window conversion, before normal ShowWindow/playback. A rejected command is logged without cancelling playback. BindMovieOutput is enabled by Apply, independently configurable, and preserves explicit false values. No new instruction ranges, DLL dependencies, external player or registry modifications are introduced.

The VM accepted the assignment at 781 ms; the output handle was already correct before assignment and remained correct afterward. Playback returned at 12,828 ms with the saved movie procedure cleared. The screenshot captured the subsequent loading scene, not the video, so this run establishes command acceptance and completion only. The hardware-host outcome remains unknown. The [alpha.7 test instructions](../../releases/v1.1.0-alpha.7.md) require one comparison, not another four-way matrix.

Microsoft's [MCI window command](https://learn.microsoft.com/en-us/windows/win32/multimedia/window) distinguishes the decoder's destination window from window placement. If this assignment does not repair host output, the investigation must move to the renderer/presentation path; decoder-open success alone cannot diagnose why pixels are absent.
