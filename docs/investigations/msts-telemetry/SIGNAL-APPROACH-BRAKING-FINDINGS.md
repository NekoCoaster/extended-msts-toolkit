# Controlled stop before the player signal

Normal UI resumed the preferred Grain Train Through the Night fixture from its external-view pause at73871.1953125. Installed diesel.txt maps Backspace to EmergencyStopToggle;the exact declaration/hash is retained in emergency-binding-provenance.json. Backspace was pressed once,then1selected cab view,and Escape paused after observing0.0mph,zero pipe/equalizing pressure,approximately85PSIcylinder and a Penalty Brake indicator. These are input/observed-state associations,not proof of every internal emergency subsystem.

read_brake_series.py retained1268samples,808paused and460running,zeroerrors,clock73871.1953125..73905.859375. Selector mode4(handle0) changed to100000hex(handle0.9499999881) at first sampled clock73879.7109375. First sampled zero speed73885.953125;speed range0..5.62776184082m/s. Input wall time was not recorded inside the sampler,so these are sampled state transitions,not exact command latency or stopping duration.

Player23cars:pipe range0..90PSI,cylinder0..85.2024536133PSI. AI22cars remain present throughout with sampled pipe90/cylinder0. All owner rereads agree,though170samples span changing clock values;the stream is not atomic or a measured propagation-speed experiment. AI unchanged brake caches are not proof of independently simulated AI braking or absent forces. analyse_signal_approach_emergency.py preserves the reproducible summary and final pause.

Separate immutable approach-stopped-signal-01 snapshot confirms paused73905.859375,speed0,next normal signalindex46,aspect0,distance481.982421875metres,stable iterator andclock. No failed-activity screen was observed. Throttle remains0.25(cabN2),traction current0,brakes applied. Signal passage has not occurred. No saves/assets/settings or game memory were written;the original Alerter option was not changed.

Next: reduce throttle to Idle and establish emergency reset/train-brake release using the observed controls while capturing selector/pressure state. Prior Acela release required many semicolon steps;that does not establish the present diesel notch sequence. Keep the player stopped while observing the oncoming AI and signal clearance before attempting passage. Reobserve current UI before input;last verified screen is cab Escape pause menu. This closes a reliable emergency-stop control observation for this fixture,not the original successful signal-crossing gap.


## Emergency reset attempt and signal clearance while stopped

Normal UI sequence: resume,twoA presses(N2->N1->Idle),Backspace,three separate semicolon presses. Cab displayed Continuous Service,Suppression,Self Lap98%;penalty-brake indication cleared after leaving emergency. An oncoming AI locomotive and container wagons visibly passed the stationary cab. Leftward and upward drags from the observed train-brake handle did not change the final self-lap setting or release pressures. Installed dash9.cvf TRAIN_BRAKE declaration andhash retained in diesel-brake-cab-provenance.json;declaration alone does not establish mouse axis/scaling. Do not repeat these ineffective drags.

diesel-emergency-reset-01:3316samples,1108paused,zeroerrors,clock73905.859375..74078.3359375,speed0throughout. Modes100000hex->80000->40000->1000;handle0.95->0.9->0.85->0.8375000358. Two snapshots pair an updated handle with the previous mode before a later sample sees the new mode;732clock-crossing reads reinforce asynchronous interpretation. No exact input latency claim. Final mode1000,self-lap98%,pipe command0. Cab pressure remains pipe/equalizing0,cylinder85.20245PSI. Backspace reset alone cannot be credited with the cleared indicator because no precisely timestamped intermediate state was retained.

Bracketing signal snapshots:at73905.859375 signal46 aspect0,flags0,speed0;at74078.3359375 same signal46 aspect7,flags32768,aspect speed-1. Distance481.982421875metres unchanged and player speed0. The AI passed during this interval,but exact clearance time and exclusive causal attribution are not measured. Do not interpret aspect speed-1 as negative permitted speed. This closes an additional stopped-player signal-state transition observation,not successful player passage.

Final UI verified cab Escape pause menu,Idle throttle,forward reverser,brakes applied. Next experiment should use verified keyboard decrements from raw0.8375 toward the release notch,with a fresh bounded capture;many steps may be needed. Signal clearance is now observed,so after verified release the approach can proceed under monitoring. Goal remains incomplete;no assets/settings/saves/production changes.


## Confirmed diesel release and rollback

From pausedIdle/SelfLap98%,normal UI resumed,one semicolon decrement showedSelfLap95%,then a fixed44semicolon sequence reached Released. Pipe/equalizing pressure rose to90PSI and cylinder indication fell to0. Player began rolling with throttleIdle. N1 was selected after this pressure recovery,but signed speed later showed negative motion while forward signal distance increased. Cab speed showed a positive magnitude,so it cannot independently establish direction. EmergencyStop was applied to arrest rollback,then throttle returnedIdle and Escape paused. No forward signal passage occurred.

Read-only brake and signal series retain the release and second application,including final paused intervals. analyse_diesel_release_rollback.py summarizes each series separately;their start times differ. Input times are not embedded in the sampler,so timing claims use sampled state only. The signal remainsindex46/aspect7;its distance increases to699.42578125metres. UI forward reverser remained displayed;that is commanded direction,not actual motion direction.

Sampled traction current remains0 while throttle values include0.125(N1). The reason is unresolved;do not attribute backward motion solely to grade,insufficient power or a specific safety latch without checking that path. Brake release itself is demonstrated by selector and pressure changes. Negative speed/increasing distance provide direct rollback evidence. Next attempt must establish actual traction while holding the train,then coordinate brake release;anotherIdle release would repeat the known rollback condition.

Final last verified UI is cab Escape pause menu,clock74229.078125,speed0,Idle,brakes applied,signal46/aspect7 at699.4258m. Original assets/settings/saves and NEMT production remain unchanged.

Final analysis:5658brake samples and1788signal samples,zeroerrors. Release mode4 first sampled74122.3984375;all23player cylinders first simultaneously sampled0at74135.59375;emergency mode100000hex at74188.265625. Signed speed range-6.09222507477..0.00826698262m/s. Signal46/aspect7 throughout its stream,distance481.0546875..699.42578125m.429brake clock-crossing reads,zeroowner reread differences;no atomicity claim.
