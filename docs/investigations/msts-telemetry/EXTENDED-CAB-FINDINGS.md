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
