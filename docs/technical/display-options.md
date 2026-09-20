# Display guidance and refresh-rate cap

## Resolution guidance

The experimental in-game resolution-selection alert has been removed. NEMT no longer intercepts the resolution dropdown or repurposes the keyboard-assignment dialog. Earlier synthetic tests did not establish successful native rendering; historical implementation details remain in Git history.

The native form checks the selected borderless monitor (or primary monitor when
borderless is off) after executable detection and display selection. The strict
threshold is width > 2048 OR height > 2048, in pixels. Combined desktop width
does not determine a game's render-target dimensions. A recognized external
widescreen DLL suppresses the suggestion; unknown local D3DIM700/ddraw files
are reported as unverified external graphics components. The warning repeats
only when the last warned executable/display configuration changes.

`[Startup] HighResolutionCompatibility=true` enables the integrated MIT-0-derived
fix; missing settings default off. Use Recommended selects it for a display
above the threshold when no external graphics file is present. Apply and restart
MSTS to activate it. Selecting the checkbox is not evidence of runtime success.

The main-game bootstrap, outside DllMain, loads the system x86 D3DIM700.dll by
absolute path and retains its reference. Local D3DIM700.dll/ddraw.dll or a
non-system loaded module of either name causes NEMT to stand down; this does
not certify an external wrapper's compatibility. Editors are excluded.

Executable PE sections are inspected for the upstream `mov eax,2048` signature
followed by two adjacent stack-local dimension comparisons and unsigned branches
to the same failure block. Every candidate must be recognized; ambiguous,
malformed, or inaccessible layouts are rejected. At most eight sites are
accepted. Original instructions are rechecked and changed through NEMT's shared
thread-aware mutation transaction. Recognized `mov eax,-1` pairs are left alone.
The host system DLL has two original sites, both handled by this adaptation.
Neither train.exe nor system files are edited on disk. An unsupported enabled
fix gives a normal Win32 startup notice, with detailed state in optional deep
logging under `HIGH RESOLUTION`.

Native tests cover both paired instruction layouts, repeated/mixed patch state,
ambiguous signatures, invalid PE inputs, memory protection preservation,
external-file stand-down, saved settings, threshold boundaries and disconnected
display fallback. A separate `high-resolution-test.exe --host-probe` successfully
applied the fix inside a disposable process on the development host, then
recognized the already-patched state. This does not establish in-game device
creation, cross-OS behavior or laptop results; those remain host checks.

## Limit FPS to vsync

The optional checkbox shares the Unlock FPS row and is enabled when Unlock FPS is checked. Configure `[Startup] LimitToVSync=true` alongside `UnlockFPS=true`, or use `-UnlockFPS -LimitToVSync` with the patcher. Both default off. Restart after changing settings.

This is a refresh-rate frame cap, not a presentation VSync override. It does not guarantee tear-free display; driver/wrapper synchronization still applies. The native frame hook queries the monitor nearest the game window and its current refresh rate, updating approximately once per second. Unknown refresh falls back to 60 Hz. Integer refresh rates from Windows may round fractional rates. Slower rendering does not create catch-up debt.

Pacing uses a high-resolution waitable timer where available, otherwise Sleep. It does not alter global timer resolution, power plans or driver settings. Fallback timer granularity can yield a lower frame rate. Corrected simulation timing includes the wait; the existing pause/calendar decisions remain native. Editors use a separate frame loop and are unaffected.

Tests cover pacing at 60/144/240 Hz, slow frames, disable and timer-query failure; existing native timing regressions still pass. These synthetic checks do not establish tearing behavior, every monitor configuration or long-session stability.

## Deep logging selection

The checkbox reads `Enable deep logging (Optional; HIGH DISK USAGE! Use only for bug reporting or troubleshooting issues)`. Use Recommended enables the available feature checkboxes and explicitly turns deep logging off, including when it was previously enabled. The form reserves extra height for the longer label. UI checks cover the FPS row, logging reset and footer padding.

The form places Prefer P-cores first and deep logging after Extended F5 HUD Location for Crawling statistics. Its heading includes Patcher and the version. Content height is calculated with monitor bounds and a scroll fallback; the complete layout was visually checked without scrolling on the test display. The user reports approximately 222 FPS on a 240 Hz display and 56 FPS at 60 Hz with the cap, accepted for now. These observations do not establish exact synchronization or a particular cause of the undershoot.
