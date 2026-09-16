# Native GUI parity review — 2026-09-16

Reference: `legacy/NEMT.ps1` and the native frontend in the supplied
`extended-msts-toolkit(1).zip`. This review uses that uploaded snapshot, not
an assumed version of the online repository.

## Confirmed differences and corrections

| Area | Problem in the uploaded native port | Correction |
| --- | --- | --- |
| Apply / Uninstall | `do_save` called `load_selection(g_info.path)`, which zeroed `g_info` before reading its aliased path. A successful save could invalidate the selection. | Copy the path before clearing state, and keep a separate selected-path copy across save/reload. |
| Feedback | Reload replaced the success message with the executable version. | Separate version/status and operation messages; reload before showing the save result. |
| Recommended | The native button omitted verbose loading and cleared vsync/counter-tilt. | Follow the PS1 selection behavior, including vsync, verbose loading and counter-tilt; deep logging stays off. |
| FPS dependency | Disabling Unlock FPS erased the vsync checkmark. | Disable the dependent control without erasing its choice; effective vsync is still false when saving with Unlock FPS off. |
| Counter-tilt | Turning off crawl erased the saved preference on Apply. | Disable the control but retain its preference, as PS1 did. |
| Crawl controls | The slider was replaced by a numeric edit and the HUD dropdown by a checkbox. | Restore the 0–100 trackbar, `Disabled`/`Nx` readout, hint and Bottom right / Bottom left dropdown. |
| Layout | FPS and vsync had overlapping control rectangles. The fixed-height form had no scrolling or DPI layout. | Separate rectangles, logical-coordinate DPI scaling, vertical/horizontal scrolling, mouse wheel and focus visibility. |
| Keyboard | No tab-stop styles or dialog message processing. | Native dialog navigation, accelerators, default Apply/Browse and Escape/Close. |
| Presentation | Versioned heading/title, instructions, storage note and documentation links were missing. | Restore those items using native controls and system fonts. The existing historical screenshot is not presented as a new screenshot. |
| Loading settings | The port read only the INI and ignored manifest enablement and fallback values. | Restore manifest-driven main controls and enabled-installation INI overrides. Ignore stale INI choices after uninstall. |
| Partial INIs | Missing `CenterWindowed` and `Window.Enabled` became false. | Retain their true defaults when a key is absent. Preserve manually edited key bindings, diagnostics and log limits. |
| P-core preference | Apply forcibly cleared `PreferPCores` on an unsupported machine. | Preserve the saved value when the control is unavailable. Detection remains optional and is cached at startup. |
| Discovery | Only the process's default registry view and first existing candidate were used. Quoted paths were mishandled. | Read both registry views with an ordinary-view fallback, trim quoted paths, prefer a supported candidate. |
| Running game | Any process called `train.exe` blocked every installation, while renamed executables were missed. | Check the selected executable's name/path; inaccessible matches block conservatively. Newer path-query APIs are dynamically resolved. |
| Ownership | Ownership was inferred with substring searches, without checking schema. | Parse the whole bounded JSON record; require the top-level product/schema/enabled values. Reject malformed and duplicate top-level keys. |
| Install safety | Selected-image hash rechecks and the PS1 multi-file rollback were absent. | Verify the selected image before/after changes and restore changed owned files on an installation failure. |
| Uninstall safety | Unowned settings/status files could be deleted, and some write failures were ignored. | Only remove owned settings/runtime, preserve diagnostic status, check writes and retain the original manifest with `enabled=false`. |
| Build / packaging | Compilation wrote over the final executable directly; the release job fetched the incomplete base headers again. | Compile to a pending executable, publish it only on success, use the supplied full toolchain in CI and exclude build/test artifacts from release packaging. |

## Scope and architecture

The program remains C with Win32 system controls, x86, and an XP API baseline.
The trackbar uses the system Common Controls library (`comctl32`), not a GUI
framework. `NEMT.exe.manifest` requests standard themed controls and system-DPI
awareness; keep it beside the executable. There is no PowerShell or .NET runtime
path. The injected `runtime/DINPUT.dll` is unchanged in this review.

The layout and behavior were brought closer to the actual PS1 implementation;
this is **not a claim of complete, visually verified parity**. In particular,
legacy PowerShell command-line actions are not a new native CLI, and the initial
native port's ANSI / `MAX_PATH` path limitations have not been replaced with a
full Unicode/long-path layer. Mixed-monitor DPI changes still require reopening
the system-DPI-aware application.

## Validation actually completed here

- Portable C settings/JSON regression suite: **52 assertions passed**, compiled
  and run with GCC AddressSanitizer and UndefinedBehaviorSanitizer enabled.
- Native frontend source invariants: **19 checks passed**. These are structural
  guards, not substitutes for running the GUI.
- SHA-256 implementation compared with Python `hashlib` at padding/block
  boundaries and on larger files: **11 vectors passed**.
- Frontend and Windows GUI/installer test harness compiled to **i386 COFF object
  files** with Clang. For this independent compiler check only, two TCC-specific
  inline-assembly spellings in a temporary copy of `winnt.h` were adapted for
  Clang (`%eax` and `int 0x2c`). No vendored header was changed or shipped with
  that adjustment. This is not a completed TinyCC build or link.
- The unchanged runtime DLL passes the existing PE32/x86 import audit. That
  audit catches listed incompatible imports; it is not an exhaustive XP
  compatibility certification.
- Workflow YAML, application manifest XML, Python syntax, source checksums,
  archive integrity and patch application were checked when packaging.

## Windows verification still required

Run `BUILD AND RUN NEMT.bat` in an extracted source tree. This builds the new
`build\NEMT.exe` and its manifest using the supplied Windows TinyCC compiler.
The old uploaded executable is deliberately excluded from the corrected source
archive to avoid accidentally testing the stale version again.

Run `TEST NEMT.bat` to compile and execute the portable model tests and native
Windows regression harness. The harness creates a temporary folder and a
synthetic executable file. It exercises real control messages, settings loading,
locked-file rollback, uninstall preservation and ownership rejection without
using or launching a real MSTS installation. Its Windows execution was **not
performed in this Linux environment**; the updated release workflow runs it
before publishing.

Manual acceptance checks remain necessary on Windows 11 and the older target
systems: Browse/drop a supported `train.exe`, Apply repeatedly, close/reopen,
Uninstall, test Tab/Shift+Tab and slider keys, verify small-display/high-DPI
scrolling, and confirm the installed options in the actual game. Keep a backup
of your installation before testing a changed installer. No live game test,
Windows visual test, memory measurement or XP certification is claimed here.
