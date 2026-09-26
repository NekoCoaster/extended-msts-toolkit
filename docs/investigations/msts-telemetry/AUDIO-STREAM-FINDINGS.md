# Per-stream audio runtime telemetry

This extends the existing receiver-list work into stream runtime records. Pass189 exports six functions,2645 instructions,8915 bytes; every exported instruction matches current disk and PID7160. The consumer0053f153, predicate005384fe and enqueue0053e2d2 supply evidence; raw decompilation is not a portable API.

## Layout and semantics

Receiver+14 points to stream states with stride1c; loaded definition+14 points to stream definitions with stride20 and count at definition+10. A state contains backend pointer0, linked pending-record head4, cached volume/frequency curve results8/c, two trigger-enable words10/14 and a volume factor18. The consumer tests enable bit `(index % 32)` in word `(index / 32)`. Current configured counts range1..33; the probe reads two words, not an arbitrary mask array.

The consumer combines cached volume with receiver/global factors and an optional curve before its backend-interface call. It separately clamps a frequency parameter to100..100000. Neither cache is a measurement of final hardware output. Skipped curve branches may leave cached values stale. Backend+4 has flags;005384fe returns false for null and otherwise tests bit0x2. This is a native predicate, not proof of audibility or successful playback. Backend+30/+74 hold buffer/spatial interface pointers; the probe reads their identities and never invokes them.

The consumer and enqueue routine traverse the pending chain from state+4 through node+8 to null. The probe retains each node's first12 raw bytes; payload identities, waveform names, durations and action types remain undecoded. A completed traversal yields a candidate record count, not an audio-duration backlog. On condition changes the consumer can replace the backend pointer. Backend lock+78 is observed twice without acquiring it; zeros and stable rereads do not exclude intervening changes, removal or ABA.

## Live evidence and retained limit

Two snapshots at paused dayclock74360.5859375 find33 receivers and67 configured stream states;50 streams join inspected player-car sound handles, none join physical AI. The remaining17 streams have no association through those inspected handles; unassociated sources are not automatically AI. These stream counts are distinct from receiver counts.

The first snapshot preserves one combined cycle/bound failure for traf_m_m.sms stream2. The corrected probe records partial traversal rather than losing it and separately identifies the stop reason. The second snapshot has zero read errors: that stream reaches256 distinct nodes with a nonnull successor, hitting the research bound, not a detected cycle. Its full queue count remains unavailable. The other66 queues terminate, containing six linked records in total. No attempt was made to exhaust an unbounded chain.

All67 second-snapshot state/definition/owner and observed-link rereads agree, with lock observations0/0. These are sequential stability checks only. Seven backend bit2 predicates are true; only one of those has a buffer-interface pointer. Across all67 streams there are17 buffer and3 spatial interface pointers. This directly illustrates why native flags or allocation alone must not be relabelled audible playback.

`read_audio_streams.py` preserves probe copies/hashes with captures; `analyse_audio_streams.py` reproduces the summary. The first failure and corrected capture remain separate. No gameplay controls, process writes, audio calls, asset edits or save changes occurred. Eleven candidates (ten direct and one derived) bring the inventory to982. AI audio lifecycle, waveform/command payload decoding, actual output status and normal-playback transitions remain open.
