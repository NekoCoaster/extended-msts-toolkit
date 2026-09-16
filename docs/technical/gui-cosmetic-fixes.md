# Native GUI size and repaint fixes

Baseline: `extended-msts-toolkit-gui-parity-fixes.zip`, the version confirmed
working by the user. This is a focused presentation change; installer/config
semantics, runtime files, the application manifest and the bundled compiler are
unchanged.

## Default size and scrollbar calculation

- Preferred client area is now **784 x 864 logical pixels**, up from a requested
  760 x 840: 24 extra logical pixels in each dimension. Windows borders/title
  bar are added separately, and the outer rectangle is centered and capped to
  the desktop work area. These dimensions scale with the existing system DPI.
- The window is created without forced horizontal/vertical scrollbar styles.
  The layout adds bars only when the available viewport requires them.
- Scrollbar necessity is calculated from the client area with the current
  scrollbar widths/heights added back. The two-axis calculation starts with
  neither bar, then accounts for each bar's effect on the other axis. This
  prevents two unnecessary bars from keeping each other visible after resize.
- Enlarging the window to fit the content resets the obsolete scroll offsets.
  Small displays and higher scaling still use scrolling when the content
  genuinely cannot fit. Minimized windows skip layout/repainting.

## Scroll repaint

Previously, controls were moved with `MoveWindow(..., TRUE)` one at a time,
then only the parent was invalidated. The parent uses `WS_CLIPCHILDREN`, and
several controls draw transparent text. That path allowed partial or preserved
control pixels to outlive the movement of neighboring controls.

Now every control, including those outside the visible viewport, moves in a
single `BeginDeferWindowPos` / `DeferWindowPos` / `EndDeferWindowPos` batch.
`SWP_NOREDRAW | SWP_NOCOPYBITS` prevents intermediate redraws and copying of
stale pixels. A final `RedrawWindow` invalidates and erases the background and
repaints the controls and their nonclient edges synchronously:

```c
RDW_INVALIDATE | RDW_ERASE | RDW_FRAME | RDW_ALLCHILDREN | RDW_UPDATENOW
```

If the positioning batch cannot be allocated/completed, the fallback uses
individual `SetWindowPos` calls with the same no-copy/no-redraw flags, followed
by the same repaint. No timer, animation loop, offscreen bitmap framework,
new GUI library or newer mandatory API is added.

## Checks completed in this environment

- Portable viewport model: **104,984 cases / 998,600 assertions passed**, with
  AddressSanitizer and UndefinedBehaviorSanitizer enabled. Covers exact-fit,
  narrow/short windows, coupled scrollbars, offset clamping, repeated layout,
  and 100%, 125%, 150% and 200% scaling arithmetic.
- Existing portable settings/JSON model: **52 checks passed**, with the same
  sanitizers enabled.
- Native frontend structural guards: **28 checks passed**.
- Frontend and native GUI regression harness: both compiled to **i386 Windows
  COFF object files using Clang**. As in the preceding review, two TCC-specific
  assembly spellings in a temporary header copy were adjusted only for this
  compiler check. No bundled header was modified. There is one existing
  `noreturn` warning from the temporary copy of TCC's `stdlib.h`.
- New Win32 positioning/redraw symbols are present in the supplied headers
  and `user32.def`. Manifest XML and workflow YAML still parse.

This is **not** a completed Windows TinyCC build, linked executable test, or
live visual verification. No Windows desktop is available in this environment.
The Windows harness has been extended to check actual client size, scrollbar
removal, background erasure and child paint messages, and repeated scroll
round trips. Its execution still needs Windows.

## Apply and verify

Close NEMT. Extract the small overlay into the repository root, accepting
replacement of its listed files, or use the full updated repository archive.
Do not replace just `src/nemt.c`: the new `src/viewport_model.h` is also needed.
Rebuild using `BUILD AND RUN NEMT.bat`. Keep the generated manifest next to
`build/NEMT.exe` as before. The source archive deliberately has no old app
executable.

For automated Windows checks, run `TEST NEMT.bat`. The new viewport test is
portable; the existing GUI/installer harness still uses disposable synthetic
files in TEMP rather than a real game installation.

Manual acceptance: open at the default size on a display large enough for
it, shrink until scrollbars appear, scroll up/down and side-to-side (including
rapid thumb dragging), then enlarge again. Text/control edges should redraw
cleanly and the bars should disappear once the full content fits. Also check
Tab navigation to the bottom controls, minimize/restore, and the normal saved
settings workflow. Mixed-monitor per-monitor DPI support remains outside this
change; the existing application is system-DPI-aware.

## API references

- Microsoft: AdjustWindowRectEx ignores scrollbar styles when computing size:
  https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-adjustwindowrectex
- Microsoft: DeferWindowPos batching, SWP_NOCOPYBITS and SWP_NOREDRAW:
  https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-deferwindowpos
- Microsoft: RedrawWindow erasure, child inclusion and synchronous repaint:
  https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-redrawwindow
