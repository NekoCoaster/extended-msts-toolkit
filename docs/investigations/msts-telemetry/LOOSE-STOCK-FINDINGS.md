# Positive loose-stock enumeration fixture

Marias Pass > Setting Out Westbound Pickup (`USA2/ACTIVITIES/yard_one.act`) supplies six configured `WagonsList` activity objects: 5, 3, 1, 16, 13 and 1 vehicles, totalling 39. One singleton is an engine. The activity was selected and loaded through normal MSTS UI. No original assets or existing saves were edited.

The opening operations notebook is paused at day-seconds 39600.76953125. `read_physical_registry.py --pid 33612 --name loose-yard-notebook-01` finds **40 physical vehicles but only one train-owned vehicle**, the player GP38-2. The remaining 39 objects have null train owner, valid bodies with matching body-owner pointers, registration bit set, stable list/class/body rereads and reciprocal list links. The separate manager survey counts its five lists as 0, 52, 1342, 40 and 1. In particular the first list is still empty; it must not be labelled the static-consist list from speculation.

The 39 objects outside train chains form six connected components through car+0xa0/+0xa8, with sizes matching the six configured cuts. There are 38 native wagon kinds 0x4000d and one native engine kind 0x4000e. Every component has reciprocal car links; each multi-car group has two endpoints, and each singleton has zero links. All 39 linear velocity vectors are zero, resting flags are set and derailment flags are clear in this paused snapshot.

This is positive evidence that the independent physical-object registry covers loaded loose rolling stock that is omitted by the train registry. A null car+0x98 does **not** mean no usable vehicle/body/connection telemetry. Train-based enumerators are incomplete for this fixture. The native object IDs are separately retained; activity IDs 32768 and above are not automatically those native object IDs.

`analyse_loose_yard.py` reproduces the graph comparison from the retained registry and activity copy, writing `loose-yard-summary.json`. Component size agreement and the fixture context support loose-stock applicability; an exact per-cut activity-ID/asset/native-ID join has not been established. This does not validate physical detachment/coupling transitions, remote unloaded consists, moving loose vehicles, or every vehicle-system field. Address reuse across the activity reload is possible; do not carry the grain run's addresses into this fixture.

## Grain checkpoint preservation and current state

Normal UI Save Activity created `C:/MSTS/saves/USA2/evegrain_27092026_184329.sav`, 124886 bytes, SHA256 `6064ec5975dca19d0d392df318bd1b15c432381ab19ca5f3cdf4d1c5f17c6010`. The original earlier `evegrain_27092026_051532.sav` still matches its prior recorded hash. Copies of the new save and yard activity plus provenance are under `captures/loose-fixture-provenance-01`. UI reported save success; the new save has not been reloaded, so complete restoration is unverified. Exiting the grain activity displayed the expected early-exit evaluation before activity selection.

MSTS remains in the yard activity's opening paused notebook, speed zero. Reobserve before input. This fixture is suitable for later coupling/ownership-transition tests, while the grain save retains a resumption point for route/traffic research.
