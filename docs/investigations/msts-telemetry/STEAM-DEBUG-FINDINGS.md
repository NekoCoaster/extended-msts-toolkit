# Steam system debug telemetry

The steam branch of native debug display0060997a supplies19 additional individually mapped candidates. `map_steam_debug.py` preserves the reviewed source offsets and installed native strings in `steam-debug-fields.json`. `read_steam_debug.py` reads them only after validating a steam player context through the existing exact-image reader. The debug formatting code is evidence of intended meaning, not proof of physical correctness, rate units or independent AI simulation.

## Source map

| Candidate | Base/offset | Native label | Units/limits |
|---|---|---|---|
| water_mass | lead+0x2ce | Water mass: %.0f Ib | lb |
| generation_rate | lead+0x316 | Steam gen rate: %.0f | unresolved rate unit |
| usage_rate | lead+0x312 | Steam usage rate: %.0f | unresolved rate unit |
| cylinder_rate | lead+0x31a | Steam cylinder rate: %.0f | unresolved rate unit |
| exhaust_usage_rate | lead+0x31e | Exhaust steam usage rate: %.0f | unresolved rate unit |
| wheel_omega | lead+0x2b2 | Wheel omega: %.02f | angular speed; unit unresolved |
| smoke_colour | lead+0x32a | Smoke colour: %.02f | native scalar; range unresolved |
| smoke_release_rate | lead+0x332 | Smoke release rate: %.02f | unresolved rate unit |
| priming | lead+0x336 | Priming: %.02f | native scalar; unit unresolved |
| blowback | lead+0x33a | Blowback: %.02f | native scalar; unit unresolved |
| critical_blowback | lead+0x296 mask 0x20 | Critical Blowback! %.02f | boolean |
| tender_water_capacity | engine_definition+0x1de | Tender water mass: %.0f / %.0f Ib | lb |
| tender_coal_mass | lead+0x2e2 | Tender coal mass: %.0f / %.0f Ib | lb |
| tender_coal_capacity | engine_definition+0x1e2 | Tender coal mass: %.0f / %.0f Ib | lb |
| coal_burn_rate_raw | lead+0x32e | Coal burn rate: %.0f / %.0f Ib | rate timebase unresolved |
| energy_output | lead+0x306 | Energy output: %.02f | native energy/output unit unresolved |
| wheel_slip | lead+0x84 mask 0x1 | Engine wheel slip! | boolean |
| usage_exceeds_exhaust_limit | lead+0x296 mask 0x100 | steam usage > exhaust limit! | boolean |
| maximum_steam_rate | lead+0x4ae | max steam rate (display 3): %.02f,usage rate %.02f | unresolved rate unit |

## Evidence and important qualifications

Snapshot `captures/steam-debug-paused-01/steam-debug.json` observes paused time36268.28125, unchanged train/lead/controller/definition context, all19 reads successful. Water mass2921.347412, steam generation7293.797363, usage1500.694336, cylinder/exhaust rates0, smoke colour0.684158444, smoke release1.039143801, priming/blowback0, tender coal18000 and loaded coal capacity18000. Loaded tender water capacity50000 matches the current tender-water raw50000 from the cab probe. Maximum steam rate4ae is0 in this stationary context; zero alone does not establish whether this is a working limit, stale scratch value or inactive display state. Warning bits are false. No new control transition or rate timebase test was performed in this snapshot.

The native string77195c says `Tender water mass: %.0f / %.0f Ib`, taking lead+2de then engine-definition+1de. This resolves the stored quantity as pounds by native labeling. The cab conversion raw/10 is therefore its own mass-to-volume approximation; it does not redefine the raw field as gallons. Pressure strings771c94,771c48,771c00 explicitly label boiler, chest and steam-heat values in PSI. These strengthen existing cab candidates without adding duplicates.

The coal-burn line is internally inconsistent: string7718c0 says `Coal burn rate: %.0f / %.0f Ib`, but the first argument is tender-coal mass+2e2, while the second is+32e. Preserve+32e as a rate candidate with unresolved timebase; do not present the two formatted values as actual/maximum burn rates. Similarly the last line calls+31a usage rate even though an earlier line names it cylinder rate. The reviewed mapping keeps the earlier specific name and records+4ae as a tentative maximum steam rate.

Wheel omega is read directly from lead+2b2, distinct from the existing derived rolling-speed/radius estimate; units and slip behavior still need a moving steam run. Wheel-slip bit0 at lead+84 controls the warning. Critical blowback uses lead+296 bit0x20; usage-exceeds-exhaust-limit uses bit0x100. These are labels attached to native conditions, not events induced or observed firing in this test.

Pass82 provides the assembly and instruction verification. Its known live call patch at0060c996 lies outside these source reads; do not claim the complete routine is unchanged. All current mappings are player steam readings. Do not extrapolate the engine union to diesel/electric or assume AI has the same steam systems. Producers, injector flows, automatic firing, rate units, temperature units and controlled dynamic behavior remain open.

See STEAM-PRODUCER-FINDINGS.md for generation persistence, pressure integration and the exhaust warning producer; dynamic branch execution remains untested.
