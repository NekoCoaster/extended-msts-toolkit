# Location event firing and persistent latch

2026-10-10, Tokyo-Hakone Passenger Activity Tutorial, supported executable PID12888. External QUERY_LIMITED_INFORMATION | VM_READ sampling plus normal keyboard/mouse gameplay; no assets or saves changed.

## Observed transition

Event13 (Projected Speed) is a location event with radius10m, activation1, TriggerOnStop0, reversible0 and one type5 message outcome. Its definition in `C:/MSTS/ROUTES/JAPAN1/ACTIVITIES/tokyohakonetutorial.act` matches the loaded event. Starting stopped at horizontal distance10.3581873701m, the player was advanced slowly across the radius and then stopped after leaving it.

| Observation | Simulation seconds | Reconstructed distance | Predicate / native latch |
|---|---|---|---|
| Last outside sample before entry |65269.3984375|10.0423252845m|false /0|
| First inside sample |65269.5234375|9.9813057685m|true /0|
| First latched sample, message pause |65269.6484375|9.9147212153m|true /1|
| Last inside sample before exit |65278.8984375|9.7999385443m|true /1|
| First outside sample after exit |65279.0234375|10.2639482078m|false /1|
| Final stopped and paused state |65311.3984375|79.4341899143m|false /1|

The UI displayed the Projected Speed tutorial message at18:07:49; its text matched the fixture. Dismissing it resumed the simulation. This establishes a representative message outcome and a non-reversible latch remaining set outside the trigger region. It does not establish an activity-success result. Both activity evaluation-stop+348 and outcome-success+34c remained0.

The one sampled inside-but-unlatched state is evidence that a reconstructed present condition need not equal the native latch at that observation. It is not a universal one-frame latency guarantee: reads are sequential, and evaluator versus movement ordering was not instruction-traced. Near-boundary calculations retain float32 stores but do not fully emulate x87 arithmetic.

## Reproduction and checks

`read_event_series.py` records reconstructed location conditions, first-car geometry, speed, clock/pause, a second event-list read and activity result flags. Run `python analyse_event_transition.py` against retained `captures/tokyo-event-transition-20261010-01/samples.jsonl`; final totals and transition samples are in `event-transition-20261010-summary.json`. The baseline is `captures/tokyo-events-baseline-20261010-01/activity.json`. UI observation and fixture hash are retained in the transition capture. A stable sentinel does not verify every list node or exclude reuse; paused reads are not proof of an atomic snapshot.

Historical exports of0059a7d3,0059b76f,0059ae8e 0059b146 and0059b24c were copied with provenance into `captures/event-transition-native-20261010-01`. Fresh verification covers300exported instructions/1020bytes with0disk/live mismatches and0read errors; report `captures/event-transition-native-20261010-01-byte-verification.json`. This is exported-range verification, not fresh whole-function recovery. The evaluator latches an enabled predicate, invokes outcomes, and only reevaluates a set latch for reversal when reversible+6a is nonzero. Outcome5 dispatches the message; outcomes6/7 set separate activity result fields.

## Scope still open

Baseline snapshot contains other set latches and reduced activation levels, but their transitions were not captured here. Positive/negative activation changes, reversible-event clearing, stop-required boundary firing, other time/action predicates and actual success/failure consumers remain separate validation gaps. The broader discovery goal remains incomplete. Player is paused, speed0, throttle0, emergency brake applied.

## Independent time-event transition

The same series captures time event45 (Late for Gotokuji) latch0 at simulation65267.8984375/event-clock467.8999938964844, then latch1 at65268.0234375/event-clock468.0249938964844. Activation remains1; its outcome count is0. This event records a condition for later evaluation text; it does not display a message or assert activity failure here.

A separate paused read, `captures/tokyo-time-thresholds-20261010-01/time-events.json`, confirms category/type0/0 and stored float threshold468 at event+6e, matching ACT Time(468). Native0059b24c uses the strict comparison threshold<elapsed accumulator0080acd0. Fourteen time-event thresholds were read; event48 remains unlatched at threshold618 while elapsed is about511.4. Thresholds were read after the transition, not atomically alongside it; fixture provenance and native consumer corroborate the interpretation. `read_time_events.py` preserves the bounded subtype reader. No reset, exact equality edge, negative activation or stock timing precision claim; installed NEMT timing differences documented in CLOCK-FINDINGS remain applicable.
