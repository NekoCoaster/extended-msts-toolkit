# Neko's Extended MSTS Toolkit — NEMT

**Where we're going, we don't need rails.**

NEMT adds optional gameplay and quality-of-life features to Microsoft Train Simulator: borderless windows, clearer loading messages, widescreen cab-dial corrections, and control of connected locomotives after derailment. Choose the features you want in one control panel and launch MSTS normally.

[Download NEMT](https://github.com/NekoCoaster/extended-msts-toolkit/releases) · [User guide](docs/README.md) · [Report an issue](https://github.com/NekoCoaster/extended-msts-toolkit/issues)

## Get started

1. Download **NEMT.zip** from the release's **Assets** section and extract the whole ZIP into a folder.
2. Close MSTS, then open **NEMT.vbs**. You can also drag your installed `train.exe` onto it.
3. Confirm the detected executable, or use **Browse** to select it.
4. Check the features you want and click **Apply**. **Select All** checks every available option; you can uncheck any afterward.
5. Close the panel and launch MSTS normally. Restart MSTS whenever you change its NEMT settings.

Keep the extracted package together: the launcher needs its accompanying files. NEMT leaves `train.exe` unchanged and saves its settings beside the game.

## Features

| Option | What it does |
| --- | --- |
| Skip startup movie | Goes straight to loading, avoiding the movie-related keyboard-control issue without registry edits or renaming the clip. |
| Enable borderless windowed mode | Removes the main game's window border and keeps it centered. Does not apply to `-toolset`. |
| Resizable editor windows and fullscreen | Resize or maximize Route, Activity and Cab Editor; Alt+Enter toggles borderless fullscreen. Activity panels fold inside when needed. |
| Move Route Editor tool windows freely | Removes magnetic alignment of floating tools. |
| Fix Route Editor slowdown without nearby sounds | Prevents audio-device idle stalls without adding route sound sources. |
| Unlock FPS limit — **Potentially unstable** | Removes the game-side frame cap and applies corrected timing. Actual performance still depends on the installation and hardware. |
| Show verbose startup and activity loading details | Shows loading activity and terrain-generation counts, progress and estimated remaining time. |
| Enable deep logging | Records optional startup, activity-loading and audio/graphics diagnostics for troubleshooting. |
| Fix cabview dials for widescreen displays | Corrects dial-needle proportions with a supported widescreen-patched executable. |
| Unmute while in background | Keeps game audio playing when switching to another application. |
| Continue after passing a red signal | Shows the failure message, then lets the simulation resume after dismissal. |
| Remove derailment activity-end message | Keeps a derailment from ending the activity. |
| Unlock camera modes during derailment | Keeps camera selection available after derailment. |
| Enable counter-tilt filter while crawling | Optional throttle-based pitch filtering; defaults off and preserves manual steering. |
| Allow connected engines to crawl after derailment | Uses throttle/reverser to crawl, horn/whistle to roll upright, and train brake keys to steer derailed connected locomotives. Includes strength and HUD-position controls. |

[Explore the options](docs/features.md), including crawling controls and feature requirements.

## Compatibility

NEMT supports the identified **MSTS Bin 1.8.052113** executable in its base, widescreen, Large Address Aware (LAA), and widescreen + LAA forms. The panel checks compatibility before applying changes. A matching version label alone does not guarantee that another modified executable is supported.

The cab-dial option requires the [MSTS widescreen patch](https://digital-rails.com/wordpress/2018/06/23/running-msts-at-high-resolution/); the panel enables that checkbox when a supported patched executable is selected.

Using dgVoodoo? Follow the [window settings guide](docs/dgvoodoo.md). NEMT leaves its graphics files and configuration alone. An unrelated `DINPUT.dll` can prevent installation; NEMT will not overwrite it.

## Change settings or uninstall

Reopen **NEMT.vbs**, select the same `train.exe`, adjust your choices and click **Apply**. To remove NEMT, close MSTS and click **Uninstall**. Diagnostic and ownership records may remain; your executable is unchanged.

[Installation and troubleshooting](docs/installation.md) · [Installed files](docs/installed-files.md)

## Documentation

- [User guide](docs/README.md): installation, options, window modes, crawling and loading messages.
- [Technical documentation and testing evidence](docs/technical/README.md): implementation, development history and validation limits.

Developed and Tested by NekoCoaster with Astra.

Released under the [MIT License](LICENSE). See [third-party notices](THIRD-PARTY.md). Microsoft Train Simulator and route assets are not included.
