# Loading details and diagnostic logs

**Show verbose startup and activity loading details** replaces the loading-screen text with the latest observed loading activity. Long paths are shortened to fit the existing single line.

Terrain generation shows completed/total jobs, percentage and an estimated time remaining, for example:

```text
Generating terrain buffers 56/232 24%: ~0m 08s remaining
```

The estimate appears after enough progress is available. Individual jobs take different amounts of time, so the estimate can change and the line can pause during a slow job. After generation, **Preparing route assets...** identifies the next loading stage.

## Optional log

Enable **Write startup diagnostic log** to save `NEMT/startup.log` in the game directory. Logging and loading-screen text are independent options. Activity loading can continue to show detail without reopening the startup log.

The log records file-open/search attempts and results. Missing optional files are often normal. The last recorded file is not proof of a crash cause, and a successful open does not establish that the file's contents are valid. Some startup movie records may follow the normal startup-completion marker.

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
