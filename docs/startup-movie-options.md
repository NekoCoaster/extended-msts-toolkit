# Startup movie options

Open NEMT.vbs, select train.exe, choose the options and click Apply. Restart MSTS afterward. **Select All**, to the left of Apply, checks every available checkbox. It leaves disabled options unchecked and keeps the current thrust slider value.

- **Skip startup movie** bypasses the clip before MSTS opens it. The change lasts only for the running process. NEMT does not write the movie preference to the registry or rename GLOBAL/startup.mpg. This option is initially unchecked.
- **Restore keyboard control after movie** keeps the input recovery that passed host tests after both normal completion and skipping during playback. It is initially checked in the form. It does not bring MSTS forward when another application has focus.

Both options are independent. Leaving the keyboard option checked while skipping the movie is harmless and keeps it ready if movie playback is enabled later.

When Skip startup movie is unchecked, MSTS uses its original playback behavior, including its existing movie preference and file lookup. NEMT does not force a previously disabled or missing movie to play. It no longer changes the decoder, movie window ownership, destination rectangle or output binding. The black-picture problem on some host configurations remains unresolved.

```ini
[Startup]
SkipStartupMovie=false
RestoreMovieFocus=true
```

Apply removes the abandoned experimental settings from the generated configuration. The old SeparateMovieWindow, UseSystemMovieDecoder and BindMovieOutput settings are no longer read by the runtime. Earlier investigation documents and alpha release notes are historical evidence, not current setup instructions.

## Implementation and validation

The movie-only ShowLogo getter call at 0x52fbbe is intercepted through the shared validated hook transaction. When skipping is enabled, only the caller's returned local value is changed to zero, before its branch to movie-path construction and playback. The native getter's return value is preserved. No registry setter is called by this override. When disabled, the original value passes through unchanged.

The call at 0x52fc29 wraps original playback only to restore input afterward. Native playback still owns decoding, rendering, skipping and cleanup. Focus recovery only runs when MSTS is the valid, enabled, non-minimized foreground window and the temporary movie procedure has been removed.

Automated checks cover skip on/off, getter return preservation, focus guards, supported executable hook bytes, all four installer option combinations, skip-only/focus-only installations, removal of obsolete settings, uninstall and unchanged executable bytes. The form layout measures 760x648 with no vertical scrollbar at normal scaling. This build has not been live-tested in a driving activity; earlier host results establish the retained keyboard fix.

## Quick check

With the movie available and normally enabled, apply Skip startup movie and launch MSTS: it should go directly to loading. Uncheck it and restart: native movie behavior should return. When playback works on the installation, leave keyboard recovery enabled and check controls after both finishing and skipping the clip.
