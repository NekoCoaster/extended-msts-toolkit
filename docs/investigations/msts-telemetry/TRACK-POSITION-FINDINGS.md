# Track position discovery checkpoint

26 September 2026. Independent read-only research; game remained paused.

## Native representation

Vehicle track record is car+0x128, size 0x68. Service front-position record is service+0x4c; service+0xb4 is another position record requiring exact endpoint semantics. Native 0x5b277e advances a record along nodes and sections, preserving direction and distances. This gives track-relative location independently of body XYZ.

Record fields: node pointer +0, section ordinal +4, section pointer +8, direction +0xc, distance along node +0x10, distance within section +0x14, angle candidates +0x18, local track reference position +0x48. Node section base is +0x18, count +0x1c, total length +0x28; section stride 0x40. Verify the section pointer equals node section base plus ordinal*0x40.

Section fields: geometry definition uint16 +0, signed tile pair +0x18/+0x1c, tile-relative XYZ +0x20. Definition index addresses the geometry table at [[0x80a118]+0xc] with stride 0x18. Full geometry semantics and route-file IDs remain to map.

## Origin mapping

Assembly 0x5b3fad subtracts signed globals 0x79d118 and 0x79d11c from section tile indices, multiplies each by float constant 2048 at 0x76e48c, and adds section-local offsets. This yields local X/Z used by track traversal. The high-level decompiler misses the global subtractions inside register arguments; assembly is authoritative.

Candidate inverse: route X = local X + 2048*originTileX; route Z = local Z + 2048*originTileZ. Keep Y separately, use float64 for derived large coordinates, and sample origin before/after. These are MSTS route-grid coordinates, not latitude/longitude. Dynamic origin-crossing validation remains outstanding; do not claim it has passed.

## Paused observations

`track-paused-01` has 45 vehicles, zero read errors and zero section-pointer mismatches. Simulation time and origin remained stable. Origin tile was (-12560,14766). Player first car occupied node 113456892, section 95 of 106, distance 10894.758789 m along node and 18.441679 m within section. Its section origin tile matched the current origin.

AI first car occupied node 113456828, section 85 of 101. Its section-origin tile was (-12560,14767), already in the adjacent tile, with Z offset -873.041992. Applying the native 2048-m translation places that section near the observed track point, consistent with traversal along it. This tests the tile-offset relationship within one fixed-origin sample, not continuity through an origin change.

Body-minus-track differences across all cars: X -0.04790 to -0.01457 m; Y 2.01672 to 3.97791 m; Z 0.01782 to 0.09668 m. Preserve both reference points. The difference is not proof that either reading is wrong, nor a universal fixed correction. Vehicle-centre/track-centre conventions need explicit tracing.

Pass14 verifies all 706 exported instructions / 2574 bytes in its three functions against disk and live process with zero differences/errors. This includes the conversion/traversal evidence; it is not a global binary-identity claim.

`read_track.py` preserves raw record bytes and reader copies; `track-summary.json` summarizes this capture. The inventory adds 14 direct candidates and one derived coordinate candidate. Next validate movement through section/node boundaries and origin shifts, map native track IDs to route files, and establish gradient/curvature/orientation conventions and detached/derailed applicability.
