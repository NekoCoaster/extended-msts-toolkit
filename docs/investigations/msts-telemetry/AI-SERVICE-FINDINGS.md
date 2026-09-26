# AI service and driver discovery checkpoint

26 September 2026. Independent research; no NEMT changes. Process 7160 remained paused at simulation time 74000.0546875.

## Service identities beyond physical trains

Native lookup 0x5a8ecb returns null for -1, the player singleton 0x809890 for zero, or searches the circular list at [0x809af8] by service+0x40. List nodes contain next at +0 and service pointer at +8. This is separate from the physical train registry.

`service-registry-paused-01` contains:

| Service ID | Asset key | Train ID | Physical train | Consist reference | Path reference |
|---|---|---|---|---|---|
| 0 | EveGrain | 400007 | 23 vehicles | Dash921gran | EveGrain |
| 2 | EveGrain (Traffic) | 400005 | 22 vehicles | 2 x Dash 9, 20 Intermodal | EveGrain (Traffic) |
| 3 | EveGrain (Traffic01) | 400006 | null | D9gds | EveGrain (Traffic) |

Bounded UTF-16 strings: service+8 asset key, +0xc display name, +0x10 Train_Config, +0x14 PathID. Live values match installed SRV files, including player display name Night Grain Train (Player). These references enable static-asset joins; IDs/pointers are session-local. Parser/assignment tracing remains open.

The traffic file schedules first AI at 73020 and second at 74460 seconds. The later service exists at 74000 while its train pointer is null. This proves loaded service enumeration before physical creation, not its subsequent start/spawn. Null train can also reflect distance-based removal; do not automatically label it future/not-started.

Train+0xe6 links to service; service+0x158 links back. Both physical train backlinks match. Creation function 0x5a7a5f assigns this relationship. AI physicalization flag +0x134 is set/cleared by 0x5a58af with distance conditions. Player has flag zero despite valid train, so it is not a universal active flag.

## Driver motion and limits

Service+0x138 is signed current speed. AI read 15.6463995 m/s versus physical train 15.6463957 m/s; player read zero. Target +0x13c and acceleration +0x140 feed kinematic updates in 0x5a41c2 and 0x5a5c9a. Distance integrates speed over dt, speed advances toward target using acceleration, sign uses +0x1dc. These are AI driver values, not independent throttle/brake inputs.

Service+0x208 was 0.75 for all three, matching configured Efficiency and scaling speed/acceleration; initialization binding remains to verify. Active AI target was 15.6463995 with zero acceleration. Paused steady-speed evidence does not validate changing targets or stop transitions.

Service+0x220 is a combined cap produced by 0x5a33af from route/default and service limits, with negative sentinels and flag gates. Player read 17.8815994 m/s (40 mph), AI 15.6463995 (35 mph). It is not necessarily one speedboard value. Inputs +0x224/+0x228/+0x22c need semantic separation.

Stop/wait candidates: +0x1e0 path-end stop; +0x1e4 braking-to-wait; +0x1e8 dwell; +0x1ec elapsed dwell; +0x1f0 duration; +0x210 countdown; +0x214 countdown gate. Control flow supports these labels, but exact operational meaning and nonzero transitions remain untested. All were zero here.

## Shared profile context

0x5a41c2 traverses global profile 0x809f1c after profile-building calls for a service; 0x5a3941 consumes the same global. Treat it as per-evaluation/context-dependent data rather than a permanent player-only list. Asynchronous polling cannot assign every entry to a service without a context mechanism. Separate verified iterator 0x809ac4 remains the player UI signal source.

## Evidence and remaining work

`read_services.py` captures physical train associations and broader service list, with bounded traversal/strings, exact script copies and simulation-time checks. `service-fields.json` adds 24 flat candidates without prioritization.

Passes 10–12 preserve native code. Pass11 compares 7,408 instructions / 28,997 bytes: all disk bytes match. One live call differs at 0x494bc1 in broad caller 0x494850 (expected e891c7f6ff; actual e82e573a02). Patch origin is unknown. Driver/registry functions in that pass have no live differences. Do not describe the running executable as globally unpatched. See `pass11-byte-verification.json`.

Next: moving-service and scheduled/distance-driven lifecycle captures; service timing/state initialization; track-position records +0x4c/+0xb4; independent AI brake/traction depth; profile ownership. These remain open. No game input occurred during this checkpoint; pause and on-rail state are confirmed by the read-only captures.
