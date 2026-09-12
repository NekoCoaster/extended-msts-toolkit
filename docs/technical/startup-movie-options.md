# Startup movie options

Open NEMT.vbs, select train.exe, choose the options and click Apply. Restart MSTS afterward. **Select All**, to the left of Apply, checks every available checkbox. It leaves disabled options unchecked and keeps the current thrust slider value.

The single checkbox is **Skip startup movie (fixes keyboard control issue when loading into simulator)**. It bypasses the clip before MSTS opens it, avoiding the movie-related keyboard issue. Skipping has passed host testing. NEMT does not edit the registry, rename GLOBAL/startup.mpg or modify train.exe.

The separate keyboard-recovery checkbox has been removed following a host test where it did not resolve input recovery. Further movie/input troubleshooting is out of scope. The existing recovery setting is tied to the skip checkbox when applying configuration; because playback is bypassed, prevention through skipping is the relevant behavior.

When Skip startup movie is unchecked, MSTS uses its original playback behavior, including its existing movie preference and file lookup. NEMT does not force a previously disabled or missing movie to play. It no longer changes the decoder, movie window ownership, destination rectangle or output binding. The black-picture problem on some host configurations remains unresolved.

```ini
[Startup]
SkipStartupMovie=false
RestoreMovieFocus=false
```

Apply removes the abandoned experimental settings from the generated configuration. The old SeparateMovieWindow, UseSystemMovieDecoder and BindMovieOutput settings are no longer read by the runtime. Earlier investigation documents and alpha release notes are historical evidence, not current setup instructions.

## Implementation and validation

The movie-only ShowLogo getter call at 0x52fbbe is intercepted through the shared validated hook transaction. When skipping is enabled, only the caller's returned local value is changed to zero, before its branch to movie-path construction and playback. The native getter's return value is preserved. No registry setter is called by this override. When disabled, the original value passes through unchanged.

The call at 0x52fc29 wraps original playback only to restore input afterward. Native playback still owns decoding, rendering, skipping and cleanup. Focus recovery only runs when MSTS is the valid, enabled, non-minimized foreground window and the temporary movie procedure has been removed.

Installer checks cover both states of the combined option, skip-only installation, uninstall and unchanged executable bytes. The compact form remains 760x648 at normal scaling. Earlier native hook and focus-guard tests remain valid for the unchanged DLL, but do not establish that recovery fixes every host setup.

## Quick check

With the movie available and normally enabled, apply Skip startup movie and launch MSTS: it should go directly to loading. Uncheck it and restart: native movie behavior should return. The unchecked option restores native playback behavior; no separate keyboard-repair promise is made for that path.
