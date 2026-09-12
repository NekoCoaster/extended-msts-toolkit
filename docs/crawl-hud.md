# Crawl status in the extended F5 HUD

Enable **Show crawl status in extended F5 HUD**, Apply with MSTS closed, then restart. Press F5 through the red pages to reach MSTS Bin's white extended display. Three extra lines show state and multiplier, applied thrust in kN, throttle/regulator and reverser, and applying/connected powered-engine counts. The red pages are unchanged.

Set `ShowCrawlHUD=true` in `[Diagnostics]` for manual configuration. It defaults off, is independent of `WriteStatusJson`, and performs no diagnostic file writes. It can be enabled without crawling, which displays a disabled state. Other states include waiting for activity, armed, ready, active, paused and fault. Added thrust is zero while inactive or paused.

## Implementation

`runtime/hud.h` redirects the checked final CALL at `0x60c996` in the white renderer (`0x60997a`), then forwards to original render-state cleanup at `0x6ae6f0`. It uses font global `0x7b64d4`, height method vtable +0x18 and XY drawing method +0x34. Three lines sit near the bottom, starting at one quarter of screen width plus eight pixels to avoid the standard left-side track monitor. User-moved overlays can still overlap them.

The hook snapshots data under the existing crawl lock only after initialization. No polling thread is added. Applied thrust sums the magnitudes of added engine momentum divided by the applied timestep. It is added crawl force, not gravity, collision force or net train force; opposing vectors are not cancelled. Propulsion equations and their timestep cap are unchanged. Activity exit clears membership and eligibility.

## Validation

Automated tests cover disabled/waiting/active/paused/fault states, controls, powered membership, force conversion, activity exit, three-line placement at 640×480, hidden-HUD bypass and render-cleanup forwarding.

VM smoke build `f66e0b23e31ab945421980fe87ea38ad49ebfc5560eec48310458567ab60c8af` showed the armed state with two connected KIHA31 engines on white F5, and no additions on red F5. The final build shifts these lines right to avoid the track monitor; that coordinate adjustment has automated coverage but was not part of this live measurement. Active-force and fault examples were synthetic tests, not a newly measured live derailment run.

Host checks: inspect white F5 while crawling, pause/resume, end the activity and enter another. Check placement at your usual resolution with your other overlays.
