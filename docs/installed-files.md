# Installed files

| File | Purpose |
|---|---|
| `DINPUT.dll` beside `train.exe` | DirectInput forwarding plus the native toolkit and enabled features. |
| `NEMT/native.ini` | Feature flags, thrust strength and optional diagnostics. Read at startup/readiness; restart to apply edits. |
| `NEMT/installation.json` | Installer ownership and payload hash, saved option states. Does not control gameplay. |
| `NEMT/startup.log` (optional) | Startup-only file activity trace; created only when Startup.WriteLog is enabled. |
| `NEMT/status.json` | Installer placeholder by default; live snapshots only if diagnostic logging is enabled. |

With `WriteStatusJson=false`, the DLL does not open or write the status file, and its worker exits after hook installation. The placeholder is not a live status indicator. With logging enabled, snapshots are overwritten approximately once a second; they are not a growing history. The legacy native telemetry field names are retained for tooling compatibility.

Apply preserves an explicit logging opt-in. Uninstall removes the owned loader and native configuration, retains status/ownership records and leaves the clean executable unchanged. Migration backups use the `.nemt-migration.<hash>.bak` suffix and are retained beside the executable.

When upgrading MEDS, the old MEDS/MSTS-Derailment folder may remain with disabled ownership metadata and old diagnostic snapshots. Known active legacy runtime files are removed; arbitrary user files are not recursively deleted.

Registry detection only reads the current-user/local-machine MSTS `EXE Path` and `Path` entries in both registry views. An explicitly supplied executable takes priority, and all detected candidates undergo normal compatibility checks.

The optional extended F5 HUD reads in-memory telemetry and adds no files or file writes. Activity loading detail likewise does not reopen startup.log.
