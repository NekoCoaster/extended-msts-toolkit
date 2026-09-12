# Alpha.3 host checks

Close MSTS, pull `codex/settings-cab-investigation`, open `NEMT.vbs` and confirm **1.1.0-alpha.3** in the title. Reapply the desired options before launching normally. These changes do not modify train.exe. Stable 1.0.2 remains unchanged.

## Red signals

Enable **Continue after passing a red signal (show failure message)**. Load **Northeast Corridor → Train Rescue** and run the initial red before the oncoming train passes.

1. Expect MSTS's own ALERT/OK popup containing **Activity failed -- ignored red light.**, with driving paused while it is open. There should be no Windows message box.
2. Dismiss OK. Driving should resume, and the same signal should not repeatedly open the alert while it remains in the monitored area.
3. If practical, pass another red signal: it should still warn. End/restart the activity and repeat the first violation to check that remembered signals reset.
4. Note any missing text, unexpected pause, repeated notice or activity exit. Widget addons may change the native popup controls and need separate testing.

The earlier bypass already passed an initial host continuation test. This revised native popup and repeat suppression have automated coverage but are awaiting these in-game checks. See [implementation details](red-signal-repeat.md).

## Background audio

Enable **Unmute while in background**. With engine sound audible, switch to another application without manually pausing MSTS. Sound should continue. Switch back and verify normal controls. Uncheck/reapply/restart for a comparison. Native activity pause and other explicit muting behavior are not disabled.

The change adds DirectSound's GLOBALFOCUS flag to secondary sound buffers, preserving their existing flags. It adds no audio-processing loop. Microsoft documents the background behavior and its primary-buffer priority exception in the [DSBUFFERDESC reference](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ee416818(v=vs.85)). Instruction-site tests verify the flag change; audible host validation remains pending.

## Cab and timing

**Fix cabview dials for widescreen displays** is disabled for a non-widescreen executable. Use the adjacent [widescreen installation guide](https://digital-rails.com/wordpress/2018/06/23/running-msts-at-high-resolution/) first, then select the patched executable again. Test a 16:9 cab after five seconds of unpaused driving; the existing gameplay readiness gate remains in place. Previous host testing found that the needles looked better.

The FPS label now says **Potentially unstable**. Timing code is unchanged from alpha.2: two host runs confirmed time acceleration, with only preliminary evidence for more reliable 16× activity messages. Follow the [timing comparison](timing-host-test.md) for longer checks.
