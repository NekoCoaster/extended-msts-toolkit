# Native toolkit foundation

NEMT derives from MEDS commit `1b7760f`. One x86 `DINPUT.dll` forwards seven DirectInput exports to the Windows system DLL and owns native feature initialization. `DllMain` does not install gameplay hooks.

## Configuration and stages

`runtime/config.h` reads restart-only feature flags from `NEMT/native.ini`. Missing feature flags default off. Invalid booleans, invalid strength or crawling without activity-end prevention reject feature installation. `runtime/loader.c` verifies the normalized whole executable and requires the two legacy MEDS patches to be absent on disk.

The current gameplay stage waits for a stable train/head/body backlink, valid controls and an advancing simulation clock across about five seconds. Startup menus therefore remain unmodified. Settings load normally. This delay also means features are not available in the first moments of an activity. Initially paused activities wait for resume.

Future window-mode work will need a separately validated earlier stage. It must not weaken the gameplay readiness gate or use early Frida attachment.

## One mutation transaction

`runtime/hooks.h` supports checked detours and short raw instruction replacements. Every selected mutation claims an address range. Overlaps and unexpected original bytes are rejected before installation. Peer threads are temporarily suspended; if a thread is inside a target prefix, installation retries. A later byte mismatch rolls back earlier writes. DirectInput forwarding continues if feature setup fails.

The optional activity-end and camera replacements use their verified MEDS bytes, now in process memory only. Crawling contributes eleven native detours, preserving registers, flags, floating-point state and call cleanup. Inactive/paused fast gates avoid full callback overhead. Raw replacements have no per-frame callback cost.

```mermaid
flowchart TD
 A[Normal MSTS startup] --> B[Forward DirectInput to Windows]
 B --> C[Validate clean supported image and settings]
 C --> D[Wait for ready driving scene]
 D --> E[Prepare selected feature mutations]
 E --> F[Reject overlaps and changed bytes]
 F --> G[Install in one transaction]
 G --> H[Run enabled MEDS features]
 H --> I[Activity exit clears crawl state]
 I --> H
```

The activity-end and camera instructions remain configured until process exit. Crawl eligibility is cleared on activity exit and recovered for a later activity. The DLL never saves its in-memory patches back to `train.exe`.

## Installer migration

The form retains drag-and-drop, registry discovery, compatibility verification and Uninstall. It saves feature flags rather than toggling disk instructions. A one-time migration normalizes only the two identified MEDS patches, after making and checking an exact backup. It verifies owned DLL/payload hashes and retires known legacy runtime files. Unrelated wrappers and unknown folders are not replaced. Rollback snapshots cover changed configuration, ownership records, DLL and legacy payloads.

## Build

Use the x86 Tiny C Compiler 0.9.27 distribution:

```powershell
python runtime/build.py C:/Tools/tcc/tcc.exe
python tools/package.py
```

The build refreshes the DLL integrity hash. The packager excludes Git metadata and scratch work, verifies local documentation links and checks archive CRC/content equality. Compiler/runtime notices remain under `docs/licenses`. Contributor tools are not end-user dependencies.
