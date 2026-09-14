# Using NEMT with dgVoodoo

NEMT leaves dgVoodoo's files and settings unchanged. For NEMT to manage the game window, use the following starting configuration in dgVoodoo and retain the output renderer that already works with your installation.

| dgVoodoo setting | Value |
| --- | --- |
| Application controlled fullscreen/windowed state | Enabled (`AppControlledScreenMode=true`) |
| Disable Alt-Enter to toggle screen state | Enabled (`DisableAltEnterToToggleScreenMode=true`) |
| Resolution | Unforced / application-driven |
| Center app window | Off (`CenterAppWindow=false`) |
| Windowed attributes | Empty |
| Fullscreen attributes | Empty |

These settings let MSTS and NEMT control window size and placement. **Alt+Tab** switches between applications; **Alt+Enter** changes display mode and can conflict with the selected window settings.

Use NEMT's [borderless checkbox and normal launch arguments](borderless.md) to choose windowed or fullscreen mode. Keep a copy of a working dgVoodoo configuration before experimenting with graphics settings. This is a compatibility starting point, not a universal performance preset.

For the wrapper's own setting descriptions, see [dgVoodoo's documentation](https://dgvoodoo2.dege.freeweb.hu/dgVoodoo2/ReadmeGeneral/).
