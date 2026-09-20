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
and on repeat calls, and returned 80040154 again after restoration. This does not replace a
mouse-less in-game test of cab movement, clicks, dragging, reconnecting hardware,
and repeated activity loading. The earlier remote-host experiment established
the workaround, but is not a test of this committed runtime.
