> [!IMPORTANT]
>
> ## Disclaimer
>
> **Neko's Extended MSTS Toolkit (NEMT)** is an independent collection of enhancements, fixes, tools, and patches for Microsoft's Train Simulator (2001), developed by one guy with far too much time on his hands, whose ADHD has resulted in significantly more features being added over time—well beyond the original goal of only removing MSTS's derailment timer.
>
> **NEMT is not affiliated with, derived from, or associated with any other similarly named toolkit, toolset, utility, project, or product.** Any similarity in names does not imply a connection or endorsement.
>
> This statement does not override the acknowledgements and licenses for third-party components explicitly documented in [THIRD-PARTY.md](THIRD-PARTY.md).

# Neko's Extended MSTS Toolkit — NEMT

**\*MSTS Bin development stops\***

**"Fine, I'll do it myself."**

[Download NEMT](https://github.com/NekoCoaster/extended-msts-toolkit/releases) · [User guide](docs/README.md) · [Report an issue](https://github.com/NekoCoaster/extended-msts-toolkit/issues)

Introducing Neko's Extended MSTS Toolkit, or NEMT for short (Yeah I'm not good at coming up with names)

Originally conceptualized as a seperate smaller project on it's own, dubbed "MSTS Extended Derailment System", Or MEDS for short. The original goal was to simply patch train.exe so that once the derailment event gets triggered, the game won't automatically force the user to exit their simulator after ~20 seconds as this was originally a gripe that I had since as a kid when I always wanted to see what would happen to the trains post-derailment while things were not yet settled down (and one that remaind as a shower thought for many years until now).

This then eventually turned into, "what if we could still use the regular cameras after derailment?" to "what if we allowed the trains to keep moving even after derailment?" and then one thing lead to another and eventually, NEMT is born.

### So what is NEMT?

NEMT adds optional gameplay and quality-of-life features to Microsoft Train Simulator. It features some of the basic improvements such as borderless windows, clearer loading messages, widescreen cab-dial corrections, editor improvements, and control of connected locomotives after derailment.

And in this version v1.2.0, the patcher window has now been refactored into a small native 32-bit Win32 program written in C, eliminating the need for modern framework bloats and dependencies, while self-containing everything tht it needs on it's own to compile and patch MSTS.

As such, this patcher can now run on your grandma's 2005 Windows XP notebook as well xd.

![Patcher Window on Windows XP, 7 and 11](docs/assets/patcher.png)
_NEMT patcher window as captured for version 1.2.0, running on Windows XP, 7 and 11. Future updates may differ in appearance_

## Downloading and Installation

1. Download **NEMT.zip** from the release's **Assets** section and extract the whole ZIP into a folder.
2. Close MSTS, then open **NEMT.exe**. You can also drag `train.exe` onto the window after it opens.
3. Confirm the detected executable, or use **Browse** to select it.
4. Check the features you want and click **Apply**.
5. Close the panel and launch MSTS normally. Restart MSTS whenever you change its NEMT settings.

NEMT leaves `train.exe` unchanged and saves its settings beside the game.

## Native compatibility goal release

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

This compiles `src\nemt.c` directly into `build\NEMT.exe` and launches it. No IDE, CMake, PowerShell, .NET, Python, or separately installed SDK is required for the build itself. The batch files use syntax compatible with Windows XP `cmd.exe`.

Keep `build\NEMT.exe.manifest` beside the generated executable for native control styles and DPI behavior. `TEST NEMT.bat` runs the native regression suite using temporary fixtures, not a real game installation. See the [GUI parity review](docs/technical/gui-parity-review.md), `tools/tcc/README.txt` and [third-party notices](THIRD-PARTY.md).

## Features

| Option                                             | What it does                                                                                                                                                     |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Prefer P-cores (optional)                          | Requests the highest detected CPU performance class when the OS and CPU expose the required topology. Defaults off.                                              |
| Skip startup movie                                 | Skips startup movie for faster loading time. Also resolves keyboard input not working after loading into the simulator.                                          |
| Enable borderless windowed mode                    | Removes the game window border and centers it on the selected display beside the checkbox.                                                                       |
| Enable high-resolution compatibility               | Removes recognized legacy Direct3D dimension limits in memory; automatically disables when using external graphic wrapper DLLs.                                  |
| Resizable editor windows and fullscreen            | Resize or maximize Route, Activity and Cab Editor windows; Use Alt+Enter to toggle borderless fullscreen.                                                        |
| Move Route Editor tool windows freely              | Removes jankly snap alignment of floating tool windows in Route Editor.                                                                                          |
| Fix Route Editor lag when no sound sources present | Prevents Route Editor from lagging when loading into a route with no nearby sound sources playing.                                                               |
| Unlock FPS limit — **Potentially unstable**        | Removes the game-side frame cap and applies corrective timing to frame-rate tied simulator operations.                                                           |
| Show verbose startup and activity loading details  | Shows loading activity and terrain-generation progress messages during startup and sim-loading.                                                                  |
| Enable deep logging                                | Records optional diagnostics for troubleshooting and writes them into NEMT/startup.log                                                                           |
| Fix cabview dials for widescreen displays          | Corrects dial-needle proportions with a when running MSTS in patched widescreen mode.                                                                            |
| Unmute while in background                         | Keeps game audio playing when in background.                                                                                                                     |
| Continue after passing a red signal                | Allows the simulator to resume after passing a red signal (chaos ensues).                                                                                        |
| Remove derailment activity-end message             | Removes "Activity ended -- car derailed" message after 20 seconds, allowing for infinite duration past derailment.                                               |
| Unlock camera modes during derailment              | Allows the use of standard external cameras even after train has derailed.                                                                                       |
| Allow connected engines to crawl after derailment  | Allows locomotives and connected power cars to continue moving forward/backwards even after derailment                                                           |
| Enable counter-tilt filter while crawling          | When crawling, adds a counter force to (try to) prevent trains from nose-diving tilting when crawling on terrain. Not guaranteed to work consistently everytime. |

[Explore the options](docs/features.md).

## Compatibility

NEMT requires at least **MSTS Bin 1.8.052113** but is compatible with patched versions such as the Widescreen patch & LAA or both.

The cab-dial patch option requires train.exe to be patched with the [MSTS widescreen patch](https://digital-rails.com/wordpress/2018/06/23/running-msts-at-high-resolution/).

## Change settings or uninstall

Reopen **NEMT.exe**, select the same `train.exe`, adjust your choices and click **Apply**. To remove NEMT, close MSTS and click **Uninstall**. Your executable is unchanged.

[Installation and troubleshooting](docs/installation.md) · [Installed files](docs/installed-files.md)

## Development note

Contributor checksum, toolchain, PR and packaging instructions are in [Build and publishing](docs/technical/maintenance.md). Python 3.11+ is used only for those maintainer checks and runtime rebuilding, not the ordinary frontend build. The complete compiler source must accompany compiler-containing source distributions; see [third-party notices](THIRD-PARTY.md).

The previous PowerShell/WinForms implementation is retained under `legacy/` as a migration and regression reference. It is not the intended runtime frontend.

Developed and Tested by NekoCoaster with Astra.

Released under the [MIT License](LICENSE). See [third-party notices](THIRD-PARTY.md). Microsoft Train Simulator and route assets are not included.
