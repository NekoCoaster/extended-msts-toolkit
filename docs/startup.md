# Loading details and diagnostic logs

**Show verbose startup and activity loading details** replaces the loading-screen text with the latest observed loading activity. Long paths are shortened to fit the existing single line.

Terrain generation shows completed/total jobs, percentage and an estimated time remaining, for example:

```text
Generating terrain buffers 56/232 24%: ~0m 08s remaining
```

The estimate appears after enough progress is available. Individual jobs take different amounts of time, so the estimate can change and the line can pause during a slow job. After generation, **Preparing route assets...** identifies the next loading stage.

## Optional log

Select **Enable deep logging (Optional; Use only for debugging or troubleshooting issues)** to save `NEMT/startup.log`. Logging and loading-screen text remain independent. The existing `[Startup] WriteLog` setting and `-StartupLog` command-line switch are retained for compatibility.

Deep logging records startup and activity-loading file operations, loaded module paths, Windows/display information, DirectSound/DirectDraw creation results, DLL loads and native error dialogs. Local timestamps use this format:

```text
2026-09-14 17-07-30.123: API BEGIN | id=1 | tid=1234 | DirectSoundCreate; device=default
```

This is an illustrative line, not a measurement. Matching API END records include results and elapsed milliseconds measured independently of the wall clock. A BEGIN without END means completion was not recorded; it does not by itself prove that API caused the crash. Native message-box durations include the time spent waiting for dismissal.

Every completed record is synchronously written and flushed before the intercepted operation continues. There is no deferred logging queue. Selected first-chance exception records include a code and address and never suppress the exception. They may represent an exception that the application handles normally. Logging cannot guarantee a final record after abrupt termination, stack corruption, a blocked logging thread or hardware/power failure. Operations that never reach a logging hook cannot be reconstructed.

Missing optional files are often normal. A successful open does not validate file contents, and the last file is not proof of a crash cause. Deep logging is not a full stack trace or a trace of every internal renderer/parser call. It adds disk I/O and can change timing; disable it after troubleshooting.

Logging is off unless selected. With default settings, each logged launch starts a fresh file. Disabling logging leaves existing logs untouched. Uninstall also retains diagnostic records.

For a different retention policy, close MSTS and edit these entries in `NEMT/settings.ini`:

```ini
[Startup]
MaxLogSizeKB=8192
MaxBackupLogs=0
```

The size limit accepts **4–65536 KB** and backup count **0–20**. Zero backups replaces old content when a new log begins or the size limit is reached. With backups, `startup.1.log` is the newest archived log. Reducing the count removes excess numbered backups when logging next starts. Restart MSTS after edits.

## Main-menu welcome

The main game adds a NEMT activation/help message below the original welcome line. The stock footer uses more of the empty space beside the navigation buttons so the full paragraph fits. Menu hover help continues to work. This message is independent of verbose loading and is omitted in Editors and Tools (`-toolset`).
