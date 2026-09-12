# Startup loading details and FPS option

Open **NEMT.vbs**, select `train.exe`, choose the options and Apply with MSTS closed:

- **Show verbose startup loading details** replaces the native loading-screen text with the latest observed file or directory scan. Long paths show their trailing portion to fit the existing text area.
- **Write startup diagnostic log** records file-open and directory-search attempts and their results in `NEMT/startup.log`. It is off by default and works independently of the display option.
- **Unlock FPS limit (forces -noclamp launch parameter)** adds MSTS's existing `-noclamp` option to its private startup command line. Shortcuts need no edits. Existing resolution/window arguments are preserved, and an existing `-noclamp` token is not duplicated. Disabling the option does not remove a parameter explicitly supplied by the user.

```ini
[Startup]
VerboseLoading=true
WriteLog=false
UnlockFPS=false
```

Restart MSTS after changing settings. Missing flags default off. The initial splash image is unchanged. The display updates when MSTS redraws its native loading screen; it is not an independently animated monitor, and it may hold its last message while a long operation runs. The first version reports actual file API activity rather than inventing names for untraced parsing or registry operations. It does not report file reads made privately inside other DLLs.

The tracker stops when the application reaches its first main event-loop frame. Later activity loading and gameplay do not generate startup records or substitute loading text. An enabled log is replaced on each fresh launch, capped at 8 MiB, and closed at startup completion. Disabling logging leaves an existing log untouched. The installer does not create this optional fourth file; Uninstall retains it as a diagnostic record. Regular OS writes are used, without per-record flush-to-disk calls. Logging has some startup I/O cost, and the last record is not guaranteed to survive a machine/power failure.

## Reading a log

Each line contains elapsed milliseconds, an operation type, a sequence number and a path or result. `OPEN` and `SCAN` appear before the corresponding API call; `OPENED` or `FAILED` follows it. Results include the operation number, so overlapping calls can be correlated. A failure includes the Windows error number. Missing optional files and unsuccessful searches are often normal. A successfully opened file is not proof that its contents parsed successfully, and the last listed file is not proof of a crash cause.

`DISPLAY UPDATES` counts native text substitutions, and `STARTUP COMPLETE` marks the end of tracking. Paths use the game's Windows ANSI encoding and can include installation paths. This is a loading trace, not a crash dump or stack trace. Crashes before NEMT's early initialization cannot be recorded.

## Implementation and findings

The localized `Loading...` string is resource 308 in `string.dll`. The initial `Exec Splash Window` at `0x7066b0` is a different display; its Windows text draw was investigated but left unchanged. The native progress renderer at `0x44cace` looks up text at calls `0x44cceb` and `0x44cd0d`, then draws it through the game's font object. Only those two calls are redirected. Normal localized lookup resumes after startup. This preserves the existing graphics backend, font and placement.

The game's `CreateFileA` and `FindFirstFileA` imports at `0x84db34` and `0x84dc98` are chained to record activity, preserving the original arguments, handle and `GetLastError` result. Tracking uses bounded buffers and a critical section; it never recursively invokes the renderer from a file operation. The first event-loop frame call at `0x6ba175` closes tracking and forwards to `0x6ad020`. Five checked raw mutations use the existing transaction/claim mechanism; no executable gateway allocation is needed for these changes.

The early command-line stage now also runs when no video-mode argument was supplied. It retains exact image-header and normalized whole-image validation and the compatibility-import chaining fix. Configuration and file I/O run outside `DllMain`. The optional `-noclamp` addition uses the game's parser; limiter instructions and timing equations are not patched. See the [historical FPS investigation](miscellaneous/fps.md).

## Validation

VM smoke-test DLL SHA-256: `5b9cef7975fa389c95639ac6857089d3d8d63395afc982e3c83d063fe3780d6c` (38,400 bytes). Normal `train.exe -vm:w` launch, no Frida. The recorded run reached the menu, counted 18 text substitutions and 346 file/directory operations, and closed the log at the first event-loop frame. The main menu was visually inspected and MSTS exited normally. These counts describe this installation and run, not a benchmark or universal startup sequence. The fast loading-screen text itself was not captured visually; host readability validation remains pending.

Automated tests cover argument preservation and `-noclamp` deduplication, compatibility redirect chaining, native window sizing, startup API result/error preservation, bounded text, post-startup bypass, and 28 installer combinations across four executable variants. Original call-site bytes are checked against the supplied base/widescreen fixtures. Existing native physics, lifecycle and mutation tests remain separate regressions. No game binaries or raw research exports ship in the package.

## Host checklist

1. Enable verbose loading and the diagnostic log, then launch normally. Check that the before-menu loading text is readable and changes as loading advances.
2. At the main menu, confirm `startup.log` ends with `STARTUP COMPLETE`. Enter an activity and check its size/modified time stays unchanged.
3. Disable the log and restart. Confirm the previous file stays unchanged while verbose text still works.
4. Enable the FPS option and launch without manually adding `-noclamp`. Compare with the known explicit-parameter behavior; rendering/CPU limits can still constrain FPS.
5. Retest `-vm:bw`, a custom resolution and Alt+Tab. The prior host-validated borderless checkpoint remains available as `nemt-borderless-host-tested`.
