# Toolset implementation and validation

Toolset hooks install during the verified command-line bootstrap, after supported-image identification and configuration validation. Exact `-toolset` token detection bypasses simulator window normalization and game feature installation. Editor flags default off and are independent.

The shared mutation transaction owns the main window-procedure entry at `0x696c00`, frame calls at `0x4999b0`, `0x6764b3` and `0x451d4f`, the optional snapping helper entry at `0x55521c`, and the optional SetWindowPos import at `0x84df30`. All original instructions are checked before writes. The supported executable's disk bytes remain unchanged. Mode 1 plus the toolset flag identifies Route Editor; mode 3 is Activity Editor, mode 4 Cab Editor and mode 2 the launcher.

Resize processing waits until a native frame boundary after window dragging settles. It releases UI surface references, calls the native renderer reset at `0x521315`, and reconnects UI surfaces through `0x646210`. The temporary window-placement suppression flag is cleared before subsequent launcher/editor transitions. Maximized dimensions also update MSTS's cached client dimensions, which its own procedure only refreshes for restored windows.

Route camera dimensions and horizontal field of view are updated together, preserving vertical field of view. Native refresh `0x51cd5f` rebuilds projection and selection transforms. Native fastcall helpers use named function-pointer typedefs: this toolchain otherwise compiled an anonymous fastcall cast with the wrong calling convention during development.

Activity map bounds at `0x80adb8` preserve world center and scale when resized; `0x67360d` applies the native map-bound constraints. Panel placement temporarily guards MSTS's own recursive anchoring flag at `0x80ae98`. Panel ownership keeps them above the map without making them globally topmost. Layout calculations use the nearest monitor's work area, including negative screen coordinates.

Cab Editor's two presentation calls at `0x44a8e6` and `0x44a8ba` are also transaction-owned when resizing is enabled. They proportionally fit the completed 640×480 canvas through DirectDraw, retaining native window clipping and white margins. Client mouse coordinates use the inverse fit; menus and tool dialogs retain their normal coordinates. This preserves alignment between cab artwork, instruments and selection outlines without editing cab files.

## MegaCoaster audio finding

On this installation, the listener update at `0x541926` took about 206 ms per call when the route had no active nearby audio. A short authorized capture recorded 21 calls taking 4,324 ms. Starting a silent looping software buffer removed that delay. With the installed fix, a later 15-second capture recorded about 56 native frames per second and 847 listener calls taking 83 ms in total, compared with roughly 4–5 frames per second before the fix. These are local observations, not a hardware-independent performance guarantee.

The fix uses the existing DirectSound device and a one-second, mono 22,050 Hz, 16-bit buffer. Both lock regions are zero-filled. Buffer loss and stopped playback are recovered, creation failures back off, and the owned buffer is released on leaving Route Editor, minimizing or destruction. It changes no route sound files or sources. The four missing model references removed from the local MegaCoaster fixture were separately authorized test preparation and are not included in NEMT.

## Regression checks

- `tests/editor-sites.py`: verifies frame calls, snapping/window entries and renderer/camera/map helper entries against base and widescreen fixtures.
- `tests/editor-config.c`: checks missing settings, all eight option combinations and malformed values.
- `tests/editor-installer.ps1`: checks independent settings and manifest persistence, install/uninstall across base, widescreen and both LAA variants; executable hashes stay unchanged.
- `tests/editor-layout.c`: covers independent right/bottom folding across monitor origins, minimum layout and small-monitor fallback.
- `tests/editor-cab.c`: checks centered 4:3 fit and mouse-coordinate round trips at seven display sizes, including tall and ultrawide windows.
- `tests/editor-audio.c`: checks the DirectSound ABI, silent split locks, looping, recovery, teardown and retry backoff with a fake device.
- Window argument, Win32 behavior, bootstrap, mutation transaction, native timing, startup, movie, cab-dial, signal, crawl lifecycle and world-relative pitch checks also pass with the combined runtime.

Run C checks with the project's x86 TCC, linking `-ladvapi32 -luser32` for tests that include the loader. Installer fixtures and disassembly exports belong in ignored `work/`. Live editor checks cover this host's graphics setup; other wrappers, mixed-DPI monitors and extended editing sessions still need user coverage.

The GP38 cab was opened without saving changes. Maximizing produced a centered proportional view with white side margins; clicking its displayed speedometer selected the correct needle. Route Editor was checked on MegaCoaster with an enlarged native camera viewport. The world-relative crawl correction also received a successful in-game user report before the editor work.

Activity Editor was checked with the existing USA2 `yard_two.act`: the maximized map redraws throughout its available area and both panel groups fold inside. Alt+Enter enters borderless fullscreen. Returning from fullscreen restores an ordinary 800×600 launcher client and its exit controls work. No activity or cab file was saved during these checks.
