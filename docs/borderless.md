# Borderless window test build

Enable **Enable borderless (-vm:bw) and centered windowed modes** in NEMT, apply, and restart MSTS. This option works independently of the derailment options. No executable bytes are changed on disk.

From the installation directory:

```powershell
.\train.exe -vm:bw
.\train.exe -vm:bw,1280,720,32
.\train.exe -vm:w,1280,720,32
```

The first uses MSTS's configured resolution. The second requests a borderless 1280×720 client area. The third keeps the ordinary frame and centers it. Substitute a resolution supported by your installation that fits your monitor. Borderless does not stretch a smaller resolution to fill the monitor. A launch with no window argument retains MSTS's default behavior.

```ini
[Window]
Enabled=true
CenterWindowed=true
```

`CenterWindowed=false` leaves ordinary `-vm:w` positioning alone. Borderless mode still centers. With `Enabled=false`, `-vm:bw` falls back to ordinary `-vm:w`; other window changes are disabled. Missing flags default off. Changes require a restart. Invalid configuration disables feature installation.

## Host visual checklist

Use the [dgVoodoo baseline](dgvoodoo.md). Keep the same route and graphics settings while comparing launches.

1. Start with `-vm:bw`: confirm settings and route load normally, the menu is centered, and no title bar or resize border remains.
2. Enter an activity, return to the menu, then enter another activity. Check centering, borders, rendering and mouse alignment each time.
3. Repeat with `-vm:bw,1280,720,32` (or a smaller supported resolution). Confirm the view retains that size rather than stretching to the monitor.
4. Alt+Tab away and back; minimize and restore if available. Check focus, controls and rendering. With dgVoodoo's toggle disabled, Alt+Enter should not unexpectedly change display mode.
5. Repeat with `-vm:w,1280,720,32`: expect a normal frame and centered placement at size changes. Check that moving the window manually is not continuously undone.
6. Launch without a window argument to check the existing default mode. If applicable, repeat window tests on another monitor or DPI setting.

Report the launch argument, monitor resolution/scaling, dgVoodoo version and which transition misbehaved. The first borderless build has automated Win32 coverage; in-game borderless behavior is not yet validated. The earlier host-tested MEDS migration remains tagged `nemt-migration-host-tested`.

## Discovery and implementation

The identified images have base address `0x400000`, image size `0x481000`, timestamp `0x3c1625d7`, entry point RVA `0x31edf8` and no executable TLS callbacks. DirectInput is a static import. The EXE CRT reads its command line through `GetCommandLineA` at IAT slot `0x84dbec` before the video-mode parser.

The general option handler at `0x706af0` dispatches `vm` to `0x707000`. That routine consumes the `w` token, optionally consumes `s`, then reads width, height and depth. It does not understand `bw`. NEMT therefore removes only the `b` from recognized `-vm:bw` argument tokens in a private command-line copy. Quotes, other arguments and native resolution suffixes are preserved. Windows-owned command-line storage is not modified. Repeated recognized window options follow the last mode token.

At DLL process attachment, a minimal bootstrap checks the image fingerprint, absence of TLS and the expected command-line import pointer, then redirects that one pointer. It performs no configuration reads, hashing, User32 calls, thread creation or waits. The redirected function runs when the EXE CRT requests its command line, outside the loader entry callback. It checks the complete supported executable hash and reads configuration before installing the window module. This follows the constraints documented for [DllMain](https://learn.microsoft.com/en-us/windows/win32/dlls/dllmain) and the immutable storage returned by [GetCommandLineA](https://learn.microsoft.com/en-us/windows/win32/api/processenv/nf-processenv-getcommandlinea).

The window module chains the game's existing `SetWindowPos` (`0x84df30`) and `ShowWindow` (`0x84df40`) imports. It affects only the main HWND stored at `0x82813a`. The native sizing routine at `0x6963a0` uses cached styles at `0x82818a` and `0x82818e`; these must be updated along with the visible window style. Frame extents are accounted for so requested client dimensions survive border removal. Borderless uses the nearest monitor's full rectangle; ordinary windows use its work area. First appearance and size/frame changes trigger centering. There is no polling loop, topmost enforcement or per-frame window callback.

The IAT mutations participate in the shared address-claim registry. Raw-only transactions allocate no executable gateway page. The initial command-line import is claimed atomically during startup; subsequent window and gameplay transactions reject overlaps and mismatched bytes. Gameplay retains its separate driving-scene readiness gate. No Frida attachment is used.

## Automated coverage

- `tests/window-math.c`: quoted executable/argument paths, case, comma resolutions, optional `s`, tabs, false positives, duplicate options and negative monitor coordinates.
- `tests/window-native.c`: real Win32 window creation, frame removal, exact client dimensions, cached style update, centering after resize, retained manual movement and bordered mode. This is a synthetic window, not an MSTS/dgVoodoo test.
- `tests/window-installer.ps1`: window-only and combined installation, preserved centering preference, unchanged EXE and uninstall across base, widescreen and both LAA variants.

Compile C tests with x86 TCC; tests including `loader.c` need `-ladvapi32 -luser32`. Run the PowerShell test with `-BaseExe`, `-WidescreenExe` and a local `-Scratch` directory. Executable fixtures and research exports are excluded from the package.
