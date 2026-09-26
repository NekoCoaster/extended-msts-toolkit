# Signal and cab discovery checkpoint

Independent research, 26 September 2026. No NEMT integration or prioritization.

## Live next-signal source

Track-monitor UI producer 0x46634a uses the iterator at 0x809ac4 (four uint32: node, direction, first index, last index), with distance at 0x809ad4. Node+0x20 points to a table of head pointers. Native 0x5c01c2 filters head type zero, direction at byte +0x20, and function type at [[head+0x14]+4]. Within a function type it selects the maximum aspect byte at head+0x21. Normal function type is zero; speed is one. 0x5c12c3 combines those results.

Aspect table is [[head+0x14]+0x50], records 12 bytes: speed at +4 and flags at +8. The observed Clear speed -1 is a sentinel, not a negative physical restriction. Generic forward-profile entries previously captured at 0x809f1c are not a substitute for this live source.

`signal-transition-01` captured the same head address 94419796 changing from aspect 0 to 7 at simulation time 73923.046875 (20:32:03.047). The first sampled Stop was 73800.8828125. At the transition, player speed was zero and next-signal distance was 960.541015625 metres. Screenshots `stopped-red.png` and `stopped-clear.png` corroborate the monitor. This establishes the extracted transition; exact occupancy/AI cause and other aspect meanings remain to trace. Do not assert that clearance occurred precisely when the AI passed the player's cab.

The 0x5a35d7 iterator updater is speed-sensitive; stationary iterator caching and route lifecycle still need explicit coverage. Head pointer identity is only session-local.

## Forward monitor joined to the route-clearance capture

clearance-forward-signal-paused-01 at73997.5390625 reads stable iterator[113455676,0,46,46],distance882.1513671875m and one normal head94419988,definition51529832,aspect7,flags32768,speed sentinel-1. Player is stationary. The same-time infrastructure-clearance-final-paused-01 snapshot has exactly one matching head/definition/direction/aspect/flags at database51564896 item318. Iterator index46 and database item318 belong to different index spaces;neither is a portable signal ID.

join_forward_signal.py verifies that head and definition in all421 infrastructure-ai-clearance-01 samples. It remains aspect0,flags0,associationnull until sample287 at73923.2265625..73923.34375,then changes to aspect7,flags32768,player association8427664. The preceding interval begins73922.7265625. This is the player-forward signal joined to the route acquisition sequence after the last AIpresence record crossed300->310 and the AI releasedjunction302/vector300. Earlier independent signal-transition-01 screenshots establish0Stop/7Clear for this installed context. The new join itself is a pointer/definition and current-iterator verification;the forward iterator was not continuously captured during the clearance run,so historical attribution is conditional on this same-run continuity. No visual color timing or exact native call order is claimed.

forward-signal-clearance-join.json preserves allthree raw source hashes and state changes. No new candidate count;this closes the previously missing item join for the captured stationary-player run. Player crossing,other direction/mode cases,origin changes and pointer reuse remain open.

## Cab table and producers

`native-cab-map.json` maps all 68 names at 0x77fce0 against the installed-image jump tables, including 163 source excerpts. Nine names are absent from installed CVFs. Name presence and branch routing are not proof of live support. FUEL_GAUGE enum 67 is not handled by these base dispatchers. Bin helper 0x422f06 also accepts extended values; those need separate discovery.

CabViewType values are electric 1, diesel 2, steam 3, different from the player-controller enum. Decompiled control flow has shared-helper warnings, so the mapping uses raw jump-table bytes and assembly. Extended-table experimentation beyond enum 0x113 ran into adjacent data; do not treat that as valid additional channels without tracing the caller constraints.

Diesel lead-car pressures: main reservoir +0x412, equalizing reservoir +0x436, brake pipe +0x238, cylinder +0x230. When uint16 engine-definition+0x622 has bit 4, cylinder display uses max(+0x230,+0x486). Native pressure is PSI; unit conversions are in the dispatcher. Recorded emergency braking changed pipe/equalizing 90 to zero and cylinder zero to about 85.202 PSI; main reservoir rose from about 93.123 to 130 PSI. Visible integer displays agree.

**Current-unit correction:** lead+0x2c2 is traction amps. If lead+0x472 is positive, the displayed current uses negative lead+0x476 (dynamic amps). AMPS unit enum 16 copies directly; the other branch multiplies by 1000 for the smaller unit. The first detailed probe mistakenly named these raw values `*_kiloamps` and multiplied `ammeter_amps` by 1000. Original capture files and reader copies are preserved, including that error. `analyse_details.py` explicitly normalizes legacy fields in its derived summary. Current `read_signals_cab.py` is corrected. Initial native 202.987 agrees with the displayed 203 amps. Zero-only paused comparisons did not expose the mistake.

Raw fuel +0x2ce and engine rotation +0x2d2 are recorded as candidates. Fuel display litre conversion factor 4.546092 suggests Imperial gallons internally; producer semantics and engine-rotation units need further validation. Dynamic-braking branch was not exercised in this capture.

## Executable provenance

`pass09-byte-verification.json` compares 2,779 exported instructions / 10,790 bytes across 14 functions against both installed disk image and running process. There were zero disk differences, zero live differences and zero read errors. This covers exported instructions in the diesel dispatcher, monitor UI, signal selection/speed helpers and related callers. It is not a whole-executable comparison and does not cover omitted function chunks, all data tables or future patches.

Reproduce with `export.ps1`, `verify_code_bytes.py --pass-name pass09 --pid <currentPID>`, and `read_signals_cab.py --pid <currentPID> --name <unique-name> --seconds 240`. `analyse_details.py` writes `detail-summary.json`; raw samples remain unchanged. External reads remain asynchronous; same-time and iterator-stability checks expose only some races.

## Remaining work

The wider discovery goal remains active. Next expand per-channel producer semantics, AI service/driver state, stable coordinates, vehicle forces/brakes/couplers, lifecycle and other surfaces listed in README. Full coverage has not been achieved. Do not count static configuration leaves or all named cab channels as independently validated live telemetry.
