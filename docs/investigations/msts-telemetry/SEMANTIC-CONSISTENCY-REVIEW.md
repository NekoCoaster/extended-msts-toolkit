# Scoped inventory consistency review

This is a correction of five current candidate records, not an inventory-wide semantic approval or goal completion. Historical findings and raw captures remain unchanged. No candidates are ranked or removed.

| Candidate | Stale current statement | Evidence-backed correction |
|---|---|---|
| engine.vigilance_monitor_state | Countdown/action transitions unvalidated | monitor-enabled-events.json records quarter-step countdown changes, alarm/action edges and brake response. ENGINE-MONITOR-FINDINGS.md qualifies one differing reread; no atomicity claim. Complete reload restoration and acknowledgement remain open. |
| session.vigilance_update_suppressed | Successful toggle/initialization unvalidated | Enabled run records0; captures/monitor-options-restored-01/gates.json records1 after restoring General Options and restarting activity. Exact write timing and process-restart persistence remain open. |
| session.aws_update_suppressed | Same stale gate lifecycle | Same paired gate observations establish settings-state changes, not AWS intervention or successful Ctrl+numpad4 dispatch. |
| car.shape_node_transform | Cadence/reload untested; transforms not reread | Moving capture validates representative player/AI type5 changes and paused stability with repeated matrix reads. Initial node probe did not reread. Exact frame cadence and reload lifetime remain open. |
| car.wheel_transform_groups | Moving cadence untested | Moving capture validates representative player/AI type4 wheel changes and paused stability. Context reread differences remain retained; exact frame cadence and lifecycle remain open. |

Sources reviewed: generated inventory records, monitor-enabled-events.json, wheel-matrix-player-ai-01-summary.json, and the associated retained raw captures reprocessed with their existing analyzers. Structural audit alone cannot prove these meanings. The coverage review also updates its evidence count and fixture population and removes an obsolete next-step instruction to seek the already-completed UI activation method.

Remaining review scope includes earlier force, animation-rate, serializer and AI metadata and all other candidates. Append-only evidence updates can leave old limitations in current records; each apparent contradiction must be checked against its original experiment scope before revision. Unknowns must not be silently upgraded to verified support.
