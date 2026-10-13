# Track geometry joined to player and AI location

Read-only observations at paused simulation time 74525.53125; no gameplay changes this checkpoint.

## Layout and native evidence

Geometry definition g = [[0x80a118]+0xc] + uint16(section+0)*0x18. Table count is [[0x80a118]+0x10]; the reader now bounds the definition index against it. Existing section-pointer validation remains required.

| Offset | Meaning | Evidence |
|---|---|---|
| +0 | Section length, metres | Traversal 0x5b277e and parser 0x5caf51 |
| +4 | Curve radius, metres; zero for straight | SectionCurve first value; used as divisor of distance for angular displacement |
| +8 | Signed total curve angle, radians | SectionCurve degrees converted by native constant 0x753f74 |
| +0xc | Configured width | SectionSize first float; observed 1.5, not proven physical rail gauge |
| +0x10 | Section skew angle, radians | SectionSkew converted in parser |
| +0x14 | Raw flags, uint32 | SectionFlags parser ORs bits; individual meanings incomplete |

Native name table entries pair pointer THEN token: SectionSize at 0x794e30 maps to 0x40075; SectionCurve at 0x794e48 maps to 0x40078. The neighboring preceding token belongs to another name. Parser 0x5caf51 reads width and straight length directly, radius and angle separately, and replaces curved length with radius times absolute converted angle. Malformed decompiler prototypes omit output pointers; the assembly destinations establish the offsets.

Section-origin angles at section+0x2c initialize record+0x18. Traversal changes heading using distance/radius and curve-angle sign, and subtracts pi for the reverse track direction. Full orientation and banking conventions remain incomplete. Nominal curvature magnitude can be derived as 1/abs(radius), or zero for a straight; do not call this measured train yaw curvature or signed driver-relative turn.

Pass30 verified 1,307 instructions / 4,876 bytes; pass31 verified 326 / 1,168. Zero disk/live mismatches and zero read errors. Verification covers exported instructions only.

## Live and asset comparisons

`geometry-services-paused-01` captured all 23 player vehicle records plus all three loaded service records, including both offscreen AI. `geometry-typed-paused-01` repeats with correctly typed flags and native table bound. Earlier raw captures remain unchanged; their final geometry float slot was an offset-labeled candidate and must not be interpreted as a real float quantity.

Four distinct geometry definitions matched installed GLOBAL/tsection.dat. `analyse_geometry.py` preserves the source hash, exact selected definition excerpts and comparison errors in `geometry-summary.json`. Largest length discrepancy versus double-precision asset formula was 0.0001294 m, consistent with native float/conversion precision.

- Player lead: definition 3, straight 250 m.
- First AI: definition 59, radius 1002.492493 m, total angle -0.1745328 rad, length 174.967819 m.
- Later AI: definition 15, radius 497.507507 m, same total angle, length 86.831375 m.

These are loaded geometry values associated with runtime location, not independently changing physics fields. An inactive service can retain a valid but stale location, as established in SERVICE-UPDATE-FINDINGS.md.

## Gradient evidence and limits

Twenty adjacent player-car pairs shared a section, allowing a comparison of change in track-reference Y divided by change in node distance against -sin(record first angle). For straight sections, maximum absolute discrepancy was 0.00002857. Across all tested pairs, including curves, the maximum was 0.0003123. Precision, reference spacing and varying curved tangent contribute; this is not a universal error bound.

Candidate straight grade along increasing node distance is -100*tan(section first angle), in percent. The observed small-angle slope agreement supports this scoped candidate. Arbitrary traversal reversal, curved tangent gradient and the sign convention of the native HUD have not been validated. Do not silently apply the straight formula to every track record. Origin-shift validation is still separate and incomplete.
