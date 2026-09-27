# Service efficiency source and installed clamp

005a6b1d writes service+208 from one of two sources. When service+34 is nonzero it copies selected-record+24 and jumps directly to return; that branch bypasses both baseline clamps. When null, it copies baseline service+204, calls004069aa and applies an upper limit of1. Selected-record identity and baseline asset-parser assignment remain unresolved, so this is not yet a complete Efficiency asset binding.

Assembly matters:004069aa compares the copied value against float004069d2 (0.004999999888241291), stores bit pattern3ba3d70a (the same float) if below, then adds1b to its return address. Return005a6b5b becomes005a6b76, bypassing the apparent0.05 minimum in the decompiler. The baseline branch therefore clamps ordinary finite inputs to approximately[0.005,1] in this installed image. This is not a universal stock-version rule. Nonfinite semantics and selected-record out-of-range behavior are not experimentally tested.

Capture service-efficiency-paused-01 at73903.4375 observes player and both AI services. All have baseline204=0.75, effective208=0.75 and null selected records; all pointer checks pass. Constants004069d2,00758434 and00753c38 match disk/live (approximately0.005,0.05,1). It corroborates the baseline source for these services, not selected-record override execution or clamp-boundary transitions.

Activation005a67af sets service138 to the smaller of service28 and1f8 after successful path initialization. Sampled player28 is11.1759996414m/s, AI values0; configured caps33.08095932,33.08095932,32.63389969 respectively. Exact start-speed/configured-cap parser binding is still open. This evidence should not rename those fields as independently verified asset values.

Pass140:549 instructions/2065 bytes; pass142:1959/8297; pass143:50/177; all exported ranges match disk/live. Pass141 is a literal destination-offset scan used to find candidate writers, not exhaustive pointer-aware analysis; unrelated matching offsets are preserved. The helper is already present in disk and live image; no patch was installed in this investigation. Game remains paused at the existing red-signal failure alert.

## Ordered service records and selection

005a51ad enumerates circular list sentinel=[service+30], node next+0 and record pointer+8. Callers supply service+1d0 as the comparison progress and store the selected result into service+34. For each record,005a55e4 resolves record+0 as a track item ID using lookup005b7c21 with kind3, then resolves a paired item using first-item+34. It returns the absolute difference of the two items' float+c values as a length-like quantity. Selector adjustment=(that quantity-service124)*0.5; a negative sign bit replaces it with15. The first record satisfying supplied progress < record14-adjustment is returned, otherwise null. Record24 is the effective-efficiency override source established above.

The helper can return without writing all outputs when the global item table or either lookup is absent. The selector does not visibly initialize its length output before the call. Do not reconstruct this path for missing references as if it had a defined zero length. Record loader, order guarantees, exact track-item labels, units and schedule timestamp fields remain open; this evidence is insufficient to call every raw word a timetable field.

service-records-paused-01 reads all three current services at unchanged73903.4375: all lists empty, selected34 and previous38 null, sentinel checks stable. Empty lists explain the observed baseline efficiency branch but do not validate nonempty record selection or override transitions. The AI progress candidate1d0 is17608.263671875; player and later service read0. Record data requires a suitable populated activity for runtime validation.

Pass144:1981 instructions/8332 bytes; pass145:129/367; zero disk/live mismatches or read errors. read_service_records.py preserves bounded structural extraction with raw words explicitly provisional. This adds an ordered-record-list candidate without manufacturing confirmed schedule timestamps from empty data.

## Loader and station-stop identity

Service constructor005a31d4 clears250 bytes and initializes baseline204 to0.75. Service loader005a1b1a opens routes/.../SERVICES/...srv and reads token40411 directly into service204. Native label table796b10 identifies40411 as Efficiency; the pointer/token pair matches disk/live. This resolves the baseline's service-file binding, while activity-specific overrides are a separate loader path.

Loader005a2744 processes TimeTable40407 content. StationStop4040a allocates and zeroes a28-byte record and defaults record24 to0.75 before005a2abc parses PlatformStartID4040b into record0, DistanceDownPath40410 into record14, and SkipCount40412 into a temporary integer then stores its low16 bits at record1c. Record1e is cleared after success. Copy routine005a2dc3 duplicates each record as28 bytes into a new list. The runtime list can therefore be identified as station-stop records, though activity merge/removal branches and per-stop efficiency assignment still need tracing. Arrival/departure timestamp offsets are not established by this loader.

service-token-map.json preserves eight disk/live label-token pairs and SHA256 provenance for evegrain.srv and morningmaryland.act. The installed Morning in Maryland activity declares two player platforms962/1510 at path distances215.863/30323.6 and efficiency0.75/0.289063, with separate arrival/departure declarations. It is a concrete nonempty test candidate, not a completed runtime comparison. Existing grain-service lists remain empty.

Pass1472426 instructions/9246 bytes, pass148808/2925, pass149389/1233 all match disk/live. Pass146 is another exploratory literal-offset scan, not an exhaustive writer map. Parser destinations above were checked against assembly because005a2abc has poor decompiler stack recovery. No original assets or gameplay state changed.

## Populated Morning in Maryland runtime sample

Loaded Northeast Corridor / Morning in Maryland through the UI, then paused at28809.5703125, stationary with brakes applied. maryland-records-paused-01 and maryland-efficiency-paused-01 contain three services: player has two station-stop records; both AI lists are empty. All sentinel/source-pointer checks pass. Player selected34 points to the first record; previous38 remains null. Baseline204, effective208 and selected-record24 are0.75. The second record contains0.2890630066394806, the exact float32 conversion of the activity's0.289063; selection of that second record is not yet observed.

analyse_maryland_records.py compares original asset declarations and retains hashes. Platform IDs962/1510 and uint16 SkipCount0/1 match. Live distances215.86279296875/30323.611328125 differ from declared215.863/30323.6 by approximately-0.000207m/+0.011328m. Thus record14 must not be described as an exact unchanged asset copy; recalculation/writer tracing remains open.

Float interpretations of record04 match declared ArrivalTime28801/30607, and record0c match DepartTime28811/30627. Record08 reads28801 for the first and0 for the second. These are timestamp candidates, not confirmed scheduled-versus-actual semantics from one numerical match. No timestamp candidates are promoted to verified fields yet. Record1e is nonzero on the first despite its loader default0, identifying another state transition to trace.

The prior grain failure alert was dismissed before exiting; gameplay briefly resumed, so the old frozen state must not be treated as persistent after that UI action. Its raw evidence remains unchanged. No save or installed asset was overwritten. Next trace timestamp/state writers and station boarding or selection transitions in this activity; broader AI/infrastructure scope remains open.
