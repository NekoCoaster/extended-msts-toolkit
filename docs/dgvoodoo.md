# dgVoodoo and future borderless mode

**Proposed compatibility baseline, not yet a validated NEMT borderless profile.** This build migrates MEDS only; `-vm:bw` is not implemented. Continue using `-vm:w` for now.

For a future toolkit-managed window, start with:

| dgVoodoo option | Proposed setting |
|---|---|
| Application controlled fullscreen/windowed state | Enabled (`AppControlledScreenMode=true`) |
| Disable Alt-Enter to toggle screen state | Enabled (`DisableAltEnterToToggleScreenMode=true`) |
| Resolution | Unforced / application-driven |
| Center app window | Off once NEMT owns centering |
| Windowed attributes | Empty; avoid AlwaysOnTop and FullscreenSize |
| Fullscreen attributes | Empty; do not force fake fullscreen |
| Output API | Keep the working hardware renderer; WARP is software rendering |

This proposal gives MSTS/NEMT control of mode, dimensions and placement. Allowing dgVoodoo's Alt+Enter toggle could change the screen state independently and conflict with that ownership. Alt+Tab is a separate operation and should remain available; it still needs live testing.

dgVoodoo already supports `WindowedAttributes=Borderless` and `CenterAppWindow=true`. That is a useful wrapper-only comparison. `FullscreenSize` instead expands presentation to fullscreen dimensions, which differs from preserving a custom window size. These behaviors are described in [Dege's official documentation](https://dgvoodoo2.dege.freeweb.hu/dgVoodoo2/ReadmeGeneral/).

The installed test configuration already has application-controlled mode and the Alt+Enter toggle disabled, but uses WARP and dgVoodoo centering. It was left unchanged. No optimal-performance claim is made; the future borderless tests must cover custom sizes, transitions, input coordinates, Alt+Tab, minimize/restore, monitors and DPI.
