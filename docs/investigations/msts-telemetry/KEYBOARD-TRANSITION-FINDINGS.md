# Short Shift press: events observed, held state missed

The simulator was visually confirmed at the pause dialog in the stationary Dash9 cab. A30-second read-only capture observed native keyboard bits and the transient event buffer. During the series exactly one Shift_L press was sent using the computer-use skill. The immediate screenshot still showed the pause dialog. No gameplay command, resume, asset write or save action was requested.

`keyboard-shift-paused-01` preserves5394samples,zero read errors. Every sample reports pause1 and dayclock74360.5859375. All bitset/header rereads agree. Maximum sampled read window is0.000796seconds and maximum observed sample gap0.006897300016seconds; these are observational timing figures, not an isolated overhead benchmark or guaranteed future sampling rate.

Three samples contain the same two16-byte records. Their first word65578 is0001002a (native type1 and scan2a), matching the requested left Shift. Values are1 and0, corroborating the producer's press/release encoding. The remaining raw words are386589937 with888/889; their units and external API semantics remain unasserted. Repeated observations are not six input events. The records are retained once each in the analysis summary with first/last observation times.

All5394held-state bitsets are zero: the brief press/release was not observed as a held state. This does not contradict the buffered records. It demonstrates why a sampled held-key bitset cannot reconstruct all input events. Likewise these two observed events do not establish lossless buffer capture, exact event timing, full keyboard/analog support or successful gameplay-command dispatch. The previously fingerprinted live dispatcher detour remains a limit on blanket equivalence to disk code.

All three nonempty observations have cursor2,count2,capacity12: the two records had already been consumed by the native event reader and remained in the buffer. They were not pending events at those sampled instants. Snapshotting count records includes both consumed and unconsumed entries; cursor identifies the boundary, subject to non-atomicity.

This strengthens existing candidates rather than adding fields: inventory remains1005. A nonzero held interval and gameplay action transition are still unvalidated. Probe copies/hashes, raw samples and UI outcome are preserved through the local capture and this note. All capture jobs ended; game remains paused.
