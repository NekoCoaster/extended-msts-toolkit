# World-relative crawl pitching

Unreleased fix, 2026-09-13. The installed MSTS folder was inspected read-only. Its NEMT manifest identifies `1.1.0-alpha.7`, while the source checkout identifies `1.1.0-alpha.9`; the fix is based on the source checkout. This is fresh automated validation, not a live gameplay measurement.

## Cause and correction

The previous `calc_pitch` projected world angular velocity onto body right at `+0x0C`. For a locomotive facing world Z and rolled onto its side, right becomes world Y: the filter then removes turning about vertical instead of pitching about world X. For example, at full throttle, angular velocity `(2, 3, 4)` became `(2, 0, 4)` instead of `(0, 3, 4)`.

The callback now supplies body forward at `+0x24`. The filter derives a horizontal pitch axis from world up crossed with forward. It leaves the world-vertical and longitudinal components intact at every roll angle. Reversing the forward vector leaves the projection unchanged. Near a vertical forward vector, suppression fades continuously to zero rather than selecting an unstable heading. The [physics reference](../technical/physics.md) gives the equation and threshold.

The existing callback eligibility, paused/disabled gates, nested derivative isolation and two helper call-site restrictions remain in place. The changed calculation uses the callback's body buffer, not a cached address. It changes only the scratch angular velocity supplied to the orientation derivative. No new hooks, configuration flags or executable patches are introduced.

## Automated coverage

- `tests/pitch.c`: 4,488 heading/slope/throttle combinations verify pitch attenuation using the independent nose-height derivative `(omega cross forward).y`, world-yaw and longitudinal-roll preservation, non-increasing angular speed, forward-sign invariance and tolerance of matrix normalization drift. Another 1,616 cases cover the transition to both vertical poles. Invalid vectors, non-finite values and invalid scales are rejected.
- `tests/lifecycle.c`: 576 heading/roll/slope/throttle combinations run through the real runtime callbacks and both derivative helper branches. These cover upright, either side, inverted and intermediate roll angles, swapped integration buffers, nested on-rail exclusion, unrelated callers, pause/off gates, balanced return contexts, and byte-for-byte preservation of the body state.
- Existing native math and x86 gateway checks pass, including 60,000 calls covering stack cleanup, integer/x87 returns and inactive/paused bypasses. Existing connection, steam-control, wheel/rod restoration and transaction checks also pass.
- All 11 feature-configuration fixtures pass. A local comparison compiled the original formula from the checkout's parent revision and reproduced the sideways `(2, 0, 4)` result alongside the corrected `(0, 3, 4)` result.
- Read-only checks confirm all 11 crawl entry signatures match the installed MSTS executable. The complete loader is byte-identical to the checkout's starting revision, preserving the existing stable-scene, owner-backlink and advancing-clock readiness gate before gameplay installation. This is a source-preservation check, not a new live startup test.

The rebuilt x86 DLL SHA-256 is `892a73dbbe490366dea182c640ad1809384e74a62b161791c06216bf2de3c168`. DirectInput export validation and package CRC, byte-equality and integrity checks pass. The installed DLL and `train.exe` retain their original hashes; this development package has not been installed or published.

## Repeat locally

From the NEMT source directory, with an x86 TCC path, put test executables in ignored `work/`:

```powershell
New-Item -ItemType Directory -Force work/world-pitch
& $tcc -o work/world-pitch/pitch.exe tests/pitch.c
& ./work/world-pitch/pitch.exe
& $tcc -o work/world-pitch/lifecycle.exe tests/lifecycle.c -ladvapi32 -luser32
& ./work/world-pitch/lifecycle.exe
python runtime/build.py $tcc
python tools/package.py
```

A live follow-up should compare closed/half/full throttle while derailed upright, on both sides and inverted, then repeat facing a different heading and in reverse. Check that nose-up/nose-down motion is reduced while turning remains possible. Nearly vertical wrecks should retain native rotation as the correction fades. Launch normally with `train.exe -vm:w` and allow the scene to finish loading before any instrumentation. No live verification of this new build has been recorded yet.
