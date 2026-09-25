# Activity manager error during mouse initialization

Host investigation, 20 September 2026. This is diagnostic evidence and a proposed integration direction, not a shipped runtime fix.

## Observed failure

A byte-identical disposable copy of the host MSTS installation failed to load the Hisatsu introductory ride with “Failed to initialize Activity manager.” Replacing and restoring the Basic Fixes TRAINSET payload both produced the failure. An administrator run also failed. The installer is not established as its cause.

Frida observation found successful activity initialization but a later failed input initialization. No return values were overridden. The tested train.exe SHA-256 was `2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843`; addresses below describe that image at base `0x400000` and must not be assumed valid for another executable.

| Site | Observation |
|---|---|
| `0x587cf3` | Initial activity setup returns 1; object at `0x809810` has first DWORD 1 |
| `0x495b89`, `0x495ba4` | Subsequent activity calls return 1 |
| `0x495be4` | Input initializer returns 0; selected error message remains 969 |
| `0x4a40cb` → `0x4a8178` → `0x6d3010` | Input initialization reaches mouse binding setup |
| `0x6ba3c0` / `0x6bbac0` | `PtrMouseX` registration fails; no mouse device is found |
| `0x709400` | DirectInput mouse enumeration returns S_OK with no callbacks |

A standalone x86 C probe compiled with the existing TinyCC toolchain, outside the repository, reproduced zero mouse devices and `CreateDevice(GUID_SysMouse) = 0x80040154`. It also reproduced when launched normally through Explorer. System metrics reported mouse present=0, buttons=0, wheel=0. A present-device query found no Mouse-class devices. This isolates the observed problem from TRAINSET parsing and from Frida instrumentation.

The error text is misleading because the caller does not select a distinct input error after selecting the activity error. “Class not registered” from the standalone mouse probe is not proof of damaged registry registration; the system currently exposes no mouse. The existing 32-bit DirectInputDevice COM registration and dinput.dll signature were verified.

## Verification limits

Earlier primary and backup rides successfully loaded, but no mouse-presence measurements accompanied them. A later instrumented primary comparison exited unexpectedly and is inconclusive. The user confirmed remote access without a physical mouse. Do not claim every earlier installer-associated failure had the same cause solely from this reproduction.

The inspected Basic Fixes 1.2 package contains 11 complete replacement TRAINSET files. Static installer inspection found its MSTS install-path write flag disabled and no custom registry-operation block. It reads the MSTS Path value to select a destination. This is static evidence, not a captured historical registry diff.

## Possible NEMT integration

### Successful temporary experiment

In the disposable copy only, a Frida hook scoped to callers inside system DINPUT.dll translated zero `GetSystemMetrics(SM_MOUSEPRESENT)` to 1 and zero `SM_CMOUSEBUTTONS` to 3. Other metrics/callers remained unchanged. This enabled the actual Windows mouse-device initialization rather than bypassing an MSTS initializer. The Hisatsu introduction loaded and ran, and keyboard `2` switched to exterior view. A second launch with all 11 Basic Fixes payload files present (hash-verified) also loaded and ran.

The host's signed 32-bit DINPUT.dll was separately inspected: system-mouse creation directly returns `0x80040154` when `SM_MOUSEPRESENT` is zero. This explains the apparently unrelated class-registration error.

This is a candidate for a narrowly scoped remote/headless compatibility feature. It is not yet shipped or fully validated: mouse cab interaction, remote drag/buttons, device reconnection, repeat activity loads, and longer sessions remain to test. A production implementation must not blanket-override mouse metrics for the entire process or force MSTS's failed initializer to return success. Avoid OS-version-specific DINPUT.dll instruction patches; investigate an import-level wrapper with complete restoration and existing runtime safeguards.

### Diagnostics and implementation constraints

Start with an accurate diagnostic: record mouse-presence metrics at launch and identify an actual input-initializer failure when available. A warning can explain that remote pointer movement does not necessarily provide a DirectInput mouse, and suggest connecting a mouse or receiver. Do not block launch solely on a system metric or automatically edit the registry.

A native fallback for genuinely mouse-less hosts requires separate design and verification of pointer movement, buttons, camera/cab interactions, device cleanup, and remote control. Do not bypass the failed initializer or pretend mouse binding succeeded: downstream code expects valid state.

Keep diagnostics optional, preserve original return values and error state, use the existing supported-image and byte guards for any hooks, and keep XP-compatible Win32-only runtime dependencies. Frida/Python are investigation tools only and must not enter the packaged runtime.

No runtime, executable, version, or release was changed by this investigation note.
