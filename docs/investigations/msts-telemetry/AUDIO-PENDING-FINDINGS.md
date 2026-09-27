# Pending audio record payloads

Pass190 verifies5functions841instructions2608bytes; pass191 verifies11functions1335instructions4254bytes; pass192 verifies5functions577instructions1794bytes. All exported instruction ranges match current disk and PID7160. These exports refine the earlier stream findings, not actual output measurement.

## Typed records and sample identity

0053e203 allocates12bytes, initializes kind byte0=1, stores the sample-reference object at+4, caller byte arguments at+1/+3 and clears+2. Its call in0053de14 passes the selected entry's first pointer inECX and second word's low byte inEDX. The next link is+8. 0053e55a instead constructs kind2 with a different+4 payload. 0053e2d2 builds a nested structure for the multi-element branch and rewires links. Consequently type2+4 cannot be treated as a sample-reference object. The current probe leaves it opaque and does not enumerate its nested records.

0053dfa5 selects an8-byte entry using receiver trigger state. Its branches distinguish random-style history-mask selection and sequential index progression. This supports a requested sample identity but does not establish completed playback or a universal sound-event name. Full selection-state telemetry is not yet added.

005416cc checks/loads the sample-reference's resource+14 and increments+4 on its successful path, retaining a caller parameter at+c. It forms a path from two strings in the pair at+8: directory pointer at pair+0 and name pointer at pair+4. The probe captures these bounded UTF16 strings and the resource identity. The+4 counter is a load/acquisition reference counter candidate; release/reset and complete accounting remain untraced. It must not be presented as times played, queue length or number of audible users. Path labels are not independently verified filesystem identity; no file was opened based on process strings.

## Native flag refinement

00537e42 can set backend flag0x2 after starting its software processing callback. When backend flag0x10 is set, it skips the buffer playback call and sets the local result to success. This explains a concrete native path for flag0x2 without a buffer pointer. It does not establish the meaning of every flag, prove actual output, or measure silence. 00537e0f clears pending-record byte2 over the top-level chain; other writers and byte meanings remain open.

## Snapshot

`audio-pending-paused-01` reads262 top-level nodes:258kind1 and4kind2. All node rereads match; five distinct kind1 sample-reference objects have stable header and path-pair rereads. No node/read errors occur. The same traf_m_m.sms stream2 reaches the256-node bound with a nonnull successor, so traversal is still incomplete.

The five labels are obj_veh3_moving.wav, obj_veh2_moving.wav, obj_veh2_random_b.wav, obj_veh4_random_a.wav and obj_veh3_random_b.wav under loaded directory C:/MSTS/Sound/. Their stored acquisition counters are1,1,144,143,143. These counters cannot be reconciled to a partial top-level traversal alone, especially with nested records and other references unexamined. Nonzero resource pointers do not establish current playback. No AI train association follows from vehicle-like filenames.

Six additional candidates preserve kind, three raw control bytes, typed sample-reference identity, path parts, acquisition-counter candidate and loaded-resource identity. Inventory988. Game time remains paused74360.5859375. No game controls, process writes, asset edits or save changes occurred; all probes use query/read-only access. Further work includes typed nested payloads, command/selection semantics, releases/lifetimes, actual output and AI association. Broader requirements remain open.
