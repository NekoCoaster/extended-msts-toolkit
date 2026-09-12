# Timing comparison — 1.1.0-alpha.2 (unstable)

This is a development build. The high-FPS timing correction has passed automated tests with synthetic frame times, including execution of its actual x86 clock adapters. Live simulator behavior has not yet been validated. Stable 1.0.2 is unchanged.

## Install

Close MSTS, pull `codex/settings-cab-investigation`, and run `NEMT.vbs`. Confirm the title shows `1.1.0-alpha.2`. Check **Unlock FPS limit (-noclamp + corrected internal timing) (Unstable!)**, retain the other desired options, and Apply. Launch normally; adding `-noclamp` manually is unnecessary.

The existing `[Startup] UnlockFPS=true` setting now enables both the parameter and timing correction. An explicit `-noclamp` without this checkbox retains MSTS's original timing behavior. There is no five-second wait for the timing feature: its checked call sites are installed during the existing command-line startup stage outside the loader lock. No Frida is used.

## Checks

1. Use the same simple activity at high FPS, ideally above 200. At normal time, compare the activity clock against a stopwatch for 60 real seconds: it should advance about 60 simulation seconds. Avoid loading, pausing or changing settings during that interval.
2. Repeat at the available time-acceleration settings, then return to normal time. For example, a selected 2× rate should advance about 120 simulation seconds in 60 real seconds. Note the rate actually selected and the observed clock advance.
3. Pause for 15 seconds. The activity clock should stop; resuming should not jump forward to catch up. Also test Alt-Tab and returning to the game.
4. End the activity, start another, and repeat a shorter normal-time comparison. Check a moving train, braking, AI traffic and the derailment/crawl features.
5. If these pass, compare below 200 FPS and run for several minutes to check for drift. Report FPS, selected time rate, stopwatch duration and simulator clock advance, plus any unusual motion or audio.

Large stalls are deliberately limited to a 0.3-second wall-time step instead of being replayed in one physics update. Therefore time can fall behind during loading or prolonged stalls; the test target is correct timing during continuous running. High time multipliers can still stress MSTS physics and remain experimental.

## Disable

Close MSTS, uncheck the FPS option and Apply. Also remove any manually supplied `-noclamp` from the shortcut if returning to the original capped behavior. This disables both automatic parameter insertion and the new timing hooks. Cab correction remains independent.

If checked instruction sites do not match, the runtime displays a timing-unavailable message and does not automatically add `-noclamp`. A manually supplied parameter cannot be withdrawn from the original shortcut; the message asks for its removal.

## What changed

The accepted-frame wrapper obtains elapsed time from Windows' high-resolution counter using integer tick differences. The simulation preparation wrapper applies MSTS's current time multiplier once, without the old 0.005-second floor or 200-rate ceiling. Native frame counters, rendering statistics, special-mode handling, pause decisions and calendar rollover remain in place.

Two clock additions retain fractional rounding remainders between frames, avoiding repeated loss of small increments in the native single-precision clock fields. They rebase when MSTS changes those fields, such as on a new activity or clock wrap. Other clock objects retain their original addition behavior. The feature adds no per-frame disk writes.
