# Neko's Extended MSTS Toolkit — NEMT

**Where we're going, we don't need rails.**

NEMT adds optional gameplay and quality-of-life features to Microsoft Train Simulator: borderless windows, clearer loading messages, widescreen cab-dial corrections, editor improvements, and control of connected locomotives after derailment. The control panel is a small native 32-bit Win32 program written in C; it does not require PowerShell, .NET, Python, a browser runtime, or a modern GUI framework.

[Download NEMT](https://github.com/NekoCoaster/extended-msts-toolkit/releases) · [User guide](docs/README.md) · [Report an issue](https://github.com/NekoCoaster/extended-msts-toolkit/issues)

## Get started

1. Download **NEMT.zip** from the release's **Assets** section and extract the whole ZIP into a folder.
2. Close MSTS, then open **NEMT.exe**. You can also drag `train.exe` onto the window after it opens.
3. Confirm the detected executable, or use **Browse** to select it.
4. Check the features you want and click **Apply**.
5. Close the panel and launch MSTS normally. Restart MSTS whenever you change its NEMT settings.

NEMT leaves `train.exe` unchanged and saves its settings beside the game.

## Native compatibility goal

The frontend intentionally targets the old, well-understood Win32 API and is built as an x86 executable with a Windows XP SP3 API baseline (`WINVER/_WIN32_WINNT = 0x0501`). The compatibility target is:

- Windows XP SP3
- Windows 7
- Windows 10
- Windows 11

Modern-only functionality must be discovered at runtime. For example, the optional P-core preference feature resolves the Windows CPU Set APIs dynamically; on an older system the option is simply unavailable rather than preventing NEMT from starting.

The design baseline is deliberately modest: a single-core Pentium-class machine with roughly 256 MB of RAM should be able to open and use the control panel comfortably.

## Build from source

The source build is intentionally kept simple. The supplied source archive includes **TinyCC 0.9.27 x86 and the required subset of WinAPI headers** under `tools\tcc\`. Extract the complete archive, close any running NEMT window, then double-click:

```text
BUILD AND RUN NEMT.bat
```

That script compiles `src\nemt.c` directly into `build\NEMT.exe` and launches it. No IDE, CMake, PowerShell, .NET, Python, or separately installed SDK is required for the build itself. The batch files use syntax compatible with Windows XP `cmd.exe`.

Keep `build\NEMT.exe.manifest` beside the generated executable for native control styles and DPI behavior. `TEST NEMT.bat` runs the native regression suite using temporary fixtures, not a real game installation. See the [GUI parity review](docs/technical/gui-parity-review.md), `tools/tcc/README.txt` and [third-party notices](THIRD-PARTY.md).

## Features

| Option | What it does |
| --- | --- |
| Prefer P-cores (optional) | Requests the highest detected CPU performance class when the OS and CPU expose the required topology. Defaults off. |
| Skip startup movie | Goes straight to loading, avoiding the movie-related keyboard-control issue. |
| Enable borderless windowed mode | Removes the main game's window border and keeps it centered. |
| Resizable editor windows and fullscreen | Resize or maximize Route, Activity and Cab Editor; Alt+Enter toggles borderless fullscreen. |
| Move Route Editor tool windows freely | Removes magnetic alignment of floating tools. |
| Fix Route Editor slowdown without nearby sounds | Prevents audio-device idle stalls without adding route sound sources. |
| Unlock FPS limit — **Potentially unstable** | Removes the game-side frame cap and applies corrected timing. |
| Show verbose startup and activity loading details | Shows loading activity and terrain-generation progress. |
| Enable deep logging | Records optional diagnostics for troubleshooting. |
| Fix cabview dials for widescreen displays | Corrects dial-needle proportions with a supported widescreen-patched executable. |
| Unmute while in background | Keeps game audio playing when switching to another application. |
| Continue after passing a red signal | Shows the failure message, then lets the simulation resume after dismissal. |
| Remove derailment activity-end message | Keeps a derailment from ending the activity. |
| Unlock camera modes during derailment | Keeps camera selection available after derailment. |
| Enable counter-tilt filter while crawling | Optional throttle-based pitch filtering. |
| Allow connected engines to crawl after derailment | Uses throttle/reverser to move derailed connected locomotives. |

[Explore the options](docs/features.md).

## Compatibility

NEMT supports the identified **MSTS Bin 1.8.052113** executable in its base, widescreen, Large Address Aware (LAA), and widescreen + LAA forms. The native panel checks executable contents before applying changes.

The cab-dial option requires the [MSTS widescreen patch](https://digital-rails.com/wordpress/2018/06/23/running-msts-at-high-resolution/). An unrelated `DINPUT.dll` can prevent installation; NEMT will not overwrite it.

## Change settings or uninstall

Reopen **NEMT.exe**, select the same `train.exe`, adjust your choices and click **Apply**. To remove NEMT, close MSTS and click **Uninstall**. Your executable is unchanged.

[Installation and troubleshooting](docs/installation.md) · [Installed files](docs/installed-files.md)

## Development note

Contributor checksum, toolchain, PR and packaging instructions are in [Build and publishing](docs/technical/maintenance.md). Python 3.11+ is used only for those maintainer checks and runtime rebuilding, not the ordinary frontend build. The complete compiler source must accompany compiler-containing source distributions; see [third-party notices](THIRD-PARTY.md).

The previous PowerShell/WinForms implementation is retained under `legacy/` as a migration and regression reference. It is not the intended runtime frontend.

Developed and Tested by NekoCoaster with Astra.

Released under the [MIT License](LICENSE). See [third-party notices](THIRD-PARTY.md). Microsoft Train Simulator and route assets are not included.
