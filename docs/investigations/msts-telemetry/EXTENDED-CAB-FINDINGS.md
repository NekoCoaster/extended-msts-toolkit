# Extended cab helper: bounded branch evidence

Installed-image helper422f06 accepts base enum<=43 directly, otherwise subtracts100 and range-checks<=20 hexadecimal. It indexes bytes at422ea0, then dword destinations at422eb4. The byte map before the adjacent destination table has20 decimal entries, corresponding to100..113. Values114..120 index destination-table bytes as remap indexes. Their calculated targets include data addresses and non-image addresses. Do not describe the range check as33 supported extended channels or execute those IDs to test them. Upstream reachability/parser filtering remains untraced.

extended-cab-table-evidence.json preserves102 disk bytes and confirms an exact live-memory match, plus all33 arithmetic index results. This is table evidence, not blanket channel support. No game memory was changed.

| IDs | Destination | Observed branch behavior |
|---|---|---|
|102|4230a7|Boolean test of caller-context+410, written to cab object+190. Style6 updates display; other styles fall through to the next branch. Context meaning unverified.|
|104|422f34|Player service/global speed-limit-related selection, followed by display-unit conversion. Contains unusual stack/control-flow behavior; do not substitute it for verified service+220 effective-cap calculation.|
|105|422ff7|Computes abs(player train+92)+(train+96/60)*3600, clamps negative result to0, then display conversion. This resembles projected speed but train+96 semantics must be proved before naming it.|
|106|423042|Scans cars from activity-associated train; tests car+84 mask3f00 and car+88 mask3f000, emits float0/1 to cab+18c. Flag meanings remain unresolved.|
|107,108,109|4230e6|Copies caller-context+450 to cab+190; shared source does not imply three independent telemetry fields.|
|10a|423120|Lead-car+472 positive selects+476, otherwise+2c2; cab unit enum10 bypasses the alternate multiplier. Related to existing traction/dynamic-current surfaces, not automatically a new physical variable.|
|10b|4231cf|Copies lead-car+2d2 to cab+18c and updates numeric display; related to existing RPM candidate.|
|100,101,103,10c..113|4231f0|NOP sequence to zero return; no display value written in this branch.|

Unit constants753e48/753e50 are approximately2.236936 and3.6, consistent with m/s to mph/km/h. The105 arithmetic uses60 and3600 exactly. This does not establish the source acceleration units or live output validity.

Ghidra's stored function body omitted all target blocks, and helper decompilation exceeded its flow limit. TelemetryRange.java now supplies a bounded pseudo-disassembly independent of the stored function body, without changing the database. export_range.ps1 invokes it with the existing read-only project. pass60c decodes422f34..423251:269 instructions/798 bytes, all match installed disk and live process. This is linear decoding from known branch boundaries, not a recovered full control-flow graph.

Preserved tooling failures: pass60 attempted to open the project while pass59 was still alive and failed its lock; pass59 then completed, with decompiler failure recorded. pass60b's listing-only approach omitted undefined instructions and was replaced by pseudo-disassembly in pass60c. A scriptblock wrapper failed because PSScriptRoot was empty; the saved export_range.ps1 fixes that path context. No retries launched over the same live process after the lock failure.

Inventory remains768. Extended branch evidence is retained here pending upstream enum-name resolution, exact caller-context mapping and live channel validation. Existing source fields must be merged with these display routes where they describe the same quantity; unsupported branches are not counted as telemetry.

## Caller-context follow-up, 2026-10-10

The two recorded direct callers resolve the previously unnamed context. Electric0041f357 and diesel0042064b both load player train from007c2ac0, then wrapper=[train+72], controller=[wrapper+8], and store that controller in caller stack local[EBP-8]. They put the cab object in[EBP-c], load its channel enum from+f8 intoECX, then call00422f06. The helper pushesEBP without making a new frame, so its references to those locals belong to the caller. This is consistent with the established controller traversal in ELECTRIC-CAB-FINDINGS.md.

Therefore branch102 at004230a7 tests controller+410 for nonzero; branches107/108/109 at004230e6 copy controller+450. These are controller fields, not generic cab-object offsets. Their semantic names, units and writer lifecycles remain unresolved. The style-dependent102 fallthrough into004230e6 is preserved; do not present its boolean test as an unconditional final displayed value.

Fresh external read-only verification in PID12888 covers four exported ranges,66 instructions/251 bytes, with zero disk/live mismatches and zero read errors. captures/extended-cab-context-native-20261010-01 preserves the two caller prefixes, helper export, selected context branches, exact verifier sources and source hashes/range bounds. The sibling byte-verification report records the comparison. This bounds the context claim to the inspected electric/diesel call paths; it neither proves parser reachability nor validates a live extended channel. No unsafe extended enum was invoked and no new independent telemetry quantity was added.

## Extended-name parser follow-up, 2026-10-10

Parser004065f8 calls00406750 after its ordinary style or channel-name table fails. The extension helper compares the same input string against12 pointers at00780160. A match puts index+0x100 inEAX and replaces its return address with0040672d (the parser epilogue). Exhaustion replaces the return address with00406719 (the failed-match diagnostic and -1 return). The decompiler omits these return-address effects; assembly is authoritative. This establishes a named parser path to exactly0x100..0x10b, not33 supported channels from the downstream range check. Other upstream routes are not excluded by this local finding.

| Enum | Parser name |
|---|---|
|0x100|DOORS_LEFT|
|0x101|DOORS_RIGHT|
|0x102|PANTOGRAPH2|
|0x103|CABLIGHT|
|0x104|SPEEDLIMIT|
|0x105|SPEED_PROJECTED|
|0x106|DOORS_DISPLAY|
|0x107|PANTOGRAPHS_4C|
|0x108|PANTOGRAPHS_4|
|0x109|PANTOGRAPHS_5|
|0x10a|AMMETER_ABS|
|0x10b|RPM|

All12 name strings and the48-byte pointer table match live PID12888 and disk. The two parser functions also match disk/live across126 instructions/398 bytes with zero read errors. Evidence: extended-cab-parser-native-20261010 and its byte-verification report; captures/extended-cab-names-20261010-01/names.json retains names, pointers, raw bytes and exact probe sources. The reference-only export extended-cab-parser-refs-20261010 records the base table users and two helper callers.

Names strengthen intended display labels but do not prove physical meaning: PANTOGRAPH2 tests controller+410, the three PANTOGRAPHS aliases copy+450, and SPEED_PROJECTED does not establish train+96 units or a physically valid prediction. DOORS_LEFT,DOORS_RIGHT and CABLIGHT still route to the previously observed no-update branch in this helper. No channel was injected, activated or exercised through a modified cab file. Installed declaration usage and live display validation remain open. Existing68base-channel inventory count is unchanged; the12extension parser mappings are retained here as display-route evidence, not12new independent measured quantities.

## Installed fixture scan, 2026-10-10

scan_extended_cab_fixtures.py scanned all12 CVF files under C:/MSTS/TRAINS/TRAINSET. All were readable text with recognized signatures; no skipped files and no Type declarations matching any of the12 extension names. extended-cab-fixture-scan-20261010.json retains every file path/hash/size and the name-table source hash. This is a bounded text-declaration scan, not a full grammar parser or a claim about other installations. It provides no existing declared extended-channel fixture for a live test under the preserved-assets constraint. Native extension names/branches remain valid static findings; runtime display behavior remains unvalidated.

## Source alias and type review, 2026-10-10

extended-cab-route-map.json consolidates the12 parser names, source expressions, applicability, lifecycle and limitations. Three PANTOGRAPHS names share controller+450. RPM reads lead+2d2; ENGINE-MONITOR-FINDINGS independently documents a diesel-gated RPM consumer of that offset. STEAM_PR uses the same offset as pressure in the steam layout, so offset equality is not a cross-engine semantic alias. The electric helper caller does not establish an electric RPM quantity. AMMETER_ABS likewise selects engine-type-specific lead fields, not a measurement of wheel force. SPEED_PROJECTED retains its literal expression and unresolved train+96 units. No new independent quantity or general unit claim follows from these display aliases.

## Current installation context — user clarification, 2026-10-10

The user confirms that this instance has MSTSBin loaded, has no NEMT loaded, and has no community night-cab addons installed. Night-cab addon support is distinct from the extended instrument-channel parser studied in EXTENDED-CAB-FINDINGS.md. The installed CVF scan tests instrument Type declarations; it is not a night-texture asset audit. The midnight experiment tests simulation clock rollover and calendar carry, not night-cab rendering. No addon installation or game-asset modification is part of this research.


## Projected-speed metadata reconciliation

TRAIN-ACCELERATION-FINDINGS.md supersedes the earlier unresolved train+96 unit statement: native producer and debug label establish stored aggregate acceleration in m/s squared, with player-specific history filtering and rate limiting. extended-cab-route-map.json now carries that evidence. Physical prediction validity and live display behavior remain unvalidated; the earlier branch observations remain historical evidence.
