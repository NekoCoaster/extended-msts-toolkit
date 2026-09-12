# NEMT 1.0.0 validation

## Changes

The current form configures ordinary windowed launches, displays the package version and links to the NEMT repository. Configuration is read only from `settings.ini`. Earlier executable patch migration has been removed; previously modified binaries are rejected without writes. The supported original, widescreen, LAA and combined variants remain accepted.

Startup logging now supports launch/size rotation through `MaxLogSizeKB` and `MaxBackupLogs`. Defaults are 8192 KiB and zero backups. Disabled logging leaves existing logs untouched.

## Automated checks

- Installer: 32 feature/variant cases; unchanged executable bytes, dependency rejection, uninstall, dry-run and unrelated-wrapper preservation. Both prior executable feature patches are rejected without changes.
- Window installer: all four variants, combined features and preserved centering preference.
- Startup/HUD installer: 60 feature combinations across four variants, optional settings and unchanged executable.
- Native command-line tests: ordinary windowing, default windowing, custom dimensions, quoted arguments, fullscreen precedence and centering.
- Compatibility bootstrap: redirected import chaining, invalid targets and duplicate claims.
- Logging: launch rotation, size rollover, bounded file sizes, backup ordering and zero-backup cleanup.
- Existing native, lifecycle, startup, HUD, mutation transaction and feature-validation suites passed during this development cycle. No new gameplay equations were introduced.

## VM observations

Test DLL SHA-256: `097ca76990d08f4e06e618c749cf27c6a1c55c3c5d32da36238999df975f8a0d`.

Normal startup with `-vm:w` and borderless enabled reached a frameless menu. Launching without arguments with borderless disabled reached a framed menu. An explicit `-vm:800,600,32` request with borderless enabled reached the menu through the native fullscreen path. The VM's graphics wrapper still influences the visible presentation; this does not establish exclusive fullscreen behavior on every host.

A live startup with a 4 KiB limit and two backups retained exactly two backups (4052 and 4058 bytes) and a 1941-byte current log. Startup completed after 400 observed operations and 20 text updates. The ordinary 8192 KiB/zero-backup defaults were restored after testing. No Frida was attached.

These are startup smoke checks, not a repeat of every activity, resolution, trainset or host configuration. Earlier activity and host validation remains separately dated in the historical records. The current form screenshot was regenerated and inspected. Release packaging verifies DLL integrity, local documentation links, archive extraction bytes and exclusion of local game/research files.
