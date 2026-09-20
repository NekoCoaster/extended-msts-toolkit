# Feature guide

Select options in NEMT.exe, click **Apply**, and restart MSTS. The options are independent except where a dependency is described below.

| Control-panel option | Behavior and notes |
| --- | --- |
| **Skip startup movie (fixes keyboard control issue when loading into simulator)** | Bypasses the clip before playback. The registry and movie file remain unchanged. Unchecked, MSTS follows its normal movie behavior. |
| **Enable borderless windowed mode** | Removes the frame and centers the game window. An explicit fullscreen launch takes precedence. See [window modes](borderless.md). |
| **Display dropdown** | Chooses the borderless game's monitor. Disconnected displays fall back to the primary monitor. |
| **Enable high-resolution support for displays larger than 2048 in width or height** | Removes recognized legacy Direct3D limits in memory. Recommended when the chosen display exceeds 2048 pixels in either dimension. External graphics DLLs take precedence. |
| **Unlock FPS limit — Potentially unstable** | Enables the game's uncapped mode together with timing correction. Higher FPS is not guaranteed. Disable this option if it causes problems; also remove any uncapping argument you added to your own shortcut when returning to normal timing. |
| **Show verbose startup and activity loading details** | Replaces the loading text with observed loading activity. Terrain generation includes completed/total jobs, percentage and an estimated remaining time. |
| **Enable deep logging** | Records optional deep startup/activity and initialization diagnostics. It is independent of the loading-screen text. See [logs](startup.md). |
| **Fix cabview dials for widescreen displays** | Corrects dial-needle proportions. Available only for a supported widescreen executable; use the adjacent installation-guide link if needed. |
| **Unmute while in background** | Keeps game audio active when another application has focus. |
| **Continue after passing a red signal (Resume after failure message)** | Displays the built-in activity-failure message and permits continued simulation after dismissal. This does not turn the failed activity into a successful one or bypass unrelated failure conditions. |
| **Remove derailment activity-end message** | Prevents the derailment activity-end message from ending the session. Other activity-ending conditions remain separate. |
| **Unlock camera modes during derailment** | Keeps camera controls available after derailment. |
| **Allow connected engines to crawl after derailment** | Adds powered movement after derailment. The panel also selects derailment activity-end prevention, which crawling requires. |

The five [editor options](editors.md) enable resizable viewports and Alt+Enter fullscreen, freely movable Route Editor tools, the Route Editor idle-audio fix, configurable camera key swaps, and unrestricted mouse panning. Main-game borderless mode does not apply to `-toolset`.

## Crawling controls

**Use throttle for speed & reverser for direction.** Steam locomotives use the regulator and reverser. Eligible engines contribute according to their individual power and force values.

The strength slider ranges from **0–100×**, initially **10×**. At zero the form shows **Disabled**: added thrust is off, while the other selected crawling effects remain enabled. Higher settings are intended for playful movement, not realistic recovery.

Choose **Bottom left** or **Bottom right** for the crawl HUD. Bottom left is the default. The HUD is included with crawling and appears in MSTS Bin's white extended F5 display. [Crawling guide](crawl-hud.md).

## Use Recommended

The button enables recommended available features, leaves deep logging off,
and recommends high-resolution compatibility for a display above 2048 pixels
when no external graphics DLL is present. It preserves the display choice and
thrust multiplier. You can change individual options before Apply.

## CPU preference

[Prefer P-cores](cpu-preference.md) is an optional restart-only scheduling preference for compatibility testing; it defaults off.
