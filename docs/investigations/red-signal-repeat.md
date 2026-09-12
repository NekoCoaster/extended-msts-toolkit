# Repeated red-signal warnings

The first host test confirmed that the bypass allows continued driving after dismissal, but required dismissing the Windows notification twice. Alpha.3 replaces that Windows notification with a native MSTS alert; the revised native alert and repeat suppression subsequently passed host validation.

## Confirmed instruction behavior

The monitor at `0x5864ee` walks the list rooted at `0x809f1c`. For entries of type 1 or 2, it tests a float at entry offset `0x10` against zero, a float at offset `0x04` against 15, and bit `0x2000` on the referenced object at offset `0x14`. When those conditions match, it sets the controller's `0x100` failure bit at offset `0x378` and returns. It does not consume the list entry or remember that a notification was already shown.

The failure dispatcher at `0x586293` subsequently sees that bit and requests GUI method `0x24`, reason 2, through the call at `0x586449`. The current bypass clears the bit before displaying its notification. The monitor can therefore set it again while a matching entry remains eligible. This establishes a repeat mechanism consistent with the two dismissals; it does not establish that both observed warnings came from the same entry.

The threshold resembles a proximity condition, but the meaning and units of the float must be traced before calling it a 15-metre trigger zone. Multiple eligible entries or two distinct signals also remain possible explanations for the observed pair of warnings.

## Alpha.3 implementation

The runtime wraps the existing monitor thunk at `0x4013c5`, preserving the original scan and unrelated failure conditions. It groups eligible entries by their referenced object at offset `0x14`, rather than their temporary list node. Already-notified identities remain remembered while present in the list, including an aspect change. Once absent, a subsequent appearance can warn again. Simultaneous new entries share one notice. The cache is bounded to 64 identities with at most 256 list visits; there are no per-frame allocations, disk writes or wall-clock cooldowns.

The initialization thunk at `0x403ecc` clears this state before native list initialization. A controller/list-root change also resets it. Unexpected list bounds leave the native failure flag untouched instead of clearing it without a complete scan.

Reason `0x1c` in the existing GUI dispatcher creates an ALERT with one OK button, originally used for the non-ending “You are not permitted to delete the current Activity” notification. The runtime uses that presentation path, replaces `s_dlg_text` through the native text setter, and pauses through the native pause function. No GUI asset is modified. The standard `s_dlg_b3` widget sends reason 19 (`0x13`) on dismissal. With the activity-ending flags clear, that branch hides the popup and resumes instead of ending the activity. An already-active native popup defers the new notice.

The text says “Activity failed -- ignored red light.” This is a gameplay notification; the feature does not implement a new persistent scoring/failure record. The native widget names and OK action are required. Addons that remove or repurpose these controls need compatibility testing.

## Validation boundary

Automated checks execute the actual x86 notification adapter 10,000 times and cover repeated monitoring, duplicate referenced objects, a later signal, aspect changes, leaving and reapproaching, activity initialization, deferred notices and preservation of other failure bits. Native GUI calls are mocked in these tests: they do not prove on-screen rendering, pause/resume or real-route signal identity behavior.

Host testing of the earlier Windows-dialog build confirmed continued driving but observed two notices. A subsequent alpha.3 host test confirmed the native-dialog build working well. Use [Train Rescue checks](quality-host-test.md) for regression testing.
