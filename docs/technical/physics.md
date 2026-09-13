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

The identified drag coefficients and world-relative pitch-rate contribution scale by `1 - u`. Full throttle removes those contributions; closed throttle restores them. The pitch filter preserves turning around world vertical and rolling around the train's length. Existing tilt is preserved, and underlying angular momentum is not erased. Lowering throttle can reveal rotation already present in that momentum. Contacts and gravity continue to use the native solver.

Drag filtering is limited to six calls to `0x62E7C6` from the derailment force routine: returns `0x62B18A`, `0x62B207`, `0x62B30E`, `0x62B38D`, `0x62B45A`, `0x62B4D6`. Linear velocity is at body + `0x88`, angular velocity at + `0x94`. Shared vehicle definitions are never edited.

Pitch filtering changes the angular-velocity input to the orientation derivative `0x5F874C`. It reads world angular velocity at body + `0x94` and the forward vector at + `0x24` from that callback's current integration buffer. With normalized forward `f`, world up `(0, 1, 0)`, and throttle/regulator `u`:

```text
p = world_up cross f = (f.z, 0, -f.x)
h2 = dot(p, p)
omega_filtered = omega - u * dot(omega, p) * p / max(h2, 0.0001)
```

For an ordinary heading this suppresses the angular component about the horizontal axis perpendicular to the train's heading. It is independent of body roll and the sign of forward, so reversing or lying on either side does not select a different compensation axis. World yaw and longitudinal roll are orthogonal to `p` and remain intact. This preserves the current inclination; it does not pull the train upright or level it with the terrain.

Within approximately 0.57 degrees of straight up/down, suppression smoothly fades with `h2 / 0.0001`. At exactly vertical it is a no-op because there is no unique horizontal heading. This avoids amplifying small orientation noise or choosing a body-relative fallback axis.

The former body-right projection could suppress world yaw for a train lying on its side. Merely negating that right vector (a level train rolled exactly 180 degrees) was already sign-invariant; the error was choosing an axis that followed body roll. The two scoped helper returns remain `0x5F8796` and `0x5F8876`, covering quaternion and matrix derivatives. Physical orientation and angular momentum are not temporarily overwritten. See the [fix investigation and validation](../investigations/world-pitch.md).

## Wheels and steam rods

```text
equivalent wheel speed = signed longitudinal derailed speed × max(1, B × u)
```

At boost 10, 10 mph of movement gives 100 mph equivalent wheel speed at full throttle, 50 mph at half, and 10 mph at zero. Vertical or sideways movement alone produces no rotation. Reverse longitudinal movement reverses the animation.

Ordinary wheel animation uses `0x5D5381` and the normal wheel-radius factor at definition + `0x4A0`. The steam driving-wheel/rod cycle uses `0x405694`, with revolutions per second derived from engine wheel radius at + `0x112`. Native model orientation handling and phase animation remain intact.

Animation-rate fields are substituted only for the duration of their native visual routine and restored on return. Body momentum and velocity are not changed by these hooks. Mid-function probes crashed before any override ran; the shipped prototype used stable function-entry hooks instead. High apparent wheel speed can alias against the frame rate, making wheels appear to stand still or turn backward.

## Player rotational assistance (alpha.14)

Alpha.14 added no detours. Its frame callback reads held native keyboard bindings from IOM's device list (`0x8299A0`), device keyboard bitset (`+0x24`), and binding table (`+0x18`, keyboard offset `+0x10`). It checks native modifier masks, disabled bindings/actions/listeners, mode `0x829980`, foreground focus and pause. Traversals are bounded; failed reads produce no rotational input. Keyboard remapping follows the registered callbacks and controller contexts: horn/whistle `0x489A25` with steam controller `+0x368` or diesel/electric `+0x1C4`; train brake increase/decrease `0x4898DD`/`0x489987` with steam `+0xE0` or diesel/electric `+0x10C`. Brake position is not used, so a held key still steers at the lever's end stop. Joystick and mouse-operated cab controls are not rotational inputs.

The body basis is right `+0x0C`, up `+0x18`, forward `+0x24`. Righting chooses `atan2(-right.y, up.y)` about forward, with a deterministic positive-roll tie when exactly inverted. A proportional target (`0.6 * angle`) is limited to 0.35 rad/s, approached with at most `0.25 * strength/10` rad/s². Local-up steering approaches ±0.25 rad/s with at most `0.15 * strength/10` rad/s². Both steering directions held together cancel. Near a vertical nose, the righting increment fades over horizontal-heading length 0.01 and is zero below 0.0001. Rates describe the requested assist; collisions can oppose it and existing external spin is not forcibly clamped.

Native `0x5F6368` computes world angular velocity at `+0x94` from the world inverse-inertia tensor at `+0x64` and angular momentum at `+0x58` (matrix/vector helper `0x5FD74F`). The assist solves this symmetric positive-definite tensor for an angular impulse matching its requested velocity increment, validates every connected engine's planned writes first, then updates both fields. Invalid tensors fail closed. The existing simulation-time deduplication and 0.25-second timestep cap apply. Strength zero, paused scenes, on-rail and unpowered cars receive no added rotational impulse.

While an eligible powered locomotive receives rotational input, its angular drag contribution is suppressed and sleep is cleared; linear drag retains the throttle rule. During directional steering, that locomotive's derivative uses native angular velocity without pitch suppression so local-up rotation survives when rolled. Releasing steering restores world-relative pitch filtering. No orientation, horn state, brake state or shared vehicle definition is written.

Validation: `tests/rotation.c` covers 1,920 heading/roll/slope combinations, shortest-path convergence at 30/60/120 Hz, local-up signs and rotated anisotropic inertia. `tests/crawl-controls.c` covers all three controller types, remapped keys/modifiers, native masks, release/focus/menu/pause gates, stationary rotation, freight exclusion, simulation-step deduplication and full-throttle derivative interaction. These are isolated native regression tests; final in-game control feel still needs gameplay verification.

## Input bounds and manual derailment (alpha.15)

A read-only inspection of a loaded KIHA 31 driving scene on MegaCoaster found **238** native keyboard entries and a **30-byte** bitset. The following allocator bytes were nonzero (`5B 03`). Alpha.14 assumed 256 entries / 32 bytes, treated those bytes as held keys, and could reject the entire sample after following a nonexistent binding. The reader now uses the native table end (`device +0x14`) minus the key offset (`+0x10`) and reads exactly `ceil(count/8)` bitset bytes. `tests/crawl-controls.c` places both buffers directly against inaccessible guard pages and reproduces the nonzero allocator tail. The corrected reader also recognized Space against the live process, without attaching a debugger or modifying process memory. Rotational axis selection is unchanged: longitudinal roll for Space and local-up yaw for train brake keys.

Shortcut names come from the checked binding traversal, refresh once per second, and include required modifiers. The HUD reports the current eligible rotational input. Input sampling now runs on every simulation-frame callback even before derailment, while the larger on-rail consist snapshot retains its normal interval. Pause, focus and native input mode gate all commands.

Unmodified backslash (DIK `0x2B`) supplies an edge-triggered manual derail request. The request survives a press and release in the same IOM poll, which a held-bit-only physics sample could miss. After the existing driving-readiness stage, the simulation-thread frame callback validates the controlled reciprocal consist, rejects cyclic links, checks the exact six-byte entry of native routine `0x62E017`, and invokes it for each not-yet-derailed connected car. The native routine handles vehicle/train flags, camera notification, native coupler settings and engine derail state; NEMT also wakes stationary bodies and refreshes its snapshot afterward. This deliberately uses native side effects, including the routine's own in-memory vehicle-definition updates. No on-disk executable bytes or route/train files are changed. A single checked buffered-key hook at `0x6BAE0E` captures keydown before native IOM dispatch; it uses the shared mutation transaction and is installed only at the existing driving-readiness stage. This site is separate from the toolset keyboard hook because the simulator and toolset startup paths are mutually exclusive. Crawl plus activity-end prevention is required; crawl strength zero still permits the deliberate derail command. Holding the key through loading, pause, menus or focus loss cannot repeat it without a release.

`tests/manual-derail.c` executes the actual native routine from both supported executable fixtures, replacing only camera/wake callees with observers. It covers all-car native flags, engine/freight differences, train state, wake-up, already-derailed exclusion, signature/cycle rejection and one-shot/pause/feature gating. Existing rotation, pitch, lifecycle, HUD, shared-transaction and driving-readiness regression checks remain in place.

Live follow-up: the final build was launched normally with `-vm:w`, a MegaCoaster driving scene finished loading, and a backslash tap invoked derailment and switched to the native derail camera. The extended white F5 HUD subsequently showed **active** crawling, the mapped Space/semicolon/apostrophe labels, the rotation-input line and the manual-derail hint. F5 still cycled normally. A short diagnostic capture of the already-loaded scene observed a normal F5 keydown/release traverse the buffered hook with the original event pointer and key code preserved. The capture was detached and the test session was closed without saving. Sustained righting/steering strength against different terrain and vehicle masses still needs gameplay feel testing; the confirmed alpha.14 failure was the keyboard-buffer overread, and the angular gains were not changed in this fix.
