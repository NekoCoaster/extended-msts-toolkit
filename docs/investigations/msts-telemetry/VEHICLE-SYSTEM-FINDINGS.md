# Per-vehicle brake and force checkpoint

Executable verification: pass26 checks1757 exported instructions/6978 bytes. All disk bytes match the analysis image. Three instruction records differ at0x62ad6a..0x62ad6d: the function entry is a live jump patch followed by padding. This is one patched entry spanning three exported instructions, not three independent features. Coupling/force code below that entry is native static evidence; its runtime path must be treated as potentially wrapped. Other exported functions in the pass have no detected differences. See pass26-byte-verification.json.

Read-only sample vehicle-systems-running-01 contains the 23 stopped player vehicles during advancing simulation. The first AI had already lost its physical representation, so this sample does not validate AI brake/force population.

Lead cylinder pressure car+0x230=85.20245 PSI, pipe car+0x238=0. Last wagon cylinder=76.22182, pipe=0. Per-car values therefore carry information beyond the single cab display. No propagation timing or release transition was tested here.

Native writer0x6171f8 associates token0x40196 MaxBrakeForce with definition+0x918. Lead definition=140000 N; wagon=50000 N. The runtime force quantity car+0x22c was170404.9 and76221.82 respectively. It must not be clamped to the configured maximum in telemetry or described as actual wheel/rail force. Consumer0x62c679 passes it through additional adhesion/braking logic. Definition+0x954 is a reference pressure used in scaling, observed70 and50.

Coupling solver0x62d335 computes an endpoint force vector. Caller0x62ad6a stores a norm-derived quantity in car+0x1a0 and compares against definition+0x210, calling native uncoupler0x635dfb when exceeded. The lead read55796.06, trailing unconnected end zero, and configured threshold11000000. Full sign/end conventions and other producer branches remain to verify. No couplings were changed in this research.

Body+0xa0/+0xac are force/torque accumulator candidates; body+0x64 is the world inverse inertia tensor consumed by0x5f6368. Pointer stability is recorded, but snapshot success does not prove solver-phase consistency. On-rail, derailed, sleeping and kinematic-AI paths differ. Existing NEMT derailment modifications mean abnormal-state samples cannot be advertised as stock physics.

`read_vehicle_systems.py` preserves offset-labeled raw candidates; `vehicle-system-fields.json` adds10 meaningful candidates. Native evidence: passes24–26. Remaining: pressure propagation/release, actual forces versus requests, adhesion/wheel slip, brake types, signed coupler slack/force, broken and detached graphs, and AI physics depth.
