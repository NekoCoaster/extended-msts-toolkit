# Player node transitions and AI cap initialization

The preferred grain activity continued from the post-signal paused state. Normal UI resumed, reduced N4 to Idle with four A inputs, coasted, and paused at day-seconds 74596.765625. Final signed speed is 10.755123138427734 m/s (cab 24 MPH), brakes released. Resume continues a moving train. No assets, settings, saves or game memory were written.

`capture_player_track_caps.py` pairs existing read-only track, signal/cab and finite-input speed-cap readers. Exact probe dependencies and hashes are retained under `captures/player-track-caps-moving-01`. Reproduce analysis with `python analyse_player_track_caps.py player-track-caps-moving-01`. `post-signal-track-paused-01` is the separate preflight snapshot. The full reads are sequential, not atomic; each sample includes ending clock, player pointer and origin checks. Service tracks and physical car tracks are different reference points.

## Physical node changes

All physical snapshots contain the 23-car player train; the cap reader separately enumerates three services. Eight matched player car/body pairs change node from 114971836 to 114971900 between day-seconds 74422.4765625 and 74439.1015625. Their direction fields change 1 to 0 and node distances change from approximately 11941–11946 m to 6098–6103 m. Positive player speed continues. This supplies representative player car node-boundary evidence; node-local direction is not a universal forward/reverse indicator, and node distance is not cumulative route mileage.

The leading car and service were already on the new node at capture start. Do not describe these eight events as a captured locomotive or service node crossing, or claim every car crossed during this run. Section changes may skip intervening sections between samples. Matching session addresses are not a portable identity guarantee.

## AI activation and cached cap validity

AI service 3 at address 55473360 changes between samples 192/193 (74460.3359375 to 74460.6875): update gate 0 to 1, flags 4 to 20 decimal, posted cap -1 to 13.411199569702148 m/s, effective cached cap 0 to the same positive value. The other two inputs remain -1. Before this transition the finite-input selection formula returns route fallback 26.822399139404297 while the retained effective cap is zero; these 193 mismatches all have update gate zero. Afterward the cache agrees with selection from the posted cap. The other AI has gate zero and an agreeing retained cap, so gate zero alone does not imply zero, invalid arithmetic or missing service.

The player cap remains 17.88159942626953 m/s throughout, with no player cap transition. This AI observation is consistent with the previously traced initialization/backward-search producer; it does not establish an observed speedpost crossing or exact producer invocation. Preserve activation state and negative sentinels rather than exporting a recomputed cap as an unconditional live cache value.

## Multiple signal heads

Consecutive samples bracket the next selection changing from node-local head 21 to heads 2–3 at 74583.890625–74584.25, within the same iterator node 114971900/direction 1. Old distance 3.9921875 m becomes 3449.130859375 m. Both signal subreads have stable iterator and clock rereads; exact geometric crossing remains unmeasured.

The new normal-function heads have aspects 4 and 0 respectively. The already traced maximum-aspect selection rule chooses head 2/aspect 4, whose aspect-speed metadata is 17.88159942626953 and flags 1; head 3 has aspect-speed zero/flags zero. This is a positive multiple-head fixture for the emulated selector, not independent validation of the rendered monitor, signal appearance or movement authority. Raw per-head aspect, selected aspect, aspect speed and effective service cap remain distinct fields.

## Completed capture checks

721 samples, including 246 paused, have no read/track errors. The 587 sampled section-or-node changes include eight node changes. All 2163 service-cap comparisons are retained; 193 mismatches are confined to pre-activation service 3. There are 184 full-sample clock crossings, zero player-pointer reread differences and zero origin reread differences. These checks qualify coherence; they do not make the samples atomic. Inventory remains 1,039 candidates, with 827 evidence paths and 126 unchanged source assets passing the structural audit.
