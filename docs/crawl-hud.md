# Crawling after derailment

Enable **Allow connected engines to crawl after derailment** and click Apply. The panel enables **Remove derailment activity-end message** with it so the session can continue.

Use throttle for speed and reverser for direction. Steam locomotives use the regulator. Crawling activates for eligible derailed powered vehicles and clears when the activity ends. There is no timed trial cutoff.

Connected powered engines contribute using their individual power and force values. Eligibility follows the connections MSTS maintains: a car can look separated while the simulator still considers it connected. A disconnected engine no longer receives added thrust from the controlled consist. Unpowered cars do not generate thrust.

Crawling is an arcade feature. It does not put vehicles back on the rails. Throttle also affects the selected derailment drag and pitching effects, and wheel animation follows movement and throttle. At **0×**, added thrust is disabled but these other crawling effects remain enabled.

Pitch suppression follows the train's heading relative to world vertical, so it works consistently when the train is lying on either side or upside down. It reduces nose-up/nose-down rotation while allowing turning and rolling; it does not automatically level the train. Suppression fades when the train points almost straight up or down, where its horizontal heading is ambiguous.

## Strength and HUD

The slider ranges from **0–100×**, with **10×** as the starting value. Use **Bottom left** or **Bottom right** to place the HUD; the default is bottom left.

Press **F5** through the standard red pages until MSTS Bin's white extended display appears. The extra lines show crawl state, strength, added thrust, throttle/regulator, reverser and powered-engine counts. Reverse thrust is displayed with a minus sign. This is the added crawl thrust, not the train's total force.

The HUD is included automatically with crawling. If it overlaps a track monitor or another overlay, choose the other bottom corner or move the other display. Its placement follows the current resolution.
