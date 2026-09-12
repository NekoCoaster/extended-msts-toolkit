# dgVoodoo and borderless mode

**Recommended comparison baseline.** Borderless operation has been validated by the owner on their host; the exact final dgVoodoo configuration was not captured. The native borderless test build implements `-vm:bw`; follow the [visual checklist](borderless.md).

For a toolkit-managed window, start with:

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

The installed test configuration already has application-controlled mode and the Alt+Enter toggle disabled, but uses WARP and dgVoodoo centering. It was left unchanged. No optimal-performance claim is made; the borderless tests must cover custom sizes, transitions, input coordinates, Alt+Tab, minimize/restore, monitors and DPI.
