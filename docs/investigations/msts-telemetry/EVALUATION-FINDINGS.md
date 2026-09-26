# Activity evaluation storage and episode candidates

## Freight durability and passenger comfort records

00586666 appends freight records to report+2c and increments+3c; passenger records use+30/+40. Each record contains only float time+0 and marker-derived location+4, with no vehicle identity. Display0043bc16 maps+3c to resources440/441/768 and+40 to43d/43e/767, explicitly naming freight durability and passenger comfort respectively. vehicle-condition-labels.json preserves the installed resource text/hash and branch addresses.

Both collectors require both unsigned counters below40. Either reaching40 disables both collectors. The shared last-record time activity+384 must be-1 or at least30 seconds behind the day-seconds clock80acd4. It advances only when at least one kind records. Several qualifying cars collapse into one record per kind for a sampling opportunity; a continuing condition may record again after30 seconds. These are not complete histories or unique physical incidents. Midnight behavior remains untested.

The native condition takes abs(car+1c0). When this is <= definition+7cc, the threshold is abs(car+1c0)*definition+7d0; otherwise it is1. The reference definition comes from [[80aa1c]+94], not necessarily each tested car. A car qualifies when its float+28e is below that threshold. Definition byte+88==2 selects freight; otherwise byte+88==3 or definition float+c08>0 selects passenger eligibility. The units and physical producers of these inputs remain unresolved, so the UI label must not be presented as measured cargo damage or passenger injury.

captures/evaluation-paused-03/evaluation.json reads both bounded circular lists successfully: both empty/count0, last-record time-1, interval30, report presence flags2. Simulation time stayed74600.2734375 and pause flag1. This validates empty storage extraction only; no exceedance was induced, no new record observed, and no AI collector established. The previously verified pass74/75 instruction ranges support the static mapping. Four inventory candidates added, bringing the local discovery inventory to823; publication remains at2978ac2 with806.

The fixed report object is00809790. Gameplay0048fdd0 passes it in EDX alongside activity00809810 in ECX to00585d56. Teardown004963b7 later calls005897f1 with the same two objects, copying result/duration and building final stop/work-order summaries. Thus the report mixes values collected during gameplay with values assembled at teardown. An external reader must preserve those lifecycle distinctions.

00586987 collects speed-violation episode candidates. Its first gate is unsigned report+38<40. It computes an adjusted nonnegative speed from activity+1b8 through00587c02 minus constant007705b0, compares several restriction inputs, and tracks a condition in activity+398. When the condition begins it records time+388, location-related value+38c, adjusted speed+390, restriction+394 and subtype+39c. While the condition persists it increases the peak+390. On closing the episode it allocates a24-byte record and appends it to the circular list at report+28, increments report+38 and adds the duration to float report+44. It clears the active flag and peak. Old start/location/limit values can remain after closure, so they are not an active event unless+398 says so.

Record layout: start-time float+0, location-related float+4, restriction float+8, duration float+c, peak adjusted speed float+10, subtype uint32+14. List nodes use next+0 and record pointer+8. Native limit is40 completed episodes; when reached, this collector returns without maintaining further episodes. Do not advertise the count/duration as unbounded complete history. The adjusted peak is not automatically the maximum raw train speed, and the location value and subtype names remain unresolved. The report UI consumes these fields, but localized display labels have not yet been mapped independently.

Fresh paused sample captures/evaluation-paused-01/evaluation.json has count0, total duration0, active0 and an empty episode list at simulation74600.2734375. This tests readable empty storage only. The earlier abnormal run's visible speeding totals have not been connected to a retained memory sample, so no historical numeric match is claimed.

Additional traced leads are retained without prematurely labeling them:00586666 records two vehicle-condition lists/counters at report+3c/+40, bounded40 and rate-gated by activity+384. It distinguishes freight and carriage/passenger-bearing vehicle definitions and compares a vehicle+28e value with a threshold derived from+1c0. Full condition semantics remain open.00585e59 records edge-triggered controller-related errors and maintains activity+3a0/+3a4/+3a8/+3ac;00586226 needs tracing to decode its records.

Report finalization00589a96 allocates stop summaries and counts them at report+60.0059a0c0 builds action-type6..9 records and increments report+64, counting clear trigger latches at+68. Do not label these report counts as continuously updated live totals. Their detailed fields and real stop transitions remain future work.

Validation: pass72 (4 functions/555 instructions/2043 bytes), pass73 (3/331/1399), pass74 (3/3865/13712), pass75 (4/699/2520) all match exported instruction bytes on disk/live with zero errors. This proves only recorded instruction ranges, not all evaluator semantics. No UI operation, forced violation, activity exit, asset change or NEMT change occurred. Four candidates are added: completed episode count, total closed duration, active-episode state and completed records. Findings remain local after2978ac2.


## Tolerance, marker location and operational records

00587c02 is float absolute value. The speed collector subtracts float007705b0=0.8940799832344055m/s (2mph equivalent) and clamps negative results to0 before its comparisons/peak storage. Thus adjusted peak is tolerance-subtracted speed, not raw train speed. Restriction checks execute in their traced sequence; no minimum-selection equivalence is claimed. Existing subtype may describe an earlier qualifying condition even if a later comparison replaces the stored limit.

005868f2 calls005afebb in both directions from a track-position record.005b0018 searches track items of kind8 whose flags+28 low three bits are0 and005afebb returns item+2c plus distance information. The wrapper chooses based on marker values and applies its caller-supplied scale to distance when both sides resolve; one-sided results return the marker value directly, and neither side returns-1. This establishes a marker-derived location rather than stable XYZ or distance traveled. Exact route-unit conversion, direction changes, missing markers and interpolation accuracy remain unvalidated; the reader retains location_raw.

00586226 appends12-byte operational records at report+24 and increments report+34. Fields are time float0, marker-related location float4, code uint32+8.00585e59 calls it for rising conditions with codes2,4,8,16; no global completeness or unlimited capacity claim is made. Names still require localized UI/producer mapping.

read_evaluation.py is a bounded reusable reader with exact copies saved beside each capture. evaluation-paused-02 found count2 and two records, codes4 and8, both time73810.6640625 and location1178.2734375. List length matches stored count. Speed episodes remain empty/count0; pause/time are unchanged. The records predate this pass and were not observed being emitted, so their presence validates extraction but not event timing, naming or a causal UI action. Native calls were not invoked.

Pass76:11 functions/2213 instructions/7890 bytes. Pass77:4/194/588. Pass78:2 exported functions; see pass78-byte-verification.json for exact totals. All recorded instruction bytes match disk/live, zero errors. Two candidates are added for operational-error count and records; speed fields receive the tolerance/marker provenance. This remains a local checkpoint after2978ac2.


## Installed operational-error labels

map_evaluation_labels.py follows the actual byte selector at0043d75c and branch table0043d740 used by evaluation display0043bc16, then reads the MOV ECX resource ID in each branch. Selected table bytes and branch instructions match live memory. It extracts only the relevant RT_STRING entries directly from installed string.dll without loading or executing the DLL. evaluation-label-map.json records resource SHA256 and language1033.

Mapping:2 -> resource448 hex (penalty brake application);4 ->449 (emergency brake applied);8 ->44a (penalty power cutout);16 ->44b (penalty engine shutdown);32 ->44c (you applied the emergency brake);64 ->460 (left a station while loading passengers). In particular4 and32 are distinct native codes even though both labels mention emergency braking. The two retained records in evaluation-paused-02 therefore correspond to the installed labels for emergency brake applied and penalty power cutout. No claim is made that a particular user action caused either record, or that their emission was observed.

Display selects resource443 (mile) or444 (km) according to report+6c, consistent with the marker-derived location. This establishes the display's unit label selection, not independent numerical validation of the interpolation/route conversion.

Resource helper004b1ef4 calls LoadStringA and performs bounded string copying; pass80 verifies its97 instructions/281 bytes against disk/live. Pass79 followed the shared string getter and exported308 callers, much broader than needed; only the relevant getter and previously traced display path were reviewed. No coverage claim follows from that export volume. Later focused function exports should use an interior instruction address where caller expansion is not needed. Installed resource labels are not proof that another localization or mod uses identical text; preserve code and resource IDs alongside friendly labels.

Follow-up: VEHICLE-MOTION-EVALUATION.md resolves car+1c0 as stored acceleration and car+28e as loaded Durability. The earlier unresolved-input wording records the original checkpoint; reference threshold initialization and moving/nonzero evaluation tests remain open.
