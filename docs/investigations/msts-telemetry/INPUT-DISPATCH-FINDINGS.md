# Input dispatch, action state and buffered records

This refines the999-candidate input checkpoint. Pass195 exports4functions612instructions1962bytes matching disk. Two live instruction spans at006bae0e/006bae12 differ: the original6bytes have an existing E9 jump and padding. The read-only snapshot preserves the jump target and64-byte fingerprint, but does not attribute or audit its complete behavior. Other exported instructions match. Native disk dispatch semantics must therefore not be promoted to complete live-equivalence or a successful key-dispatch test.

## Listener and action corrections

In006bad60 listener mask+0c bit0x100 selects a function callback. When clear, listener+0 is instead a writable value destination; native code stores the action result there. The research probe never calls or writes either type. The initial probe's `callback` property was an overgeneralized name. New captures use `target` and `target_kind`; old raw captures remain unchanged. The first snapshot's six references all have bit0x100 set, so its observed single target remains a callback, but the general layout must retain the distinction.

Action+0c is event-type-dependent. Type1 events update a count on presses/releases; other types store the event value. It is not universally a boolean, key count or analog axis. The dispatcher also checks binding flags, action state flags, listener flags/masks and modifier predicates. Action+10 is a16-bit filter word, compared toFFFF when global mode equals2. Action+12 holds state flags. The prior32-bit `action_flags` read combined these words; inventory semantics now split the filter from the16-bit flags, while old raw evidence remains intact. No full mode enum or command-eligibility model is claimed.

The current five action objects have event value0 and filter0; state flags are0201 for one and0200 for four. These observations do not establish all flag meanings or successful input processing. Source flags and callback identities are context-dependent, not universal gameplay action names.

## Keyboard producer and event reader

Live input vtables identify keyboard update00707990, second-device update00707d10, and shared next-event method00708ad0. These addresses were missing as defined functions in the analysis database; pass196's function export returned zero functions and byte verification correctly refused to run. It is retained as a failed navigation method, not a validation result.

Bounded linear pass197 covers00707990..00707d0f:318instructions896bytes match disk/live. The update routine clears input+14/+18 on its ordinary reset path; a flag branch preserves them. It stores events at buffer[input+c]+count[input+18]*16 while count is below capacity[input+10]. It sets event word0 to native scan OR00010000, word1 to the source data's high-bit-derived0/1, and copies two additional source words to+8/+c. The corresponding bit in input+24 is set/cleared. A separate refresh path handles238 keyboard entries. This confirms the held-bit producer without a synthetic input experiment.

Pass198 is a bounded128-byte range (65instructions) matching disk/live. Getter00708ad0 compares cursor[input+14] to count[input+18], returns no event when equal, otherwise returns buffer+cursor*16 and increments cursor. Range exports include padding/neighbour instructions; they do not certify function coverage beyond inspected logic. No event-reader method was called by a probe.

The snapshot `input-dispatch-buffer-paused-01` has keyboard capacity12,cursor0,count0 and a stable header. No stale buffer tail is dereferenced. Native extra event words remain raw; timestamp/sequence units are not asserted here. Periodic observation cannot guarantee complete events because polling resets and consumes this transient buffer. Buffer capacity is not a measured loss rate or an event history length. Dynamic nonempty/press/release tests remain open.

Six candidates add action value/filter and keyboard buffer capacity/cursor/count/records. Inventory1005. Existing listener and flags metadata are corrected rather than duplicated. All observations remain paused74360.5859375; no game controls, memory writes, assets or saves changed. The live dispatcher patch, non-atomic sampling and untested transitions remain explicit limits.
