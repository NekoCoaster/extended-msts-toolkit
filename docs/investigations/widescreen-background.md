# Historical widescreen and in-game options investigation

> Historical snapshot: later work shipped the scoped cab-dial correction. In-game settings remain excluded. See the [validation summary](../technical/validation.md) for the delivered scope.

## Scope

This is a static comparison of the supported original and widescreen executable fixtures, performed in the development VM. It is not a cab-needle fix or a new live rendering measurement. No executable or decompiled game source is distributed.

## What the widescreen patch changes

The compared fixtures differ in 108 bytes, grouped into ten nearby regions. The changes cover resolution-table entries, three conditional branches and a jump into an added calculation.

Two branches in the display-options routines (`0x4633b3` and `0x464604`) stop skipping resolution entries based on their availability flag. A third (`0x521a17`) bypasses the maximum-width comparison when marking a matching resolution available. The table begins at `0x79ca70` in the loaded image.

The jump at `0x6b91f6` enters code at `0x72b1e2`. It transforms the incoming angle using:

```text
adjusted angle = 2 × atan(tan(original angle / 2) × (width / height) × 0.75)
```

The screen dimensions come from `0x7a8960` and `0x7a8964`; the constants are 0.5 and 0.75. The result returns to the original projection calculation. At a 4:3 aspect ratio the multiplier is one; wider displays increase the angle. This establishes a projection/FOV adjustment, not a texture-upload transformation.

## Cab textures and needles

The comparison does not establish that this patch stretches each cab texture before upload. Cab backgrounds, independently drawn needles, clipping rectangles and mouse hit regions may follow different coordinate paths. A safe correction needs a live comparison of those paths using a cab with a reproducible needle defect.

The intended experiment is a single screen-relative horizontal transform shared by the background, instruments, clipping and hit testing. Applying it only to the background could move needles or clickable controls out of alignment. No such change is enabled in this release.

## In-game options

This feature is out of scope. Widget add-ons can replace the existing layouts, so embedding toolkit controls would add compatibility work for limited benefit. Configuration will remain in the standalone form and `settings.ini`. The native widget findings are retained as research, not an implementation roadmap.

Adding controls to the General Options page is a plausible separate investigation. It requires identifying native control creation, placement, input callbacks, page teardown and saving. The fixed artwork limits available space, but that alone does not establish whether new checkboxes can be added safely.

For now the standalone form owns configuration. Several features initialize at startup, so an eventual in-game form would need to distinguish saved settings from features already active and show when a restart is required. The thrust slider remains in the standalone form. No in-game settings controls have been implemented or validated.

## Follow-up investigation

The [September 12 investigation](settings-and-cab-needles.md) identifies native checkbox read/write routines and the cab needle’s scale-before-rotation path. It includes a proposed scoped correction and independent geometry tests. Live integration is still pending.
