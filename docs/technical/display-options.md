# Display guidance and refresh-rate cap

## Resolution guidance

The experimental in-game resolution-selection alert has been removed. NEMT no longer intercepts the resolution dropdown or repurposes the keyboard-assignment dialog. Earlier synthetic tests did not establish successful native rendering; historical implementation details remain in Git history.

This development branch replaces that behavior with frontend display selection and optional high-resolution compatibility. Implementation and validation details will be recorded here as those checkpoints are completed.

## Limit FPS to vsync

The optional checkbox shares the Unlock FPS row and is enabled when Unlock FPS is checked. Configure `[Startup] LimitToVSync=true` alongside `UnlockFPS=true`, or use `-UnlockFPS -LimitToVSync` with the patcher. Both default off. Restart after changing settings.

This is a refresh-rate frame cap, not a presentation VSync override. It does not guarantee tear-free display; driver/wrapper synchronization still applies. The native frame hook queries the monitor nearest the game window and its current refresh rate, updating approximately once per second. Unknown refresh falls back to 60 Hz. Integer refresh rates from Windows may round fractional rates. Slower rendering does not create catch-up debt.

Pacing uses a high-resolution waitable timer where available, otherwise Sleep. It does not alter global timer resolution, power plans or driver settings. Fallback timer granularity can yield a lower frame rate. Corrected simulation timing includes the wait; the existing pause/calendar decisions remain native. Editors use a separate frame loop and are unaffected.

Tests cover pacing at 60/144/240 Hz, slow frames, disable and timer-query failure; existing native timing regressions still pass. These synthetic checks do not establish tearing behavior, every monitor configuration or long-session stability.

## Deep logging selection

The checkbox reads `Enable deep logging (Optional; HIGH DISK USAGE! Use only for bug reporting or troubleshooting issues)`. Use Recommended enables the available feature checkboxes and explicitly turns deep logging off, including when it was previously enabled. The form reserves extra height for the longer label. UI checks cover the FPS row, logging reset and footer padding.

The form places Prefer P-cores first and deep logging after Extended F5 HUD Location for Crawling statistics. Its heading includes Patcher and the version. Content height is calculated with monitor bounds and a scroll fallback; the complete layout was visually checked without scrolling on the test display. The user reports approximately 222 FPS on a 240 Hz display and 56 FPS at 60 Hz with the cap, accepted for now. These observations do not establish exact synchronization or a particular cause of the undershoot.
