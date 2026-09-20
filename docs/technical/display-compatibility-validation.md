# Display compatibility development checkpoint

20 September 2026. Branch: `feature/display-compatibility`.
This is a development checkpoint, not a version bump or release.

## Completed checks

- Native GUI/installer regression suite: 289 checks, zero failures, including
  monitor and compatibility setting persistence, external-file handling,
  threshold warnings and repeat suppression. Layout exercised at 96/120/144/192 DPI.
- Two-monitor synthetic placement: secondary display at negative coordinates,
  disconnected fallback, and strict per-monitor 2048 threshold.
- Native Win32 window test: frame removal, retained client dimensions, centering,
  resize, manual movement and editor exclusion.
- Guarded patch tests: both supported instruction forms, repeated and mixed
  states, invalid PE data, ambiguous signatures, external-file stand-down,
  page-protection and LastError preservation.
- Real desktop Direct3D7 test: 640x480 surface/device succeeded; 2560x1440
  surface succeeded but device returned `0x88760082` before the fix. After the
  fix, both the 2560x1440 surface and device succeeded. The restricted execution
  environment could not provide working graphics; its earlier run was inconclusive.
- System x86 D3DIM700.dll SHA-256 before and after remained
  `9928cf574f86f25525de9692f5866a7ca9a0166222d9c3e24a1c50a67c42ed47`.
- Live panel inspection on a 1920x1080 desktop: display dropdown enumerated the
  primary monitor; all controls fit without overlap at 96 DPI. The existing
  widescreen D3DIM700.dll was recognized. No Apply was performed on that installation.

The real graphics result is device-creation evidence, not an MSTS activity test.
The original automated run did not test Windows XP/7 or other system DLL versions.
Unrecognized implementations must stand down with an explanatory startup notice.

## Subsequent user-reported validation

- The user reported that the form works on Windows XP, 7 and 11, and that
  standalone operation without the external MIT-0 DLL works on their laptop.
- Following b98ffac, in-game clicking, dragging and activity loading work with
  no mice connected.
- Following 8349087, the window remains on the selected secondary monitor.
- The final wording/alignment update passes 299 native GUI/installer checks,
  the remaining native regression suite, source guards, repository-tool checks
  and the XP-baseline frontend import audit. The frontend build succeeded.

These reports close the reported functional issues; they do not establish every
step of the broader laptop checklist below on every operating system or wrapper.

## Laptop validation

1. Clone or check out `feature/display-compatibility`, then run
   `BUILD AND RUN NEMT.bat`. The offline build uses the bundled compiler.
2. With MSTS closed, select a disposable game installation. Record the actual
   display dimensions; 2560x1440 triggers the recommendation, whereas 2048x1080
   does not. Windows scaling does not change this pixel threshold.
3. For integrated-fix testing, use a test installation without local
   D3DIM700.dll/ddraw.dll. Preserve any existing wrappers separately; NEMT never
   removes or overwrites them. A recognized external DLL intentionally suppresses
   the missing-support suggestion and takes precedence over the integrated fix.
4. Check the warning and links, choose the desired monitor, enable compatibility,
   enable deep logging for this test, and Apply. Reopen NEMT to verify saved values.
5. Launch MSTS normally, select a supported resolution above 2048, enter an
   activity, check controls and rendering, return to the menu and enter again.
   Check `NEMT/startup.log` for `HIGH RESOLUTION` and the activation result.
6. Repeat on a second monitor if available, then with the selected monitor
   disconnected. Verify primary fallback, window size, Alt+Tab, and placement
   after changing the game resolution. Reconnect and restart to check restoration.
7. Disable compatibility and restart to compare behavior if safe. Re-enable it
   afterward as needed. Turn deep logging off when testing is finished.

Keep the final PR unchanged until these host results are reviewed. No automatic
claim of compatibility across all target Windows versions is implied by this build.
