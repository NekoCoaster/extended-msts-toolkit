# Mouse detection on remote or mouse-less hosts

For supported simulator executables with valid settings, NEMT automatically checks
mouse presence during startup, outside the loader lock. When Windows reports no
physical mouse, NEMT adjusts only the system DINPUT.dll import of GetSystemMetrics.
Zero mouse-presence and button-count results become one mouse and three buttons.
Other metrics, nonzero results, device creation errors and actual input remain
Windows' responsibility. Reconnected hardware values pass through normally.
Editors and machines already reporting a mouse are unchanged.

The import must be a unique named PE32 USER32.dll GetSystemMetrics import pointing
to the original function. Unknown or intercepted imports are left alone. The
aligned pointer replacement is atomic and restores page protection. Both modules
remain loaded for callback safety. A guarded restoration helper is regression
tested; normal process exit releases the process-local adjustment. Nothing on
disk or in other applications is patched. Startup logs record the outcome.

Validation: native regression tests cover missing-mouse values, reconnection
values, last-error preservation, malformed imports, unexpected pointers, page
protection, installation/restoration, and repeated real DirectInput mouse creation.
With the physical mouse dongle removed, Windows reported no mouse: real DirectInput
mouse creation returned 80040154 before installation, succeeded after installation
and on repeat calls, and returned 80040154 again after restoration.

On 2026-09-20, following checkpoint b98ffac, the user confirmed that in-game
clicking, dragging and activity loading work as intended with no mice connected.
This is user-reported in-game validation, separate from the native regression
results above. Physical reconnection during a running game and extended-session
testing have not been reported. The earlier remote-host experiment established
the workaround, but is not a test of this committed runtime.
