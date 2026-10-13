# Simulation clock storage and live timing patches

Native clock object begins at0080acb8. Gameplay loop0048fdd0 explicitly passes that base to00645af0. The update reads dt00828fb4 and independently adds it to float+18 (0080acd0, event elapsed accumulator) and float+1c (0080acd4, day-seconds accumulator). Setter00645d12 writes a supplied starting day-time into+1c, derives integer hour/minute/second, resets+18 to0 and sets0080ace4 to601. This establishes distinct accumulators, not a per-read subtraction of day-time minus start-time.

The update subtracts86400 from+1c on its wrap path, and carries integer seconds/minutes/hours into date fields. Fields+0,+4,+8 are day/month/year; +c,+10,+14 are second/minute/hour. Date validity, initialization origin, leap-year rules, midnight and reload behavior have not been runtime-tested. Do not equate the internal date with the narrative date in an activity description. Save code0049f73c reads these fields, and display0041e7b8 formats the hour/minute/second values. The date fields are candidates, not proof of the intended historical activity date.

Paused read captures/clock-paused-01/clock.json at74600.2734375 finds elapsed800.2717895507812, internal day/month/year3/6/2000 and second/minute/hour20/43/20. The elapsed accumulator differs from day-time minus activity start by about0.001648 seconds. This sample alone cannot assign that difference to native float drift.

In historical PID7160, pass70 finds five instruction-range mismatches in live memory: one call at0048fdd6 and four old instruction spans covering two replacement calls at00645b13 and00645b22. Disk bytes all match the original export. Current NEMT source runtime/timing.h explicitly installs these sites under UnlockFPS. The two captured live adapters at028a0000 and028a0040 match its emitted register-save/address/dt/call/restore sequence, including the distinct +18/+1c clock fields. This is strong provenance for the timing patches, not a byte comparison of the entire loaded DLL.

That source uses separate double remainder accumulators for the two stored float clocks, resets a remainder when its field changes externally, and retains the native caller's stores/calendar work. It also patches the gameplay timing-step call. Therefore the historical PID7160 gameplay probes cannot validate unmodified MSTS timing drift or update precision. No setting or patch was changed. Source reference is C:/codex/repo/NEMT/runtime/timing.h at the existing main baseline5cd5896; live-clock-patches.json preserves the actual adapter bytes and destinations.

pass70:9 functions/469 instructions/1705 bytes, zero disk mismatches, five live mismatching instruction spans. pass71:10/3389/14612, zero disk mismatches, two live mismatches at0048fdd6 and previously observed00494bc1. Do not describe these passes as fully matching live code. The clock update's unaffected instruction ranges and setter match; patch-sensitive additions require the above distinction. The time-event consumer still directly compares its threshold to0080acd0, so retaining that value is preferable to silently substituting a derived elapsed time.

This pass resolves the clock producer and reset relationship statically and adds raw internal calendar and clock-component candidates. Future tests remain: loaded-DLL identity, pause/resume accumulation measurements for both clocks, midnight/calendar transitions, save/reload resets and stock-versus-modified timing comparisons. These findings are local after2978ac2.


## UI restart follow-up, 2026-10-10

SESSION-RESET-FINDINGS.md now validates one normal UI restart resetting elapsed1212.6500244140625to0 and day66012.6484375to64800. Calendar3/6/2000 persists. This supersedes the earlier entirely-unvalidated runtime reset wording for that path only;midnight,saved-game restoration and stock timing remain open.

## Current process context correction, 2026-10-10

The user confirms that the earlier timing patches came from NEMT and that NEMT is not loaded in the current instance, PID12888. Historical pass70/pass71 and adapter captures remain evidence for their own process only; they must not qualify current gameplay as NEMT-patched.

Fresh read-only comparisons of00645af0 and00645d12 cover181 instructions/557 bytes, and0048fdd0 covers156 instructions/751 bytes. All three ranges (337 instructions/1308 bytes total) match both exported and current executable disk bytes with zero live mismatches or read errors. These include the previously patched clock-add and timing-step call sites. Evidence: captures/midnight-clock-native-20261010-01-byte-verification.json and captures/midnight-caller-native-20261010-01-byte-verification.json, with exact sources/provenance in their corresponding directories. This is a bounded code comparison, not an assertion that every process byte was checked. No patch or setting was changed.

Current inventory metadata now distinguishes these process contexts. Native float precision, midnight behavior and calendar provenance still require their own evidence; absence of NEMT alone does not validate them.

## 2026-10-10: normal-speed Explore midnight observation

Completed capture `captures/explore-midnight-20261010-01` contains 22,951 samples, zero read errors and 15 clock-block reread changes. Analysis is reproducible with `analyse_clock_series.py`; `midnight-clock-20261010-summary.json` retains step transitions, initial load discontinuity and rollover separately. Earlier accelerated gameplay is not labelled a proven wall-clock multiplier. User restored normal speed and paused at23:59:41; normal Return to Activity UI resumed the capture.

At UTC02:17:46.776907/02:17:46.877419, day clock86399.953125->0.078125 and native elapsed3599.949951171875->3600.074951171875. Both samples have step0.125, pause0, identical nonnull player/start and stable block rereads. HMS changes23:59:59->00:00:00. Calendar stays3/6/2000, including the following15simulation seconds. The visible static date-carry path is therefore not runtime proof of date advancement in this mode; its relationship to other clock writers remains unresolved. No month-end/leap/save-restoration inference follows.

The derived `session.elapsed_candidate` (day clock minus activity start) becomes -82799.921875 and cannot serve as a general elapsed duration across midnight. The native elapsed field continues forward. Inventory metadata for the day clock, HMS, calendar and derived candidate now reflects this evidence. This supersedes earlier statements that midnight was entirely untested, while preserving historical PID7160/NEMT findings separately from current PID12888.

## 2026-10-10: calendar-carry bypass resolved in inspected update path

The apparent contradiction came from treating00645540 as an ordinary conversion helper. Its assembly is authoritative:006455bb replaces its saved return address with00645c8f, the parent clock-update epilogue. Thus the call at00645b35 skips the legacy delta/HMS/calendar carry code after returning. The decompiled00645af0 listing alone misrepresents reachable behavior at this call.

Helper00645540 first tests clock[-4] (0080acb4). If nonzero, it writes day clock as that float plus native elapsed. It subtracts86400 once when the stored day-clock bits meet the positive86400 threshold, decomposes the result using3600/60 remainders, and writes low16bits of hour/minute/second. Seconds subtract0.5 before FISTP; rounding environment remains a qualification. It does not update date fields. Current start context is82800.0; constants86400,3600,60,0.5 match disk/live. This explains the captured HMS rollover without calendar increment. The two accumulator addresses remain distinct storage, but independent addition is not the complete day-clock producer when this helper's start value is nonzero. Multi-day behavior needs separate testing because subtraction occurs once.

Evidence: clock-helper-20261010/00645540.asm and00645fab.asm;69exported instructions/207bytes match current disk/live with zero mismatches/errors. Dispatch thunk00403f5d also matches disk and jumps00645af0. Constants and bounded dispatch reads are retained under captures/clock-dispatch-20261010-01. Current instance has MSTSBin and no NEMT per user; this on-disk helper is not a historical NEMT runtime patch. No statement about an unmodified original Microsoft executable follows from this build. Direct reference export clock-calendar-references-20261010 preserves known callers/readers but cannot enumerate all indirect object-field writes.
