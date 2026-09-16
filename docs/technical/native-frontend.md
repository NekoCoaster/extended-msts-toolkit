# Native frontend

The NEMT control panel is implemented in `src/nemt.c` as a deliberately small Win32/x86 application.

## Design constraints

- C and the native Win32 API only.
- Windows XP SP3 API baseline (`WINVER` and `_WIN32_WINNT` 0x0501).
- No PowerShell, .NET, browser engine, Python, Node.js or GUI framework at runtime.
- No mandatory modern API imports. Optional modern functionality must be resolved dynamically.
- Low enough resource usage for Pentium-era hardware with approximately 256 MB RAM.
- The UI and installer leave `train.exe` unchanged.

## CPU preference capability detection

`GetSystemCpuSetInformation` is not imported directly. `kernel32.dll` is queried using `GetProcAddress`; absence of the function means the option is disabled. When available, the returned CPU-set records are inspected for more than one efficiency class before the checkbox is enabled.

This prevents a modern-only optional feature from raising the minimum OS version of the entire program.

## Source build

`build.bat` invokes TinyCC directly and produces `build\NEMT.exe` plus its sidecar `NEMT.exe.manifest`. `BUILD AND RUN NEMT.bat` is the user-facing wrapper. Both deliberately avoid newer shell syntax.

The release workflow uses the bundled compiler and required WinAPI header subset, invokes the same build script, and runs `TEST NEMT.bat --ci` before packaging a release. The generated executable is not committed to the repository.

The supplied `tools/tcc/` directory contains the reviewed 50-file x86 compiler/header/library subset for offline builds. Keep that subset together. Build outputs are not project source.

## Legacy reference

The former PowerShell/WinForms implementation lives under `legacy/`. It is retained temporarily for feature-parity comparison and regression work only.

## Parity review and regression tests

See [the GUI parity review](gui-parity-review.md) for the corrected differences, tests actually run, and remaining Windows validation. The GUI-independent settings/manifest model is in `src/settings_model.h`; ownership JSON parsing is in `src/json_record.h`.

## Repository verification

The read-only PR workflow and tag-only release workflow share the native test checks. `tools/source-checksums.py` manages source checksums explicitly; packaging writes a separate release manifest without modifying source. The complete TinyCC source archive is redistribution material, not a new build prerequisite. See [Build and publishing](maintenance.md) and [current migration validation](native-frontend-validation.md).
