# Crawl status in the extended F5 HUD

Enable **Allow connected engines to crawl after derailment**, Apply with MSTS closed, then restart. The form includes the HUD automatically; there is no separate HUD checkbox. Press F5 through the red pages to reach MSTS Bin's white extended display. Four extra lines show state and multiplier, applied thrust in kN, throttle/regulator and reverser, applying/connected powered-engine counts, mapped control keys, rotational input and the manual-derail shortcut. The red pages are unchanged.

Set `ShowCrawlHUD=true` in `[Diagnostics]` for manual configuration. The installer enables it with crawling; manual configurations may still disable it. It is independent of `WriteStatusJson`, and performs no diagnostic file writes. It can be enabled without crawling, which displays Standby. Standby also covers waiting, paused and faulted states; only eligible unpaused crawl displays Active. Added thrust is zero while inactive or paused.

## Implementation

`runtime/hud.h` redirects the checked final CALL at `0x60c996` in the white renderer (`0x60997a`), then forwards to original render-state cleanup at `0x6ae6f0`. It uses font global `0x7b64d4`, height method vtable +0x18 and XY drawing method +0x34. Four lines sit near the bottom with an eight-pixel margin. Choose Bottom left (default) or Bottom right in the form when crawling is enabled. Left placement can overlap MSTS’s track monitor; move or hide that monitor as needed. Top placement is not offered because MSTS Bin already uses that area. Right-aligned lines are measured using the native font width method (vtable +0x24), so alignment follows resolution and text length. User-moved overlays can still overlap them.

The hook snapshots data under the existing crawl lock only after initialization. No polling thread is added. Applied thrust sums the magnitudes of added engine momentum divided by the applied timestep. It is added crawl force, not gravity, collision force or net train force; opposing vectors are not cancelled. The reverser supplies the displayed sign: reverse is negative, forward is positive; inactive zero remains unsigned. Propulsion equations and their timestep cap are unchanged. Activity exit clears membership and eligibility.

## Validation

Automated tests cover disabled/waiting/active/paused/fault states, controls, powered membership, force conversion, activity exit, four-line placement at 640×480 and 1920×1080, hidden-HUD bypass and render-cleanup forwarding.

VM smoke build `f66e0b23e31ab945421980fe87ea38ad49ebfc5560eec48310458567ab60c8af` showed the armed state with two connected KIHA31 engines on white F5, and no additions on red F5. That historical build used an earlier placement. Active-force and fault examples were synthetic tests, not a newly measured live derailment run.

Host checks: inspect white F5 while crawling, pause/resume, end the activity and enter another. Check placement at your usual resolution with your other overlays.

Host testing confirmed the earlier white F5 display on the host. The latest right alignment and signed-force changes have automated coverage and still need host visual confirmation.

VM build `9d06d47e3cc9a76fd68c996bab844ff6c1cd6a19d21633faec6d291ee356ca66` was subsequently verified in LGVMed at 640×480: all three lines end at the bottom-right margin, including the paused state. The native font width call executed successfully. Signed nonzero force is covered by synthetic tests; this live run remained on rails.

Manual setting: `[Diagnostics] CrawlHUDAnchor=BottomRight` or `BottomLeft`. Missing values default left; unsupported values invalidate configuration. The installer preserves the saved choice when its internal option is omitted. Restart MSTS after changing it. Tests cover both anchors and two resolutions.

VM build `4a0d061070a7af6c14b241604dba85d77038c8ff0e8c0bf1fbd1d0c973e5d34d` displayed the selected bottom-left anchor in LGVMed. Closing the overlapping track monitor exposed all three lines at the left/bottom margin. Bottom-left is now the default for installations without a saved choice; saved right-hand placement is preserved.

## Shortcut display (alpha.15)

Alpha.15 reserved six lines using `HUD_LINE_COUNT`, retaining the existing bottom-left/bottom-right placement. Its last three lines showed current bound rotation keys, eligible rotation input, and the backslash manual-derail shortcut. The bound keys and input mask are copied under the crawl state lock. Paused, disabled and fault states show no active rotation input. `tests/hud.c` checks remapped names, combined inputs, inactive states and all six line positions at both anchors.

## Four-line display (alpha.16)

`HUD_LINE_COUNT` is now four. The first line uses `Crawl system: Standby|Active; Strength: NNx; Force: XX.XX kN`. The second combines direction and applying/connected engines. The third shows `None`, `LEFT`, `RIGHT`, `UPRIGHT`, `LEFT + UPRIGHT` or `RIGHT + UPRIGHT`. The fourth lists the configured derail key and native mapped rotation controls. Buffers accommodate the combined labels. Tests cover both anchors, signed two-decimal force, inactive states, remapping and combined input order.

Alpha.16 was checked in a loaded MegaCoaster driving scene at 640×480: all four HUD lines were visible, F12 (configured for the test) invoked native derailment, and Standby changed to Active. The main-menu paragraph and restored route-selection navigation were checked visually. The keyboard test required temporarily skipping the intro movie; the user’s original movie preference was restored afterward.
