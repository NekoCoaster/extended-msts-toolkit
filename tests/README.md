# Which tests to run

The current frontend suite is `TEST NEMT.bat` (interactive) or `TEST NEMT.bat --ci` (no pause). It compiles and runs the settings model, viewport model and native GUI/installer harness using the bundled x86 compiler. It uses temporary synthetic files, not a real game installation.

The same entry point also runs guarded high-resolution patch, display-selection
and native window-placement regressions. The high-resolution tests modify only
synthetic memory in their own process. `tests/high-resolution-device.c` is an
optional desktop host experiment, excluded from normal CI: compile with the
bundled compiler and `-ladvapi32 -luser32`, then run in an interactive desktop
session. It compares real 640x480 and 2560x1440 Direct3D7 devices before/after
the integrated fix. Unsupported graphics environments report INCONCLUSIVE.

Contributor Python checks are `python tests/native-frontend.py` and `python tests/repository-tools.py`. The former is a source guard, not a GUI test. The latter exercises source inventories, toolchain locks, source-archive validation and deterministic/non-destructive packaging. Its generated compiler-source fixtures are unit-test data, **not** a substitute for the genuine pinned source archive.

Other C/Python tests here cover particular runtime components or historical executable-analysis fixtures. Run those appropriate to an intentional runtime change, using the documented fixtures. Do not assume a directory-wide test run has all game-specific fixture inputs available.

The `.ps1` tests belong to the former PowerShell frontend and its historical regression environment. They are retained as migration references, not part of the current native CI suite and not a PowerShell requirement for end users. Their old source-layout assumptions must not be confused with testing today's native frontend.

See [Build and publishing](../docs/technical/maintenance.md) and [migration validation](../docs/technical/native-frontend-validation.md) for commands and evidence limits.
