# Paired infrastructure, forward monitor and physical tracks

`capture_infrastructure_transitions.py --paired` now reads these three surfaces in successive phases of each sample. The outer read window includes all phases; the monitor retains its own clock endpoints and iterator reread. This is not an atomic snapshot. Copies and hashes of all seven probe dependencies accompany each new capture; earlier captures are unchanged.

## Completed stationary-player experiment

`captures/paired-player-crossing-01` completed normally: 601 samples, zero outer or nested errors, 35 initially paused samples, simulation clock 73997.5390625 to 74280.59375. The directory name expresses the intended experiment, not its outcome. Maximum complete read duration was 0.156281200 seconds; this is not a measurement of gameplay overhead.

The player never moved: all sampled speed values were zero, all 23 abstract records stayed on node 305 with fixed distances 10536.568359375 to 10973.1484375. All 601 forward-monitor samples had distance 882.1513671875, iterator index 46, normal head 94419988, definition 51529832, aspect 7 and flags 32768. Each head/definition pair joined uniquely to infrastructure database item 318, with zero aspect disagreements. Origin and iterator rereads were stable. This strengthens stationary continuity only; moving distance refresh and player node crossing remain unvalidated.

The 22 AI abstract records remained on node 310 and continued advancing. The separately read physical registry changed from 45 cars/two trains in sample 158 (74059.328125 to 74059.4375) to 23 cars/one train in sample 159 (74059.8203125 to 74059.9375). This repeats the physical-removal versus persistent-service distinction; it does not establish a lifetime-safe identity scheme or prove the exact removal instruction/time. The full abstract-record set remained 45, with no node crossings, identity inconsistencies or route-map changes. Four infrastructure signal-record changes were retained separately.

Normal controls reduced throttle from N2 to Idle and stepped the train brake from emergency through continuous service and suppression into Self Lap 98%. Brake pipe and equalizing reservoir stayed at zero, cylinder pressure at 85.20245361328125 PSI. Two vertical cab drags did not release it. After the capture finished, a horizontal drag intended for the brake visibly changed the power/dynamic-brake controller to Setup instead. No train movement followed. These mouse coordinates are not a reliable brake-control method and should not be reused as one.

The final separate paused capture `paired-control-attempt-final-paused-01` confirms clock 74360.5859375, paused flags 1 before/after, player speed zero, 23 cars and no sampled derailment flags; monitor unchanged. There is an uncaptured tail between the series and this snapshot. Cab sampling reports throttle and dynamic-braking raw values zero; the preceding UI displayed Setup, so do not infer the full controller mode from those two floats alone. No game memory, assets, settings or saves were written. All capture jobs ended.

## Reproduction and limits

Run `analyse_infrastructure_transitions.py`, `analyse_presence_crossings.py` and `analyse_paired_infrastructure.py`, each with `paired-player-crossing-01`. Their summaries record the source SHA256 `53b7a4d6185bebe405e4ac189bbefb742c8d7577ec4e242fe104e8aa77d07d82`. The paired analyzer recursively retains nested errors rather than relying only on the capture's top-level error count.

No candidates were added: the inventory remains 920. Next moving validation requires a verified brake-release method, then short monitoring intervals around the reachable player boundary. Another stationary capture cannot resolve that gap. The broader discovery handoff must distinguish fields already discovered from runtime transitions still untested, without ranking or discarding candidates.
