# Crawl physics and animation

This is an arcade addition to MSTS's derailment solver. It keeps the native derailed state and collision handling, then supplies extra momentum to eligible powered vehicles. It does not rerail a train or restore realistic wheel/rail traction.

## Connected powered vehicles

The controlled locomotive comes from `[0x7C2AC0] + 0x6A`. The graph follows each car's reciprocal links at + `0xA0` and + `0xA8`, including unpowered intermediate cars. The walk is bounded at 256 vehicles and rejects inconsistent links. A powered car is identified by vehicle definition + `0x88` equal to 1.

Coupler type is not a whitelist. Eligibility follows the live connection graph. A visually separated vehicle can remain logically connected; a real link break removes its eligibility without erasing its existing momentum. The native uncoupler at `0x635DFB` is checked before and after each attempt. Only changed links trigger a graph refresh. Rebuilding the graph on every unsuccessful attempt caused a severe performance regression and was removed.

Only physically derailed powered vehicles receive added thrust. Connected unpowered cars participate in the drag, pitch and wheel-animation treatment. A powered vehicle still on rails continues to use native traction.

## Force and timestep

Let `u` be throttle/regulator fraction, `d` the sign of the reverser, `B` the selected boost, and `v` the signed projection of body velocity onto its forward axis:

```text
F = B × u × d × min(MaxForce, MaxPower / max(0.5, abs(v)))
dt_applied = min(dt_simulation, 0.25 seconds)
momentum += forward_axis × F × dt_applied
velocity += forward_axis × F × dt_applied / mass
```

Each engine contributes using its own force, power and mass. The 0.5 m/s divisor floor avoids division by zero; the maximum-force term caps low-speed effort. A zero-duration frame adds no impulse. Finite-value and range checks run before propulsion writes. The 0.25-second cap limits a single stalled-frame kick; it is not a duration limit on crawl mode.

Mass is the reciprocal of body + `0xC8`. Maximum power and force are engine definition + `0xFE` and + `0x102`. The current body pointer at car + `0x5C` must be reread because physics buffers swap. Momentum is body + `0x4C`, velocity + `0x88`, forward axis + `0x24`, and position + `0x30`. Body + `0xF2`, bit 4 denotes physical derailment; bit 8 denotes resting. Eligible moving bodies are kept awake.

The backward-facing Dash 9 test showed that its body axis already followed consist direction. Applying an additional force reversal from the model's orientation flag would have been wrong.

## Steam controls

Control type at `0x7B6438`: 1 steam, 2 diesel, 3 electric. The control object is `[0x7B6440]`.

| Type | Throttle/regulator | Signed reverser |
|---|---|---|
| Steam | + `0x54` | + `0x8C` |
| Diesel/electric | + `0x8C` | + `0xC8` |

For steam, cutoff magnitude is not another thrust multiplier. Its sign selects direction, zero selects neutral. Boiler pressure, fuel, adhesion and heating do not limit artificial crawl thrust. Control + `0x1C` is a combined power value, not the reverser.

## Drag and pitching

The identified drag coefficients and local pitch-rate contribution scale by `1 - u`. Full throttle removes those contributions; closed throttle restores them. Contacts, gravity, yaw and roll remain native. Existing tilt is preserved, and underlying angular momentum is not erased. Lowering throttle can reveal rotation already present in that momentum.

Drag filtering is limited to six calls to `0x62E7C6` from the derailment force routine: returns `0x62B18A`, `0x62B207`, `0x62B30E`, `0x62B38D`, `0x62B45A`, `0x62B4D6`. Linear velocity is at body + `0x88`, angular velocity at + `0x94`. Shared vehicle definitions are never edited.

Pitch filtering changes the angular-velocity input to the orientation derivative `0x5F874C`. Scratch vectors remove only the component along body-local right. The two scoped helper returns are `0x5F8796` and `0x5F8876`. Physical orientation and angular momentum are not temporarily overwritten.

## Wheels and steam rods

```text
equivalent wheel speed = signed longitudinal derailed speed × max(1, B × u)
```

At boost 10, 10 mph of movement gives 100 mph equivalent wheel speed at full throttle, 50 mph at half, and 10 mph at zero. Vertical or sideways movement alone produces no rotation. Reverse longitudinal movement reverses the animation.

Ordinary wheel animation uses `0x5D5381` and the normal wheel-radius factor at definition + `0x4A0`. The steam driving-wheel/rod cycle uses `0x405694`, with revolutions per second derived from engine wheel radius at + `0x112`. Native model orientation handling and phase animation remain intact.

Animation-rate fields are substituted only for the duration of their native visual routine and restored on return. Body momentum and velocity are not changed by these hooks. Mid-function probes crashed before any override ran; the shipped prototype used stable function-entry hooks instead. High apparent wheel speed can alias against the frame rate, making wheels appear to stand still or turn backward.
