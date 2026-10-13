# Departure with unfinished passenger loading

2026-10-10 Tokyo-Hakone Passenger Activity Tutorial, Setagaya Daita/platform70. Here early departure means leaving before loading finishes; the train was already later than its scheduled departure.

Accepted ENTER starts loading with UI1:30, flags0to2 and recorded arrival65508.5234375. The capture includes a row with arrival/flag already written but active/countdown still0,followed by active1 and remaining89.875. This intermediate observation reinforces that sampling fields sequentially does not provide an atomic transaction.

Last active sample65526.6484375 has71.875seconds remaining. At65526.7734375 active clears,remaining becomes0,flags change2to0x1a and recorded departure becomes65526.7734375. Selected record initially remains Setagaya Daita56244720; at65526.8984375 it advances to Gotokuji56244800 with the former record in previous. UI subsequently shows loading00:00 and actual departure18:12:07. Zero remaining therefore does not establish successful loading completion. Prior normal-expiry evidence has flags0x62 then departure0x6a; this fixture lacks the completion/cue bits and adds bit0x10.

## Native corroboration and limits

Player processor00586f58 compares absolute service speed+138 through00587c02 with float0.05000000074505806 at00758434. With boarding active and ordinary finite magnitude not below this threshold, the branch ORs record+1e bit0x10 at0058749c,clears activity+370,ORs departure bit8,writes day clock to record+10 at005874da,and clears activity+374. The native caller reads service speed. Adjacent sampled service speeds are0.0640310645 and0.1056264341m/s,already above the0.05threshold in the preceding active sample;this confirms that read order/update cadence prevents treating the bracket as an exact speed-threshold crossing. Sampled train speed is not interchangeable for exact branch timing. The next sampled selection advance is consistent with the ordinary departure/successor path; no instruction invocation was traced.

Fresh exported-range comparison for00586f58 and00587c02 covers611instructions/2281bytes,0disk/live mismatches and0errors. Files are in `captures/early-departure-native-20261010-01`,with final report in the sibling byte-verification JSON. The initial incorrect8byte interpretation of the threshold is preserved as `initial-wrong-double-interpretation.json`; assembly explicitly uses FCOMP float,so the corrected4byte value in `speed-threshold.json` supersedes it. This is a type correction,not a changed game value.

Reproduce analysis with `python analyse_early_departure.py` using `captures/tokyo-early-departure-20261010-01/samples.jsonl`; it retains the service speed alongside train speed and produces `early-departure-20261010-summary.json`. Raw record bytes,probe sources,metadata and UI observation are retained. Quality checks do not prove atomicity. No global activity success/failure,evaluation score,AI loading behavior,exact speed-boundary equality,or general loading-duration formula claim.

Final player state: paused65562.3984375,speed0,throttle0,emergency brake applied. All research remains independent of production NEMT.

Final capture totals:1764samples,0errors,14clock-crossing reads,0flagged service/list/record instability and177active-loading samples. These checks are limited consistency evidence,not atomicity proof.
