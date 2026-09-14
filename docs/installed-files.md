# Files installed beside MSTS

| File | Purpose |
| --- | --- |
| `DINPUT.dll` beside `train.exe` | Runs the enabled toolkit features. |
| `NEMT/settings.ini` | Saves feature choices, crawl strength, HUD placement and diagnostic preferences. |
| `NEMT/installation.json` | Lets the installer identify the files it owns. |
| `NEMT/status.json` | Status placeholder by default. Ordinary use does not continuously update this file. |
| `NEMT/startup.log`, when enabled | Optional loading diagnostics. Numbered backups may also be present if configured. |

Apply requires MSTS to be closed. Settings take effect after a restart. Use the control panel for normal configuration and Uninstall for removal.

The extended F5 HUD does not need a log file. Startup logging is optional and is controlled separately. See [logging and retention](startup.md).

Uninstall removes the owned runtime and settings while retaining ownership and diagnostic records. NEMT leaves `train.exe`, the startup movie, route files and unrelated graphics-wrapper files unchanged.
