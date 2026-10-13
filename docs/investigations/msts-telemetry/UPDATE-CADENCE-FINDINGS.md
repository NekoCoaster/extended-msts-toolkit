# Bounded pause/resume experiment

The existing Grain Train Through the Night session was resumed through the actual Escape menu, with emergency brake left applied, then paused again. No remote function calls, process writes, asset edits or save were used. The player stayed stopped and ended paused at sim74548.40625, with23 cars and zero derail flags.

capture_update_cadence.py recorded587 external samples over60 wall seconds, zero read errors. Raw evidence and exact script dependencies are in captures/update-cadence-01; analyse_update_cadence.py reproduces update-cadence-summary.json.

| Phase | Samples | Wall span within phase | Simulation delta | train+d6 delta |
|---|---:|---:|---:|---:|
| Initial paused |144|14.632s|0|0|
| Running, stationary player |223|22.729s|22.734375s|22.73516845703125s|
| Final paused |220|22.422s|0|0|

The train+d6 accumulator changed across all222 consecutive running sample pairs and across none of the paused pairs. Native00608800 adds simulation delta[828fb4] to+d6 and recalculates consist aggregates in the same function. This provides runtime evidence of repeated callbacks during ordinary running, rather than initialization-only execution. Differences of roughly0.0008s over this interval are consistent with float storage/sampling; they are not an exact callback count. External target cadence was0.1s and27 samples crossed a simulation step.

Player speed was exactly0 throughout. Definition mass/length totals, train+da distance candidate, selected sound region and all audio records were unchanged. Default region0 still has its handles and bypasses the timestamp-expiry rule, so this is NOT a test of non-default audio expiry or playback. All three service effective caps exactly matched the independent selector at every sample; none changed. AI2 remained represented as a retained service, not an active physical train; no claim of AI movement comes from this capture.

The run establishes pause versus running behavior for the observed train accumulator and repeated aggregate-callback execution. It does not establish callback rate above the sample rate, physical AI cadence, post-coupling updates, speedpost crossing, resource changes, or audio-region transitions. Those tests remain open. Inventory remains768; this checkpoint strengthens existing lifecycle evidence instead of counting the same semantic fields again.
