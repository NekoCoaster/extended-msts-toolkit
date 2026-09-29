# Executable identification and historical patch locations

This record preserves the inherited patch locations and earlier permanent-patcher method. NEMT requires clean supported on-disk bytes and applies selected changes only in process memory; see the [native architecture](native-runtime.md).

The supported executable family is the exact MSTS Bin 1.8.052113 image used during this investigation. Development fixture filenames included `train.vanilla1.4.exe`; that filename alone is not a version identifier. Support does not extend to every stock MSTS 1.4 executable.

All accepted images are 4,091,953 bytes, PE32, with preferred image base `0x400000`. Identification normalizes only the two known feature patches and the LAA header bit, then checks the entire image's SHA-256. An unknown modification is rejected before any write.

| Normalized build | SHA-256 |
|---|---|
| Base | `69218fce876298c684a2140c7d3925a452c47bb10037ffd8c491f65c5c0c6e7a` |
| Widescreen | `1b041ecf4b2d2a7306218efa1d7418fd87dc21dc4b2d00056cb5749084fe55a4` |

The LAA flag is bit `0x20` at file offset `0x116`. It is normalized for identification, never changed by the derailment patcher. This gives four supported combinations: base, base + LAA, widescreen, and widescreen + LAA. The LAA-only test fixture was derived by setting this known bit.

## Remove the derailment activity-end event

| File offset | Preferred virtual address | Original bytes | Enabled bytes |
|---|---|---|---|
| `0x1862DC` | `0x5862DC` | `74 16` | `EB 28` |

The activity checker `0x586293` tests derailment state at activity object + `0x378`, bit `0x2`. A timer at + `0x3B4` normally accumulates simulation time and dispatches the derailment end event after approximately 20 seconds. An alternative immediate-dispatch branch exists in the assembly. The patch skips that dispatch path; it does not merely hide a string or substitute a very large timeout.

Physical derailment flags, vehicle motion, and the pause menu remain native. The original priority between failure conditions is preserved: this is not a general guarantee that every other failure will still be evaluated during a derailment. A synthetic fusible-plug failure in a non-derailed activity still dispatched with this patch enabled.

## Unlock derailment cameras

| File offset | Preferred virtual address | Original bytes | Enabled bytes |
|---|---|---|---|
| `0x11C98C` | `0x51C98C` | `0F 84 55 03 00 00` | `90 90 90 90 90 90` |

The selector at `0x51C958` checks the camera object's type at `[0x7C2A88] + 0x11C`. Type 6 is the derailment camera. The patched conditional jump previously rejected a camera change when this type was selected. Removing the jump allows the existing selection routines to run.

Cab, exterior, passenger and coupler views were observed after derailment. Trackside selection succeeded but its camera could be inside terrain. Unlocking a mode does not guarantee comfortable placement around a rotated or scattered consist.

Since version 1.2.1, this same option additionally suppresses
the camera-only derail notification at `0x51D4E1`: the verified nine-byte prologue
`55 8B EC 81 EC B4 00 00 00` becomes `C3` plus eight NOPs. The notification
selects camera type 6 and then initializes that camera; skipping only its selector
call would leave the remainder relying on a possibly uninitialized camera.
Skipping the whole camera notification preserves the current view, including
FPV, without changing vehicle/train derail flags, wake-up, or physics in its
caller `0x62E017`. The replacement and original camera-unlock patch share the
existing verified hook transaction. Neither is installed when the option is off.
Feature-combination and native derail-routine tests passed. Subsequent in-game
test reports accepted the camera-preservation behavior; see the
[development chronology](walking-development.md).

## File safety

Both options can be restored independently. Only their exact known bytes are changed; widescreen and LAA remain intact. The patcher must refuse to replace a running target, check that the selected file has not changed, preserve a verified backup, prepare a verified temporary image, and replace the target atomically. A drive letter is not an executable compatibility criterion.

Virtual addresses and file offsets are not interchangeable for arbitrary sections. The relationships above were checked for this executable's code section. Zero-initialized runtime globals have no corresponding patchable file bytes.
# Toolkit migration note

The following MEDS research documents the recognized image and byte locations. NEMT applies enabled feature bytes in process memory. Its installer only restores known old MEDS disk patches during migration; normal configuration does not enable disk patches.
