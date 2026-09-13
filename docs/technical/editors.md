# Toolset implementation and validation

Toolset hooks install during the verified command-line bootstrap, after supported-image identification and configuration validation. Exact `-toolset` token detection bypasses simulator window normalization and game feature installation. Editor flags default off and are independent.

The shared mutation transaction owns the main window-procedure entry at `0x696c00`, frame calls at `0x4999b0`, `0x6764b3` and `0x451d4f`, the optional snapping helper entry at `0x55521c`, and the optional SetWindowPos import at `0x84df30`. All original instructions are checked before writes. The supported executable's disk bytes remain unchanged. Mode 1 plus the toolset flag identifies Route Editor; mode 3 is Activity Editor, mode 4 Cab Editor and mode 2 the launcher.

Resize processing waits until a native frame boundary after window dragging settles. It releases UI surface references, calls the native renderer reset at `0x521315`, and reconnects UI surfaces through `0x646210`. The temporary window-placement suppression flag is cleared before subsequent launcher/editor transitions. Maximized dimensions also update MSTS's cached client dimensions, which its own procedure only refreshes for restored windows.

Route camera dimensions and horizontal field of view are updated together, preserving vertical field of view. Native refresh `0x51cd5f` rebuilds projection. Picking separately hard-codes a 640×480 coordinate basis in four selection/placement routines. The 24 verified `FDIVR` instructions listed in `runtime/editor_picking.h` now read the current camera width/height. All 24 ranges belong to the same editor hook transaction. This retains the native client-to-camera conversion during deferred resizing, along with the native rays and hit tests. Compass anchors are refreshed through `0x6413e6`, keeping the compass and latitude/longitude centered at the top.

Native fastcall helpers use named function-pointer typedefs: this toolchain otherwise compiled an anonymous fastcall cast with the wrong calling convention during development. Activity wheel zoom calls native `0x672f34` with the same 20% step as the Tools palette, followed by `0x67360d` for bounds. Partial wheel deltas accumulate to 120-unit detents. Screen-relative hit testing excludes folded panels and floating tools, and zoom is ignored during mouse capture or without a loaded activity.

Shared startup/loading hooks install outside the simulator-only bootstrap branch. Timing, movie, gameplay and main-game borderless hooks remain isolated from toolset.

Activity map bounds at `0x80adb8` preserve world center and scale when resized; `0x67360d` applies the native map-bound constraints. Panel placement temporarily guards MSTS's own recursive anchoring flag at `0x80ae98`. Panel ownership keeps them above the map without making them globally topmost. Layout calculations use the nearest monitor's work area, including negative screen coordinates.

Cab Editor's two presentation calls at `0x44a8e6` and `0x44a8ba` are also transaction-owned when resizing is enabled. They proportionally fit the completed 640×480 canvas through DirectDraw, retaining native window clipping and white margins. Client mouse coordinates use the inverse fit; menus and tool dialogs retain their normal coordinates. This preserves alignment between cab artwork, instruments and selection outlines without editing cab files.

The native logical-canvas cursor warp at `0x44390a` now uses the forward cab fit. Its arguments contain the old native window origin plus logical canvas coordinates; the wrapper recovers those logical coordinates and adds the current client origin and centered fit. Upward integer rounding preserves the inverse mouse-coordinate round trip. Only this verified indirect-call instruction is redirected, so ordinary Windows dialogs and other cursor calls keep their screen-coordinate behavior.

## Route Editor camera keys

`SwapArrowKeys` installs independently of resizing. Six case-insensitive `RE_CAM_*` bindings use DirectInput scan codes, with duplicate, reserved and malformed enabled bindings rejected during configuration validation. Installer Apply preserves custom values.

The buffered-input gateway at `0x6bae0e` remaps keyboard events before native IOM lookup. Physical camera keys use reserved scan zero to suppress their displaced commands; the native zero slot is unbound. Arrow events select the configured key's original action, retaining native command handlers and their editing-mode restrictions. Releases use the mapping and modifiers chosen by their matching press. Ctrl+Up/Down consumes the Ctrl modifier for the displaced command; the paired gateway at `0x6bb236` restores the original modifier mask and native Ctrl state before fetching another event, leaving no pointers into a returned stack frame. Both gateways preserve registers, flags and floating-point state.

The camera-input call at `0x48ff6b` is wrapped separately. The native routine still handles mouse motion, rotation and timing; camera translation reads held physical keys from the native keyboard bitset. This supports simultaneous forward, lateral and vertical motion without synthesizing a global Ctrl key. Shift speed and lateral cooldown remain native-compatible. Ctrl+letter shortcuts, Ctrl+Left/Right rotation, and Alt shortcuts remain available. Focus is checked on the window's GUI thread, including exclusion of menus and move/size loops, so text fields and tools retain normal input. These three instruction ranges use the shared startup mutation transaction and are installed only in toolset mode.

## MegaCoaster audio finding

On this installation, the listener update at `0x541926` took about 206 ms per call when the route had no active nearby audio. A short authorized capture recorded 21 calls taking 4,324 ms. Starting a silent looping software buffer removed that delay. With the installed fix, a later 15-second capture recorded about 56 native frames per second and 847 listener calls taking 83 ms in total, compared with roughly 4–5 frames per second before the fix. These are local observations, not a hardware-independent performance guarantee.

The fix uses the existing DirectSound device and a one-second, mono 22,050 Hz, 16-bit buffer. Both lock regions are zero-filled. Buffer loss and stopped playback are recovered, creation failures back off, and the owned buffer is released on leaving Route Editor, minimizing or destruction. It changes no route sound files or sources. The four missing model references removed from the local MegaCoaster fixture were separately authorized test preparation and are not included in NEMT.

## Regression checks

- `tests/editor-input.c`: executes all 24 production picking operands across seven sizes, including differing client/camera extents during resize; checks wheel detents, partial deltas and reversals.

- `tests/editor-sites.py`: verifies frame calls, snapping/window entries and renderer/camera/map helper entries against base and widescreen fixtures.
- `tests/editor-config.c`: checks missing settings, all sixteen option combinations, custom keys and malformed/duplicate/reserved values.
- `tests/editor-installer.ps1`: checks independent settings and manifest persistence, install/uninstall across base, widescreen and both LAA variants; executable hashes stay unchanged.
- `tests/editor-layout.c`: covers independent right/bottom folding across monitor origins, minimum layout and small-monitor fallback.
- `tests/editor-cab.c`: checks centered 4:3 fit and mouse-coordinate round trips at seven display sizes, including tall and ultrawide windows.
- `tests/editor-cab-cursor.c`: exercises the production cursor wrapper and inverse mouse mapping across five sizes, stale native origins, negative monitor coordinates and disabled/other-editor fallback.
- `tests/editor-keyboard.c`: exercises the production event gateway callback and camera wrapper in an isolated x86 memory fixture: configurable/displaced bindings, modifier and release pairing, focus changes, diagonal and vertical movement, Shift speed and disabled behavior.
- `tests/editor-audio.c`: checks the DirectSound ABI, silent split locks, looping, recovery, teardown and retry backoff with a fake device.
- Window argument, Win32 behavior, bootstrap, mutation transaction, native timing, startup, movie, cab-dial, signal, crawl lifecycle and world-relative pitch checks also pass with the combined runtime.

Run C checks with the project's x86 TCC, linking `-ladvapi32 -luser32` for tests that include the loader. Installer fixtures and disassembly exports belong in ignored `work/`. Live editor checks cover this host's graphics setup; other wrappers, mixed-DPI monitors and extended editing sessions still need user coverage.

The GP38 cab was opened without saving changes. Maximizing produced a centered proportional view with white side margins; clicking its displayed speedometer selected the correct needle. Route Editor was checked on MegaCoaster with an enlarged native camera viewport. The world-relative crawl correction also received a successful in-game user report before the editor work.

Activity Editor was checked with the existing USA2 `yard_two.act`: the maximized map redraws throughout its available area and both panel groups fold inside. Alt+Enter enters borderless fullscreen. Returning from fullscreen restores an ordinary 800×600 launcher client and its exit controls work. No activity or cab file was saved during these checks.

Alpha.11 checks: in maximized MegaCoaster, clicking the track near the lower-right edge selected the track under the cursor, beyond the old 640×480 area. The loading screen displayed verbose file details. The compass stayed centered in fullscreen and after returning to the original window. Wheel up enlarged the loaded USA2 activity map and wheel down reduced it. The patcher displayed the full HUD label and dropdown on a separate row. These tests saved no route or activity edits.

Alpha.12 checks: selecting the GP38 speedometer in borderless fullscreen kept the cursor on the displayed instrument. MegaCoaster loaded with the keyboard hooks installed; with a temporary custom G camera binding, G no longer toggled its old grid command. Physical-arrow and sustained-key live checks remain for user coverage: this host's automation sends its Up command as scan `0x48` (numpad 8), not the physical arrow's `0xc8`, and brief injected taps do not establish held movement. The isolated x86 tests cover the intended scan codes, releases and simultaneous held axes. No cab or route changes were saved.
