# Neko's Extended MSTS Toolkit — NEMT

A small native toolkit for Microsoft Train Simulator. This first migration brings MEDS's activity-end prevention, camera access and connected-engine crawling into one configurable `DINPUT.dll`.

**Loading and HUD test build:** single-line verbose text now covers startup and activity loading, with terrain-buffer progress and estimated remaining time. An automatically included crawl [extended F5 HUD](docs/crawl-hud.md) shows crawl controls and applied thrust without diagnostic file writes. See the [loading guide and validation limits](docs/startup.md). The owner validated the earlier startup display; the owner has also confirmed terrain generation completed and the F5 HUD was visible. The latest HUD alignment/sign and dependency preflight changes still need host validation.

**Borderless foundation:** native `-vm:bw` support and optional window centering are now included. The owner confirmed activity transitions, Alt+Tab and resolution changes; see the [validation and launch guide](docs/borderless.md). The existing MEDS releases remain unchanged. This is a separate local repository; it has not been published to a new GitHub repository.

## Install or migrate

1. Close MSTS and extract the whole package.
2. Open **NEMT.vbs**, or drag your `train.exe` onto it. Registry detection and Browse remain available.
3. Select features and click **Apply**. Enable the window option and use `-vm:bw` for borderless, or `-vm:w` for ordinary windowed mode.

Supports the identified MSTS Bin **1.8.052113** base, widescreen, LAA and widescreen + LAA images. Exact image checks reject other modifications.

On a clean supported executable, the installer does not change `train.exe`. Migrating an existing MEDS executable creates a verified backup and restores only its two known feature patches. Widescreen/LAA modifications are preserved. All subsequent feature changes are configuration-only; the DLL applies gameplay features to process memory after the driving scene becomes ready. The separate window module initializes during normal startup.

The installer upgrades only an owned, hash-matching `DINPUT.dll`. Existing dgVoodoo graphics DLLs and configuration are left alone. There is no Frida, Python, network listener or separate helper required during play.

![Toolkit configuration form](docs/assets/patcher.png)

## Settings

`NEMT/native.ini`:

```ini
[Startup]
VerboseLoading=false
WriteLog=false
UnlockFPS=false

[Window]
Enabled=true
CenterWindowed=true

[Derailment]
PreventActivityEnd=true
UnlockCameras=true
EnableCrawl=true
CrawlStrength=10

[Diagnostics]
WriteStatusJson=false
ShowCrawlHUD=true
```

Settings take effect after restarting MSTS. Crawling requires `PreventActivityEnd=true`; the form enforces this. Invalid manual configuration prevents feature installation. Missing feature flags default off. Thrust ranges from 0–100×; zero disables added thrust while retaining the selected throttle-dependent collision/animation effects.

Use **Uninstall** to remove the owned DLL and configuration. The clean executable remains unchanged. Migration backups and ownership/diagnostic records are retained. To return to MEDS, uninstall NEMT, then apply the preserved MEDS package to the clean executable.

## Documentation

- [Architecture and migration](docs/native-runtime.md)
- [Installed files](docs/installed-files.md)
- [Validation and limits](docs/release-validation.md)
- [Borderless launch guide and implementation](docs/borderless.md)
- [dgVoodoo borderless settings](docs/dgvoodoo.md)
- [Inherited physics equations](docs/physics.md) and [identified patch locations](docs/patches.md)
- [Research history](docs/discovery.md)
- [FPS: prefer the existing -noclamp option](docs/miscellaneous/fps.md)

Developed and Tested by NekoCoaster, Powered by Codex — 2026 | [MIT License](LICENSE). See [third-party notices](THIRD-PARTY.md).

NEMT now checks supported text route track databases for missing section definitions before startup. [Dependency checks and limits](docs/track-dependencies.md) explains the Xtracks warning and what it can detect.
