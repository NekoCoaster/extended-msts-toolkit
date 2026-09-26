# Activity event discovery checkpoint

26 September 2026. Game stayed paused at simulation time74000.0546875.

## Loaded event list

Activity singleton at0x809810 contains event-list sentinel pointer at+0x324 (global0x809b34). Nodes are circular with next+0 and event pointer+8. Native parser0x59c2ed inserts events there; the high-level decompiler incorrectly removes insertion blocks as unreachable, so use its assembly. Save loader0x5902ef independently references this list.

Read-only capture `activity-events-paused-01` finds all three location events matching evegrain.act:

| ID | Tile | X/Z offset | Radius | Requires stop | Outcome |
|---|---|---|---|---|---|
|2|(-12557,14761)|(15.47,194.293)|10|No|Display message|
|3|(-12557,14761)|(-153.183,-804.48)|50|No|Display message|
|0|(-12557,14761)|(-77.4832,-421.09)|99|Yes|Activity success|

Category+4=2, type+8=1, ID+0xc; tile pair+0x6e/+0x72; X/Z+0x76/+0x7a; radius+0x7e; TriggerOnStop+0x82. Location allocation size0x86 is established by0x59d037. Its decompiled output omits subtype reads that are visible in assembly. Native token table associates EventTypeLocation with0x403fa, Activation_Level0x403f6, TriggerOnStop0x403ea. These are parser tokens, not runtime event enums.

Each event has activation level+0x24=1, state+0x20=1, state+0x10=0. Parser initializes these separately and save loading restores them separately. Work-order UI0x458de1 uses+0x10 for action types6..9; that alone does not prove the complete fired/completed semantics for location events. Keep raw labels pending evaluator tracing and an actual transition.

Outcome count+0x66 was1 in each event. Inline outcomes at+0x2a, stride12, correspond to types5(message) and6(success), corroborated by native writer0x59c610 and ACT definitions. The read-only probe bounds the inline capacity to5 inferred from layout. Message payload pointers were read as raw references, not decoded strings in this checkpoint. Success outcome presence is not activity-success state.

## Investigation limits

The initial failure lead0x58ea72 proved to be a generic indexed-object message dispatcher, not an activity-result setter. Do not label its arguments as universal activity end codes. The current NEMT install modifies failure behavior, so later evaluation testing must record those settings.

No event was triggered here. No operational evaluation counter was decoded yet. Future work: event evaluator/context, activation changes, time/action event extensions, outcome payloads, actual completion/failure result, speed/error counters and elapsed evaluation times. Readable loaded definitions are useful metadata, but not proof of changing telemetry.

`read_activity.py` preserves exact readers and bounded raw observations. `activity-fields.json` adds14 candidates with per-field limitations. Passes17–23 retain parser, writer, save loader and UI evidence. Do not trust high-level decompiler omissions without comparing assembly.

Follow-up: ACTIVITY-EVALUATOR-FINDINGS.md resolves the native activation gate, mutable activation/reset baseline, trigger latch and reversal handling, and adds two activity outcome flags. Earlier raw-label uncertainty above is historical; actual event-firing transitions remain untested.
