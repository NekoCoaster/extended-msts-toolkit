# Observed native save and reload

This supersedes the earlier statement that no save/load had been exercised. One normal UI save/reload succeeded in Grain Train Through the Night. It validates selected identity and state behavior for this fixture, not every saved field, AI physical state or future load.

The pre-save read found a paused player train at74360.5859375, throttle0, reverser1. The installation contained no `.sav` files. Clicking Save Activity in the pause menu produced a success message and a new `C:/MSTS/saves/USA2/evegrain_27092026_051532.sav`:124746bytes, SHA256787f435189dcd5b645c3f448070d5d94e42330f8bca5275555d8e75b1b915a9d. A copy and provenance are retained under captures/save-generated-01. The immediate post-save snapshot has the same clock, controls, train pointer and full sampled car records. No existing save was overwritten.

The generated file partitions exactly into seven top-level blocks: SaveHeader734bytes, SaveObj33645, SaveTDBs76081, SaveTrItems100, SaveActivity13465, one not-yet-labelled token payload244, and SaveController389. SaveObj contains two SaveEngine,21SaveWagon and one SaveTrain block. The train's226-byte raw range matches the earlier retained paused source exactly; its four saved object IDs also match:200223,200245,200223,FFFFFFFF. Other payloads remain undecoded. This provides direct emitted-byte evidence for part of the previously traced writer schema.

After dismissing the success message, the activity was exited through its menu. The evaluation screen recorded an early exit. Load Saved Activity then listed the newly created Grain Train Through the Night entry under Marias Pass. Selecting it and clicking the Start arrow loaded the saved cab and operations notebook. The game remains paused in that notebook. There was no direct game-memory write or native function invocation.

Before/after comparison by saved vehicle ID:

| Check | Observed result |
|---|---|
| Train numeric ID |400007 before and after |
| Train address |58694560 changed to52260788 |
| Vehicle IDs |Same23IDs |
| Vehicle addresses |All23changed |
| Vehicle position and three orientation vectors |All23exactly equal |
| Angular velocity, angular momentum, mass and body flags |All23exactly equal |
| Derailment/resting predicates |All23equal |
| Reciprocal consist links |Valid before and after |
| Controls |Throttle0, reverser1, type2 preserved |
| Linear velocity/momentum |All23differ at tiny magnitudes; maximum component deltas8.0081e-10m/s and8.5484e-5kg m/s |
| Clock |74360.5859375 before save;74361.2734375 at post-load notebook |

The0.6875-second clock difference and tiny motion differences are not evidence of a restoration defect: sampling was not instantaneous and the UI sequence permitted brief simulation progress. The later pre-load menu sample had clock74366.3203125, while the loaded state returned near the saved clock. No full exact-state claim is made.

The60-second transition capture has239samples and no outer snapshot exceptions, but96samples contain explicitly recorded registry errors:95invalid-null-address states and one train-ownership mismatch during loading. Those errors must not be reported as a clean239sample registry read. They are expected unavailable/transitional observations for this probe, not valid empty-train telemetry. The ownership check caught a partially reconstructed state. A stable registry/load-complete signal still needs work; this single observation does not prove the exact reconstruction instruction running at that moment.

Post-load services contain the player and two AI service records, with no physical AI train. The player service backlink matches the new physical train. Thus this test validates player reload association and retained AI service presence, not AI train rephysicalization or AI state fidelity. `analyse_save_reload.py` reproduces the file partition and comparisons from retained evidence. It never accesses the live game.

Inventory remains1015. Existing candidates gain runtime lifecycle evidence; raw block bytes are not additional named channels. Original source assets remain protected by the existing126-file hash audit. The research-created save is intentionally retained. Next use this saved fixture for further gameplay tests and investigate the remaining physical-AI, station/crossing and origin-transition gaps.
