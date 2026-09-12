# Historical frame-rate investigation

For the shipped option, see the [feature guide](../features.md). The observations below retain their original development context.

The NEMT form can now add the existing parameter automatically through **Unlock FPS limit**. See the [startup options](../technical/startup.md). The experimental limiter patches below remain historical.

## Recommended first step: use `-noclamp`

Follow-up: host testing reports accelerated simulation time and unreliable time acceleration with this option. `-noclamp` alone should not be treated as a fully validated high-FPS solution. Alpha.2 adds an experimental timing correction through the FPS checkbox; [host timing validation](../investigations/timing-host-test.md) remains pending. The historical minimum-step finding below is relevant, but is not validation of this new build.

MSTS already has a `-noclamp` launch parameter that disables the game-side frame limiter identified in this investigation. Host testing established the desired higher-frame-rate behavior, with performance still constrained by CPU throughput. For that goal, **prefer this existing option over reverse engineering or patching the executable**.

For a windowed launch from the MSTS installation directory, use:

```powershell
.\train.exe -vm:w -noclamp
```

Alternatively, append `-noclamp` after the executable path in an existing shortcut's Target field. This removes the identified game-side restriction; it does not guarantee 300 FPS or remove other rendering, synchronization, or hardware limits. This host test was not a controlled benchmark or comprehensive high-frame-rate physics validation.

## Historical reverse-engineering experiments

The measurements below document exploratory work performed before the host test established that `-noclamp` was sufficient. These experimental patches are not required or recommended to obtain that result.

The roughly 57 FPS observation was traced to a nominal 60 FPS game-side limiter, not conclusively to VM throughput. The limiter at `0x6AD0F0` compares a single-precision absolute timer difference against a minimum interval. At the observed timer magnitude its quantization turns the nominal 1/60-second limit into approximately 17.578 ms, or 56.89 FPS.

| Experiment | Median updates/s | Simulation time / wall time |
|---|---:|---:|
| Original nominal 60 cap | 56.94 | 1.000 |
| Nominal 120 cap | 113.81 | 1.000 |
| Nominal 200 cap | 170.47 | 1.000 |
| Nominal 300, original timestep clamps | 229.70 | 1.167 |
| Nominal 300, corrected timestep clamps | 231.68 | 1.000 |

At high rates, the original minimum 0.005-second simulation step could advance the game too quickly. The corrected experiment changed both step and reciprocal-rate limits consistently; it did not demonstrate sustained 300 FPS. The scene was a stationary single HHP-8 with low geometry and a software-rendering wrapper in the VM. These are instrumentation measurements, not general hardware benchmark claims.

The limiter enable global was `0x829900`, the interval `0x829904`, and the startup interval immediate at file offset `0x2BA004`. The parser's `noclamp` option cleared the enable flag. Later host testing confirmed that `-noclamp` met the desired host-machine behavior and closed this investigation.

No permanent FPS or timestep patch is installed by MSTS Derailment. Moving collisions, AI, accelerated simulation and long-running timer precision were not comprehensively tested at high frame rates. All exploratory changes were restored after measurement.
