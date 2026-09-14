# Windowed and borderless mode

The **Enable borderless windowed mode** checkbox controls the border of an ordinary MSTS window. Configuration is in `NEMT/settings.ini`; restart after applying changes.

| Launch | Checkbox on | Checkbox off |
|---|---|---|
| `train.exe` | Borderless window | Bordered window |
| `train.exe -vm:w` | Borderless window | Bordered window |
| `train.exe -vm:w,1280,720,32` | Borderless 1280×720 client area | Bordered 1280×720 client area |
| `train.exe -vm:1280,720,32` | Fullscreen | Fullscreen |

Use a resolution supported by the installation and display. MSTS has no native `-vm:f` token: its parser recognizes `w` for windowed, and resolution-only arguments leave the native fullscreen mode selected. An explicit fullscreen request takes precedence over windowed arguments. Existing width, height and bit-depth values are preserved. With no recognized mode, NEMT supplies `-vm:w`. The former `-vm:bw` alias is unsupported.

`[Window] Enabled=true` enables border removal. `CenterWindowed=true` centers normal framed windows; borderless windows are always centered. A smaller borderless resolution is centered, not stretched to fill the monitor. The no-argument windowed default applies while NEMT is installed, even with border removal disabled.

## Implementation and checks

The command-line copy is prepared outside DllMain. Only valid supported executable/configuration combinations activate features. The explicit fullscreen form is established from the native `0x707000` parser: it consumes `w` if present, then optional `s` (software rendering), then width, height and depth. `s` is not a fullscreen switch. NEMT suppresses conflicting windowed tokens when a native fullscreen resolution is present.

The native window hooks still preserve client size and center on creation/resizing. Automated tests cover quoted executable paths and arguments, native resolution suffixes, fullscreen precedence, default windowing, limiter-option deduplication and monitor centering. Host checks for 1.0.0: repeat menu/activity transitions, Alt+Tab and resolution changes with border removal both on and off; test an explicit fullscreen resolution separately.

## Historical implementation and validation

The following records describe pre-1.0.0 builds and their former `-vm:bw` alias. Current behavior is described above.

The identified images have base address `0x400000`, image size `0x481000`, timestamp `0x3c1625d7`, entry point RVA `0x31edf8` and no executable TLS callbacks. DirectInput is a static import. The EXE CRT reads its command line through `GetCommandLineA` at IAT slot `0x84dbec` before the video-mode parser.

The general option handler at `0x706af0` dispatches `vm` to `0x707000`. That routine consumes the `w` token, optionally consumes `s`, then reads width, height and depth. It does not understand `bw`. NEMT therefore removes only the `b` from recognized `-vm:bw` argument tokens in a private command-line copy. Quotes, other arguments and native resolution suffixes are preserved. Windows-owned command-line storage is not modified. Repeated recognized window options follow the last mode token.

At DLL process attachment, a minimal bootstrap checks the image fingerprint, absence of TLS and an executable command-line import target, then redirects that one pointer. It performs no configuration reads, hashing, User32 calls, thread creation or waits. The redirected function runs when the EXE CRT requests its command line, outside the loader entry callback. It checks the complete supported executable hash and reads configuration before installing the window module. This follows the constraints documented for [DllMain](https://learn.microsoft.com/en-us/windows/win32/dlls/dllmain) and the immutable storage returned by [GetCommandLineA](https://learn.microsoft.com/en-us/windows/win32/api/processenv/nf-processenv-getcommandlinea).

The window module chains the game's existing `SetWindowPos` (`0x84df30`) and `ShowWindow` (`0x84df40`) imports. It affects only the main HWND stored at `0x82813a`. The native sizing routine at `0x6963a0` uses cached styles at `0x82818a` and `0x82818e`; these must be updated along with the visible window style. Frame extents are accounted for so requested client dimensions survive border removal. Borderless uses the nearest monitor's full rectangle; ordinary windows use its work area. First appearance and size/frame changes trigger centering. There is no polling loop, topmost enforcement or per-frame window callback.

The IAT mutations participate in the shared address-claim registry. Raw-only transactions allocate no executable gateway page. The initial command-line import is claimed atomically during startup; subsequent window and gameplay transactions reject overlaps and mismatched bytes. Gameplay retains its separate driving-scene readiness gate. No Frida attachment is used.

## Automated coverage

- `tests/window-math.c`: quoted executable/argument paths, case, comma resolutions, optional `s`, tabs, false positives, duplicate options and negative monitor coordinates.
- `tests/window-native.c`: real Win32 window creation, frame removal, exact client dimensions, cached style update, centering after resize, retained manual movement and bordered mode. This is a synthetic window, not an MSTS/dgVoodoo test.
- `tests/window-installer.ps1`: window-only and combined installation, preserved centering preference, unchanged EXE and uninstall across base, widescreen and both LAA variants.

Compile C tests with x86 TCC; tests including `loader.c` need `-ladvapi32 -luser32`. Run the PowerShell test with `-BaseExe`, `-WidescreenExe` and a local `-Scratch` directory. Executable fixtures and research exports are excluded from the package.

## Host startup compatibility follow-up

The initial 32 KB build failed on a reported Windows 11 host using the supported widescreen + LAA image and WINXPSP2 compatibility flags. Ordinary -vm:w worked; -vm:bw failed even with Window.Enabled=false. No crash event was available. The original bootstrap rejected any command-line import that differed from the DLL's own GetCommandLineA import, which could leave bw untranslated when a compatibility layer redirects that import.

The follow-up build chains an existing executable import target, checks committed executable memory, and rejects null, non-executable and duplicate targets. Exact image headers and the later whole-image hash verification remain enforced. tests/window-bootstrap.c verifies a synthetic compatibility redirect, translation, forwarding and rejection cases. Host testing confirmed that this updated build resolves the host startup failure. The precise redirected API target was not captured, so the compatibility-layer explanation remains an inference.

## Host validation

Validated runtime commit: 018b549. DLL SHA-256: a1f41ae008797fddf4e8aaa8c1bad87a12d52a63c6d4fbd6bb69272c480d61c9 (33,280 bytes). The host diagnostics identified Windows build 26200 and the supported widescreen + LAA executable.

Host testing confirmed successful borderless startup, activity entry, Alt+Tab away and back, activity exit, another activity entry and repeated Alt+Tab. Resolution changes also remained centered and scaled correctly. These observations come from host testing; they are separate from the instrumented VM runs. The exact final dgVoodoo configuration was not captured; no claim is made for every renderer, monitor/DPI configuration or executable variant. Previous migration and MEDS checkpoints remain preserved.
