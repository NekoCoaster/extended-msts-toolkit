# Provenance and investigation

The toolkit builds on MEDS's verified activity-end branch, camera restriction, connected-engine graph, momentum model, scoped drag/pitch effects and wheel/steam-rod animation. Its inherited equations remain in [physics.md](physics.md), and the two identified byte changes are documented in [patches.md](patches.md).

MEDS checkpoints remain in the original repository: `39402b7` (Ready V1), `b16105c` (native V2), `42c4281` (host-tested checkpoint), and `1b7760f` (latest patcher polish used for this migration). Historical traces stay with those releases. They are not presented as new toolkit measurements.

This migration replaced the installer’s permanent feature toggles with INI flags and moved the two changes into the DLL's native mutation transaction. The loader now requires the corresponding disk bytes to be clean. Fresh live observations recorded the original bytes at the loaded menu, followed by enabled bytes in process memory during an activity, with the original executable hash unchanged throughout.

No Frida probe was used for this migration's live smoke check. External reads used read-only process-memory access after normal startup. The same configured Megacoaster route showed its 2 mph speed limit, and derailments were enabled through the game's settings.

The original VM issue where the Derailments checkbox did not persist was observed again before gameplay patches were installed. The cause is not established; it is not attributed to the toolkit. Tests explicitly enabled the setting before starting the activity.

See [validation](release-validation.md) for exact scope and [architecture](native-runtime.md) for ownership and startup constraints. Borderless mode remains separate future work. dgVoodoo already offers relevant window options; compare that baseline before introducing new window hooks.
