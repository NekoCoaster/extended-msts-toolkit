# Crawling after derailment

Enable **Allow connected engines to crawl after derailment** and click Apply. The panel enables **Remove derailment activity-end message** with it so the session can continue.

Use throttle for speed and reverser for direction. Steam locomotives use the regulator. Crawling activates for eligible derailed powered vehicles and clears when the activity ends. There is no timed trial cutoff.

Connected powered engines contribute using their individual power and force values. Eligibility follows the connections MSTS maintains: a car can look separated while the simulator still considers it connected. A disconnected engine no longer receives added thrust from the controlled consist. Unpowered cars do not generate thrust.

Crawling is an arcade feature. It does not put vehicles back on the rails. Throttle also affects the selected derailment drag effects, and wheel animation follows movement and throttle. At **0×**, added thrust and rotational controls are disabled but these other crawling effects remain enabled.

Counter-tilt/pitch filtering is optional and defaults off. Enable **Enable counter-tilt filter while crawling (optional)** in the patcher, or set `CounterTilt=true` under `[Derailment]` in `NEMT/settings.ini`, then restart MSTS. With it off, crawl leaves the native orientation derivative unfiltered. With it on, increasing throttle suppresses nose-up/nose-down rotation relative to world vertical; it does not automatically level the train. Manual left/right steering temporarily bypasses the filter so rotation still works on the train’s side. Friction reduction is present in either mode.

## Righting and steering

While crawling, hold these keys:

| Control (default key) | Movement |
| --- | --- |
| Horn/whistle (**Space**) | Gently roll toward upright along the shorter direction around the locomotive's length. |
| Train brake apply (**'**) | Turn right around the locomotive's own up axis. |
| Train brake release (**;**) | Turn left around the locomotive's own up axis. |

These follow the corresponding keyboard bindings in MSTS, including modifier keys. The horn and brakes still perform their normal functions. Both steering keys together cancel steering. The controls work with the throttle closed and the reverser in neutral, and stop applying assistance when released, paused, or the game loses focus.

Righting eases off near upright. An exactly upside-down locomotive chooses one of the equally short directions; a locomotive pointing vertically has no unique upright roll direction, so righting fades out there. Steering follows the locomotive even on its side or upside down. Native collisions and gravity still apply, so this is assistance rather than an instant recovery or rerailing command.

Rotational acceleration follows crawl strength; its target roll and turn rates remain modest. The HUD's thrust figure measures forward/backward assistance only; rotational assistance can be active while it reads zero.

## Strength and HUD

The slider ranges from **0–100×**, with **10×** as the starting value. Use **Bottom left** or **Bottom right** to place the HUD; the default is bottom left.

Press **F5** through the standard red pages until MSTS Bin's white extended display appears. The extra lines show crawl state, strength, added thrust, throttle/regulator, reverser and powered-engine counts. Reverse thrust is displayed with a minus sign. This is the added crawl thrust, not the train's total force.

The HUD also shows the current keyboard bindings for upright rotation and steering, plus a live **UPRIGHT**, **LEFT**, or **RIGHT** input indicator. The labels follow MSTS key remapping. Before bindings are available it shows the default keys. If the indicator stays at **None**, the game is not receiving an eligible rotation input.

Press `\` once to derail the currently controlled consist, including at a standstill. This invokes MSTS's native derailment sequence for each connected vehicle. It requires crawling to be enabled, works only in the active driving scene, and does not repeat while held. Pausing or leaving the game requires releasing the key before another command. Modified combinations such as Ctrl+\ do not trigger it. The shortcut is also listed on the extended F5 HUD.

The HUD is included automatically with crawling. If it overlaps a track monitor or another overlay, choose the other bottom corner or move the other display. Its placement follows the current resolution.

## Choose the derail key

With MSTS closed, edit `NEMT/settings.ini` beside `train.exe`:

```ini
[Derailment]
DerailKey=BACKSLASH
```

`BACKSLASH` or `\` selects the default key. You can use a letter, a number, `F1`–`F12`, a named key such as `HOME`, or a DirectInput scan code such as `0x56`. `NONE` disables the shortcut. Escape and modifier keys are rejected; modifiers such as Ctrl are not supported for this command. These are physical keyboard bindings, matching MSTS. Avoid a key already used for a game action: NEMT does not consume its normal function. Apply preserves this setting, and the HUD displays the selected key. Restart MSTS after editing.

The extended HUD uses this four-line format (rotation is **None** when idle, or **UPRIGHT** when righting alone):

```text
Crawl system: Active; Strength: 10x; Force: -12.34 kN
Direction: 50% - Reverse; Applied on engines: 1 of 2;
Active rotation nudge: LEFT + UPRIGHT
Controls: Derail = \  Steer Left = ;  Steer Right = '  Rotate Upright = Space
```

Inactive, disabled, paused and faulted states show **Standby** and zero applied force. The detailed internal fault state remains available in optional diagnostics.
