# Startup/activity loading details and FPS option

Open **NEMT.exe**, select `train.exe`, choose the options and Apply with MSTS closed:

- **Show verbose startup and activity loading details** replaces the native loading-screen text with the latest observed file or directory scan. Long paths show their trailing portion to fit the existing text area.
- **Enable deep logging** records file-open and directory-search attempts and their results in `NEMT/startup.log`. It is off by default and works independently of the display option.
- **Unlock FPS limit (-noclamp + corrected internal timing) (Unstable!)** adds MSTS's existing `-noclamp` option and enables experimental high-resolution timing in `1.1.0-alpha.2`. Shortcuts need no edits. Existing resolution/window arguments are preserved, and an existing `-noclamp` token is not duplicated. Disabling the option also disables timing correction, but does not remove a parameter explicitly supplied on the command line. See the [timing comparison guide](../investigations/timing-host-test.md).

```ini
[Startup]
VerboseLoading=true
WriteLog=false
UnlockFPS=false
MaxLogSizeKB=8192
MaxBackupLogs=0
```

Restart MSTS after changing settings. Missing flags default off. The initial splash image is unchanged. The display updates when MSTS redraws its native loading screen; it is not an independently animated monitor, and it may hold its last message while a long operation runs. The first version reports actual file API activity rather than inventing names for untraced parsing or registry operations. It does not report file reads made privately inside other DLLs.

Initial file/display tracking stops at the first main event-loop boundary, but an enabled deep-log handle remains open. Activity loading reactivates file tracking independently of verbose display, records BEGIN/COMPLETE/FAILED boundaries and retains the same log and sequence. Optional API and exception diagnostics remain available after loading. With zero backups, each launch starts fresh; size rotation and configured retention still apply. Each record uses synchronous WriteFile followed by FlushFileBuffers. Failure disables further file logging without stopping MSTS. See [deep logging implementation and crash limits](deep-logging.md).

## Reading a log

Each line starts with local time `YYYY-MM-DD HH-mm-ss.mmm`, followed by an operation, sequence number, thread ID and path/result. Timed initialization API results also include monotonic elapsed milliseconds. `OPEN` and `SCAN` appear before the corresponding API call; `OPENED` or `FAILED` follows it. Results include the operation number, so overlapping calls can be correlated. A failure includes the Windows error number. Missing optional files and unsuccessful searches are often normal. A successfully opened file is not proof that its contents parsed successfully, and the last listed file is not proof of a crash cause.

`DISPLAY UPDATES` counts native text substitutions, and `STARTUP COMPLETE` marks the end of tracking. Paths use the game's Windows ANSI encoding and can include installation paths. This is a loading trace, not a crash dump or stack trace. Crashes before NEMT's early initialization cannot be recorded.

## Implementation and findings

The localized `Loading...` string is resource 308 in `string.dll`. The initial `Exec Splash Window` at `0x7066b0` is a different display; its Windows text draw was investigated but left unchanged. The native progress renderer at `0x44cace` looks up text at calls `0x44cceb` and `0x44cd0d`, then draws it through the game's font object. Those two lookups substitute one line while tracking is active. Normal localized lookup resumes outside loading. This preserves the existing graphics backend, font and placement.

The game's `CreateFileA` and `FindFirstFileA` imports at `0x84db34` and `0x84dc98` are chained to record activity, preserving the original arguments, handle and `GetLastError` result. Tracking uses bounded buffers and a critical section; it never recursively invokes the renderer from a file operation. The first event-loop frame call at `0x6ba175` closes tracking and forwards to `0x6ad020`. Thirteen checked raw mutations use the existing transaction/claim mechanism; no executable gateway allocation is needed for these changes.

The early command-line stage also runs when no video-mode argument was supplied. It retains exact image-header and normalized whole-image validation and the compatibility-import chaining fix. Configuration and file I/O run outside `DllMain`. The optional `-noclamp` addition uses the game's parser. Starting with alpha.2, the FPS option also installs four checked timing instruction changes in memory; executable files remain unchanged. See the [historical FPS investigation](../miscellaneous/fps.md).

## Validation

Historical startup-only VM smoke-test DLL SHA-256: `5b9cef7975fa389c95639ac6857089d3d8d63395afc982e3c83d063fe3780d6c` (38,400 bytes). Normal `train.exe -vm:w` launch, no Frida. The recorded run reached the menu, counted 18 text substitutions and 346 file/directory operations, and closed the log at the first event-loop frame. The main menu was visually inspected and MSTS exited normally. These counts describe this installation and run, not a benchmark or universal startup sequence. The fast loading-screen text itself was not captured visually; subsequent host testing confirmed the startup text was visible and working.

Automated tests cover argument preservation and `-noclamp` deduplication, compatibility redirect chaining, native window sizing, startup API result/error preservation, bounded text, post-startup bypass, and 60 startup/HUD installer combinations across four executable variants. Original call-site bytes are checked against the supplied base/widescreen fixtures. Existing native physics, lifecycle and mutation tests remain separate regressions. No game binaries or raw research exports ship in the package.

## Host checklist

1. Enable verbose loading and the diagnostic log, then launch normally. Check that the before-menu loading text is readable and changes as loading advances.
2. At the main menu, confirm `startup.log` ends with `STARTUP COMPLETE`. Enter an activity and check its size/modified time stays unchanged.
3. Disable the log and restart. Confirm the previous file stays unchanged while verbose text still works.
4. Enable the FPS option and launch without manually adding `-noclamp`. Compare with the known explicit-parameter behavior; rendering/CPU limits can still constrain FPS.
5. Retest the borderless checkbox with `-vm:w`, a custom resolution and Alt+Tab. The prior host-validated borderless checkpoint remains available as `nemt-borderless-host-tested`.

## Terrain-buffer progress and remaining time

During actual generation, the single line reads for example `Generating terrain buffers 58/232 25%: ~10m 00s remaining`. Before enough progress is available it says `estimating...`. The estimate is elapsed time multiplied by remaining percentage divided by completed percentage. It is an estimate, not a deadline: individual buffers can take different amounts of time.

MSTS supplies integer percentages; no sub-percent precision is claimed. Updates arrive after completed buffer jobs when MSTS redraws. The message may remain stationary during a slow job. No separate animation or timer redraw is injected. Existing loading text is replaced, not stacked into a second line.

The generator at `0x56685f` counts missing jobs, increments the completed count after generating a buffer, and passes floor(completed × 100 / total) to the progress renderer. Checked calls `0x566cc2` and `0x566d21` wrap progress initialization and updates respectively, forwarding to `0x4023e2`. Resource 53 identifies generation; resources 58 and 59 identify the preceding checks/collation. Activity tracking wraps creation at `0x490e1d`, failure cleanup at `0x49105d` and first-frame cleanup at `0x4900e7`. Failed loading-window creation also clears tracking.

Automated tests cover initial/partial/completed estimates, insufficient samples, repeated activity loads and failed creation. VM smoke build `f66e0b23e31ab945421980fe87ea38ad49ebfc5560eec48310458567ab60c8af` displayed a single file-detail line while loading Megacoaster and reached the driving scene. The startup log stayed closed and unchanged during activity loading. No real missing-buffer generation was measured in that run; the subsequent LGVMED trial below was blocked before generation. Synthetic estimate tests are not a substitute for that route test.

For a repeatable route test, inventory the untouched route before its first load, record the post-load differences, and preserve any original files. Only newly generated terrain buffers verified by this comparison should be removed for a repeat. Keep route files and inventories local, outside release archives.

## LGVMED trial, 12 September 2026

Final DLL `6e257dc1f58bba74175acfe5b46fc520fb05754ad4c2379aa8c1adf8b41d09b0` (44,544 bytes) was tested with a fresh installed LGVMed 3.0 copy. The original route was inventoried by relative path, size and SHA-256 before launch, and preserved separately. Startup crashed before reaching the menu or terrain generation. A second normal windowed launch with NEMT's DLL temporarily removed crashed at the same `train.exe` offset `0x002f4c5a`, exception `0xc0000005`. This reproduces the failure without NEMT, but does not identify its underlying cause.

The logged run had progressed beyond LGVMed's paths before its last observed open, `routes/USA2/Marias.tdb`. That last file is not proof of fault. Post-run comparison found zero added, removed or content-modified route files, so no generated buffers required rollback. NEMT was restored and the test route copy moved out of active Routes into local scratch; the original route copy was untouched. Live terrain-percentage/ETA verification remains blocked by this independent startup failure. Inventories, crash events and logs remain local under work/ and are excluded from the release.

After moving the LGVMED test copy out, the final build reached the main menu normally: 346 observed operations, 18 text substitutions, and a closed startup log. The menu was visually inspected and MSTS exited normally.

## Host follow-up

Host testing confirmed successful terrain generation, with a screenshot recording 46.0% and an estimated five seconds remaining. Installing Xtracks to satisfy LGVMed’s documented 3.10 requirement resolved the host startup crash. The supplied VM comparison package is Xtracks Standard Edition 3.22. These host reports supersede the earlier blocked terrain test, without turning the earlier VM failure into a successful measurement.

## Generation counts and the following pause

The generation line now includes completed/total jobs: `Generating terrain buffers 56/232 24%: ~0m 08s remaining`. These are per-tile generation jobs, not individual output files. LGVMed’s 232 jobs generate 464 `_e.raw`/`_n.raw` files. Percentage remains the native integer result; the decimal `.0` was removed to keep the line compact.

Two checked argument-load instructions now supply exact counts to the existing wrappers: `0x566cbd` reads total jobs from `[EBP-0x24]`, and `0x566d1c` reads completed jobs from `[EBP-0x4]`. Both originally loaded resource 53; the wrappers restore that resource when forwarding to the original renderer. The pair is installed atomically with the existing progress-call redirects. No guessed total is derived from a rounded percentage.

The code immediately following generation selects the environment file (`0x4935af`) and initializes route/activity assets. No distinct post-generation terrain-validation loop with a measurable total was identified. The new checked call redirect at `0x494bc1` displays `Preparing route assets...`, clears generation mode and forwards to the original environment selection routine. It intentionally does not invent a validation count, percentage or ETA. Later native redraws continue to show observed file activity.

VM build `4a0d061070a7af6c14b241604dba85d77038c8ff0e8c0bf1fbd1d0c973e5d34d` showed 56/232 jobs, 24% and approximately eight seconds remaining at 640×480, then entered LGVMed successfully. Only the 464 previously inventoried generated files were moved aside for this repeat, after checking every hash and path; original route files were preserved. The brief transition message was not captured visually in that run; its forwarding and generation-state reset have automated coverage. These observations do not imply every post-generation delay has been identified.

## Log rotation in 1.0.0

`[Startup] MaxLogSizeKB` accepts 4–65536 (default 8192). `MaxBackupLogs` accepts 0–20 (default 0). Invalid values reject configuration. With backups enabled, each new launch archives the prior log; reaching the size limit during startup also rotates before the next record. Files are `startup.log`, `startup.1.log` (newest backup), and so on. Zero backups discards the previous content on launch/size rollover. Recording continues after a size rotation.

Changing the backup count prunes the recognized numbered backups above that count when logging next starts. Previously recorded backups may reflect an earlier, larger size limit until replaced. Logging disabled leaves existing logs untouched. Rotation failures disable further logging without stopping the simulator. There are no periodic per-frame log writes; activity loading uses the retained log handle.
