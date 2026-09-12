# Startup movie and keyboard recovery — alpha.4

## Findings

The startup clip produced audio but only a black rectangle on the host with NEMT removed as well as installed. dgVoodoo was enabled, initially using D3D12 with no GDI hook. Enabling `SystemHookFlags=gdi`, then also selecting `OutputAPI=d3d11_fl11_0`, did not restore the image in those host comparisons. Neither setting change is a confirmed solution for this installation.

MSTS's movie opener at `0x52ffb3` first requests `tsmpegvideo!<filename>` for MPEG files, then retries the plain filename only if opening returns an error. A driver can successfully open and play audio without producing a visible picture, so that fallback need not run for the reported symptom. The VM's 32-bit MCI registry associates `tsmpegvideo` with the old `tsqtz32.dll` and `MPEGVideo` with Windows' `mciqtz32.dll`.

The playback function at `0x52fc32` temporarily subclasses the main window. Its movie procedure at `0x52fb70` discards `WM_ACTIVATEAPP`. Successful completion or skipping restores the saved procedure, but does not explicitly restore keyboard focus or replay the current application activation state. This is a plausible cause of the keyboard symptom; a new host comparison is required to establish whether the correction resolves it.

## Test build

Alpha.4 adds two startup-only settings, enabled when applying this package:

```ini
[Startup]
UseSystemMovieDecoder=true
RestoreMovieFocus=true
```

The decoder option tries Windows' `mpegvideo` driver first for `.mpg` files. If that open fails, it retains the original opener as fallback. It does not install codecs, modify the MCI registry, alter the clip or change dgVoodoo configuration.

The focus option wraps the original playback call. After the original procedure has been restored, it focuses the main window if necessary and sends `WM_ACTIVATEAPP` through the normal message chain. It runs only if MSTS's main window is currently foreground, valid, enabled and not minimized. It never forces MSTS ahead of another application. An incomplete original movie cleanup is left alone rather than sending activation messages into the temporary movie procedure.

The checked call sites are `0x52fc29` (playback) and `0x52fd4a` (open). Installation uses the shared byte-checked transaction at normal command-line startup, outside the loader lock. The wrappers are dormant when the movie is disabled or missing. No Frida, additional player process, recurring worker or per-frame writes are used.

These are comparison fixes, not confirmed playback or keyboard results. Automated tests mock the media and focus APIs and verify selection, fallback, return preservation, focus guards and disabled settings. Supported executable sites and installer persistence also pass.

## Host checks

1. Close MSTS, pull `codex/settings-cab-investigation`, run `NEMT.vbs`, confirm **1.1.0-alpha.4**, and Apply the desired features. Both movie settings above are written automatically; there is no extra checkbox.
2. Ensure the clip is named `GLOBAL\startup.mpg` and the simulator is configured to show it. Use the same dgVoodoo configuration for the before/after comparison.
3. Let the clip finish. Check whether video appears, then load an activity and test the keyboard before Alt-Tabbing.
4. Restart and skip the clip. Repeat the keyboard check. Also test switching away during playback: the game should not pull itself back to the foreground.
5. If the image remains black, report whether keyboard input is now working. We can isolate the decoder change by setting `UseSystemMovieDecoder=false` in `NEMT/settings.ini`, restarting, and comparing. `RestoreMovieFocus=false` independently restores the old focus behavior. Apply preserves explicit choices for these two settings.

The compact form uses a 760×648 client area at normal scaling. Scrolling remains available for smaller/high-DPI desktops. No existing option was removed.

## References

- [Microsoft: MCIWndCreate](https://learn.microsoft.com/en-us/previous-versions/ms709626(v=vs.85)) describes the legacy movie window and its styles.
- [Microsoft: SetFocus](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setfocus) describes focus delivery on the owning thread.
- [dgVoodoo documentation](https://dgvoodoo2.dege.freeweb.hu/dgVoodoo2/ReadmeGeneral/) describes GDI cutscene hooking and mixed-rendering limitations. Those settings alone did not resolve this host case.
