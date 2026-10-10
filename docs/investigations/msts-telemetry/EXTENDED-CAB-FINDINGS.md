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

## Targeted controller writer navigation, 2026-10-10

TelemetryPantographWrites.java scans existing Ghidra instructions for explicit destination displacements410/450 on MOV,FST/FSTP,AND/OR/XOR,INC/DEC,ADD/SUB. extended-cab-writers-20261010/pantograph-offset-writes.tsv contains one hit:006153f0 inside00614c8e clears dword[ECX+410]. No direct450 destination was found by this bounded syntactic scan. This is navigation evidence,not proof of no writers:missing/displaced analysis,bulk initialization/copy,indexed or aliased addresses,other mnemonics and helper writes are outside the test. Equal offsets on unrelated object classes are not ownership proof. The containing function context and MSTSBin helper code remain necessary before assigning pantograph semantics;the installed fixture limitation remains unchanged.

## Writer ownership correction, 2026-10-10

The sole explicit-displacement scan hit006153f0 is inside vehicle-definition parser00614c8e,already mapped by CONSIST-AGGREGATE-FINDINGS.md (Size+3f8..400 and mass+444) and DEFAULT-PARAMETER-FINDINGS.md. Its local branch clears definition+410 alongside+414/+418 under definition flags+8c. It is not established as a controller writer. The offset coincidence is therefore rejected as pantograph-source evidence;do not rename definition fields from extended-cab labels.

captures/extended-cab-object-context-20261010-01/context.json reads distinct current objects:controller64057724 and vehicle definition56433116,control type3. Both raw410/450 values are zero in both objects;root rereads agree. This reinforces the need for object-qualified field mapping,not semantic equality from values or offsets. The scan produced no qualified controller writer. Next useful writer work must include MSTSBin code outside stored instruction coverage or indirect/bulk operations,not repeat the same displacement scan. No field meaning or live display behavior is claimed.

## Indirect controller-field lead, 2026-10-10

A literal410/450 scan of PE .text is retained in extended-cab-displacement-byte-leads-20261010.json. Matches are byte navigation only,including immediates,data and offsets on unrelated objects. One useful match488ff6 belongs to00487dfe:it forms [7b6440]+410 and passes that pointer alongside callback00489a25 to006bc240. It also registers the same callback against other offsets including3ec,so callback sharing does not independently name the field. This is an address-passing path missed by the direct destination-displacement writer scan,not yet a proven write.

Callback00489a25 invokes00406e7a,then branches on the dword at its EDX pointer:1 selects4840b9 when006baa50()&3==3 or48411b otherwise;2 selects484822;it finishes with489aa1. Assembly/calling context,helper effects and selected operation identities remain necessary before deriving control states or pantograph transitions. The decompiler alone must not be used to infer006bc240's full registration signature.

extended-cab-control-writer-20261010 verifies00487dfe:1676instructions/6879bytes;extended-cab-controller-helper-20261010 verifies00489a25:44instructions/124bytes;all current disk/live exact. The directory name is a navigation label,not a claim of a confirmed writer. No native callback invoked and no new semantic candidate added. Next trace the shared callback helpers and pointer provenance;do not repeat the already exhausted direct-displacement scan.

## Engine-layout qualification and callback interception, 2026-10-10

Control registration00487dfe places controller+410 in the control-type2 branch (diesel),not type3 (electric);the type3 branch exits separately after0040b6f2. Therefore the earlier registration lead cannot name electric controller+410. Callback00489a25 interprets its input as a control record:record+0 selects kinds1/2,while ordinary setters004840b9/0048411b write record+10 and choose configured numeric values at+14/+18 into+1c.00484822 handles a different kind2 layout. This corrects any inference that the first dword is universally a pantograph state.

00406e7a additionally gates a hook on lead engine-definition byte+88==2 and calls00406cd4. The latter tests controller+440 nonzero,compares the supplied control-record pointer against controller+254 and then controller+400 (254+1ac),and redirects them by+1ec or+40 to controller+440. It calls0040d4f0 or0040d482 respectively and replaces a stacked return address with00489a9d,skipping the ordinary callback body. This is assembly-level interception;ordinary decompilation omits that control-flow consequence. It gives a concrete route toward electric controller+450 as an offset within the440 record,but helper semantics must be established before naming it.

extended-cab-control-operations-20261010 verifies5functions/194instructions/608bytes disk/live exact. extended-cab-pantograph-remap-20261010 preserves the remapper and two targets;decompilers warn aboutcccccccc and cannot be trusted for full flow. No native execution,field mutation or UI validation was performed. The next step is bounded assembly interpretation of the two remapped helpers and current byte checks,not reuse of the diesel410 registration as electric-state proof.

## Remapped selector arithmetic and dispatch bounds, 2026-10-10

The inspected remappers0040d482/0040d4f0 first call0048c2ac and require byte[EAX]==34,then subtract3 from record kind+0 and dispatch for unsigned results<=2. They additionally require incoming event dword0==1 before state operations. Table40d4e2 selects40d4ac/40d4c2 for kinds3/4;table40d556 selects40d51a/40d533. Both third entries arecccccccc in disk and current memory. Thus the encoded range check is not proof that kind5 is supported;do not invoke it. captures/extended-cab-pantograph-tables-20261010-01 retains24verified table bytes. Meaning of the byte[EAX] gate remains unlabelled.

0040d384 operates on record+10:direction0 decrements and direction1 increments within0..3;crossing an endpoint wraps only when retained cab object+f8 equals107,otherwise exits without storing the out-of-range value.0040bd46 operates similarly within0..4 but does not wrap. Both gate on record+4!=0,004284f0()==0,and !(record+8==1 && global7b70a0!=0),then call483f60,set record+20=1,and on accepted values call40bd14 and48bc59. Given the established remap to controller+440,this identifies controller+450 as a multi-position selector source for these paths. It does not identify physical pantograph combinations or establish its live availability in the current cab. Input outside the expected range must not be normalized by an external reader.

extended-cab-pantograph-state-20261010 verifies3functions/210instructions/660bytes disk/live exact.0048c2ac searches current cab objects by control pointer and stores a matched identifier at record+c;its retained-EAX contract and upstream gate need assembly-context interpretation,not the decompiler void return alone. The remap verification from the preceding checkpoint also passed93instructions/284bytes. No UI input or native invocation was used.

## Selector-to-control mapping, 2026-10-10

0040bd14 receives EDX=controller+440,EAX=A,ECX=B. It writes A to[EDX-1dc]=controller264 and B to[EDX-30]=controller410,then calls0048411b on control records254 and400. Each ordinary toggle has its own availability/block gates and can invert its record+10 value. Therefore the following table describes pre-toggle assignments,not unconditional final state or roof geometry:

| Selector | Four-position A,B | Five-position A,B |
|---|---|---|
|0|1,1|0,0|
|1|0,1|1,0|
|2|0,0|1,1|
|3|1,0|0,1|
|4|not selected|0,0|

When each toggle is eligible,the corresponding assigned boolean is inverted;if gated it remains assigned. This establishes electric410 as the secondary command/control value paired with264,and450 as their multi-position selector on the traced extension path. It does not establish front/rear pantograph identity,animation completion,overhead contact or actual current. Existing ELECTRIC-CAB-FINDINGS already identifies264 as the ordinary pantograph command/display source.

After mapping,the selector routine calls0048bc59 with the player lead. That routine dispatches0048bc8e only for engine-definition byte88 values2 or3;downstream effects remain outside this bounded review. extended-cab-selector-output-20261010 verifies2functions/34instructions/103bytes disk/live exact. No live transition or installed extended-cab support is claimed.

## Post-selector interlock call, 2026-10-10

0048bc8e,called through0048bc59 after selector updates,is a shared engine control interlock routine. It compares controller reverser/throttle/braking values against retained lead49a/49e/4a2,can revert control changes under its conditions,then refreshes those retained values and calls0048c242(10) if it intervened. The exported function has no direct264/410/450 accesses. Therefore this particular call is not evidence of pantograph roof animation,command propagation or electrical contact. Indirect helper behavior and other update consumers are separate questions. extended-cab-command-consumer-20261010 verifies312instructions/1290bytes disk/live exact. No runtime intervention or execution trace was captured.

## Current control availability, 2026-10-10

captures/extended-cab-control-availability-20261010-01/records.json reads three40-byte records through the current type3 player controller. Primary254 has kind1,gate+4=1,value+10=1. Secondary400 and multi-position440 are entirely zero-filled in the bounded read (kind0,gate0,value0). All record/parent rereads agree. Since00406cd4 requires controller440!=0 and ordinary state setters require record+4!=0,this observed fixture fails those prerequisites. Zero410/450 must therefore not be interpreted as validated lowered pantographs or an active selector at position0. Equal rereads are not atomicity or initialization proof.

This observation agrees with the separate installed-CVF scan's absence of extension declarations but neither proves all installed stock lacks runtime support nor justifies modifying assets. Two independent raw source candidates are retained with explicit availability gates:secondary command record400 and selector record440. Display aliases remain in the route map without creating duplicate independent quantities. Physical mapping and enabled live transitions remain unresolved.
