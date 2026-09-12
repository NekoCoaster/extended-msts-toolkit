# Unclamped timing — follow-up investigation

Host testing reports that `-noclamp` speeds up simulation time and makes time acceleration unreliable. No timing correction is enabled in the current alpha. The needle correction received positive host feedback; its five-second delay is inherited from the gameplay readiness gate, not required by its geometry calculation. In-game settings integration has been dropped because of widget-addon compatibility concerns.

## Confirmed static findings

The frame preparation routine at `0x4b7b20`, called by `0x48fdd0`, saves the raw step at `0x80ace0`, then multiplies the simulation step at `0x828fb4` by the time-scale value at `0x80acd8`. In its ordinary branch it compares this result with `time_scale * 0.005`, but assigns the constant `0.005` when the result is below that threshold. The assignment does not retain the multiplier. A corresponding upper comparison uses `time_scale * 0.3` but assigns `0.3`.

The same routine caps the reciprocal-rate value at `0x828f6c` to 200. A separate mode (`0x7be0ec == 2`) has different bounds and must not be changed without understanding its purpose.

For idealized 300 updates per real second, the ordinary branch produces:

| Selected time scale | Incoming step | Step after original lower bound | Accumulated seconds per real second |
|---|---|---|---|
| 1× | 1/300 second | 0.005 second | 1.5 |
| 2× | 1/300 second | 0.005 second | 1.5 |
| 4× | 1/300 second | 0.005 second | 1.5 |

These are predictions from the verified instructions, not new live measurements. They explain both faster-than-real-time behavior and why increasing the selected multiplier can stop having the intended effect. Other timer precision or gameplay issues may also contribute.

## Fix direction and validation

Measure elapsed time independently of rendering throughput, apply the selected multiplier exactly once, and keep the simulation step and reciprocal-rate values consistent. Preserve pause, activity transitions and sensible handling of stalls; do not compensate merely by slowing the displayed clock. Replacing the 200-update bound with another fixed bound only moves the threshold.

The earlier limited VM experiment documented in [FPS research](../miscellaneous/fps.md) restored approximately 1:1 simulation/wall time near 232 updates per second with adjusted bounds. That experiment did not validate accelerated time and is not evidence for a new DLL build.

Before enabling a correction, compare wall time and accumulated simulation steps at normal and accelerated time, below and above 200 updates per second. Include pause/resume, activity restart, frame stalls, moving physics and a longer run. Trace the writer of the time-scale value and the raw-timer source before choosing a final replacement. The visual-only needle feature can be considered for an earlier native startup stage separately; the crawl readiness gate remains intact.
