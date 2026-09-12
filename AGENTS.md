# Toolkit scope

This is a separate local repository for Neko's Extended MSTS Toolkit (NEMT), derived from MEDS commit `1b7760f`. The authorized GitHub repository is `NekoCoaster/extended-msts-toolkit`. Access only this repository for NEMT work; do not push toolkit work into MEDS.

Preserve MEDS releases. Never include game executables, private keys or raw game decompilation. Scratch files belong outside the distributable source or in ignored `work/`.

Launch the designated MSTS installation normally with `train.exe -vm:w`. Never attach Frida before settings and the driving scene finish loading. The native readiness gate must remain covered by regression checks.

Clean supported executables must remain byte-for-byte unchanged by normal configuration and uninstall. Reject previously patched executables; never migrate legacy installations or write train.exe. Never replace unrelated DirectInput or graphics wrappers.

New features must claim their instruction ranges through the shared mutation transaction, reject overlaps, validate original bytes and define their startup stage. Configuration changes require a game restart. The current borderless setting controls ordinary `-vm:w`. Read configuration only from `settings.ini`; historical NEMT options are not supported.

Build with `python runtime/build.py <x86-TCC-path>`. Package with `python tools/package.py`; this excludes `.git` and `work` and checks archive bytes and DLL integrity. Never present old MEDS traces as new toolkit measurements.
