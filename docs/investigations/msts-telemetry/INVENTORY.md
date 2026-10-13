# Telemetry discovery inventory (work in progress)

{'runtime_direct': 460, 'runtime_derived': 28, 'cab_channels': 68, 'installed_cab_channels': 59, 'config_paths': 511, 'config_leaf_paths': 478, 'config_mixed_paths': 37, 'files_scanned': 143, 'total': 1067}

No priorities or keep/drop decisions. See inventory.json for full provenance and per-field limitations.

| Candidate | Meaning | Evidence status |
|---|---|---|
| simulation.time | Simulation time value; observed near activity seconds since midnight | Distinct day-clock storage traced;UI restart66012.6484375->64800 observed;old value persists into debrief; normal-speed Explore rollover86399.953125->0.078125 with elapsed advancing0.125s; helper00645540 rebuilds day clock from nonzero clock[-4] plus elapsed and subtracts86400 once, then recomputes HMS |
| simulation.step | Simulation frame delta | readable in live captures; semantics partly inherited/static |
| simulation.paused | Pause state | Gameplay/menus observed;result dismissal1->0 precedes teardown;debrief/loading pause0 without active player;restarted briefing1 |
| train.registry | Currently registered train identities; future unspawned services excluded | readable in live captures; semantics partly inherited/static;player coupling and F9 separation validate chain1to6to1 and five loose owners0toPlayerTo0;stored physical count40 |
| train.identity | Native train identifier | readable in live captures; semantics partly inherited/static |
| train.kind_raw | Native train kind byte; player observed 3 and AI 1 | readable in live captures; semantics partly inherited/static |
| train.is_player | Train matches selected player global | readable in live captures; semantics partly inherited/static |
| train.speed | Native signed train speed; compare with per-body speed | readable in live captures; semantics partly inherited/static;forward player next-signal selection transition observed after clearance |
| train.first_car | First car pointer | readable in live captures; semantics partly inherited/static;player coupling and F9 separation validate chain1to6to1 and five loose owners0toPlayerTo0;stored physical count40 |
| train.last_car | Last car pointer | readable in live captures; semantics partly inherited/static;player coupling and F9 separation validate chain1to6to1 and five loose owners0toPlayerTo0;stored physical count40 |
| train.lead_car | Lead/controlled car pointer | readable in live captures; semantics partly inherited/static;player coupling and F9 separation validate chain1to6to1 and five loose owners0toPlayerTo0;stored physical count40 |
| train.service_pointer | Associated service/runtime object; fields not decoded yet | readable in live captures; semantics partly inherited/static |
| car.identity | Vehicle instance address | readable in live captures; semantics partly inherited/static;positive yard fixture has39owner-null loose vehicles outside train chains in6linked components;player coupling and F9 separation validate chain1to6to1 and five loose owners0toPlayerTo0;stored physical count40 |
| car.train_owner | Owning train | readable in live captures; semantics partly inherited/static;positive yard fixture has39owner-null loose vehicles outside train chains in6linked components;player coupling and F9 separation validate chain1to6to1 and five loose owners0toPlayerTo0;stored physical count40 |
| car.links | Connections at both ends | readable in live captures; semantics partly inherited/static;positive yard fixture has39owner-null loose vehicles outside train chains in6linked components;player coupling and F9 separation validate chain1to6to1 and five loose owners0toPlayerTo0;stored physical count40 |
| car.definition | Shared vehicle definition | readable in live captures; semantics partly inherited/static |
| car.asset_directory | Trainset directory/name string | readable in live captures; semantics partly inherited/static |
| car.powered | Definition identifies powered vehicle | readable in live captures; semantics partly inherited/static |
| car.body_pointer | Current integration body pointer | readable in live captures; semantics partly inherited/static;positive yard fixture has39owner-null loose vehicles outside train chains in6linked components;player coupling and F9 separation validate chain1to6to1 and five loose owners0toPlayerTo0;stored physical count40 |
| body.position | Physics-body reference position in local simulation coordinates | live player/AI movement sampled; local body and track reference points compared; clock and producer-phase differences documented;39loose vehicle track records have valid node/section joins and bounded distances |
| body.right | Orientation right basis | readable in live captures; semantics partly inherited/static |
| body.up | Orientation up basis | readable in live captures; semantics partly inherited/static |
| body.forward | Orientation forward basis | readable in live captures; semantics partly inherited/static |
| body.velocity | Stored physics-body linear velocity vector | readable in live captures; semantics partly inherited/static;preserved moving player/AI observations reveal orientation changes with zero stored angular velocity and nonzero position/velocity discrepancies; combined moving player/AI endpoint analysis preserves discrepancies and phase-sensitive outliers; combined moving player/AI comparison supports distinct motion time bases |
| body.angular_velocity | Stored physics-body angular velocity;not universal track-orientation derivative | readable in live captures; semantics partly inherited/static;preserved moving player/AI observations reveal orientation changes with zero stored angular velocity and nonzero position/velocity discrepancies; combined moving player/AI endpoint analysis preserves discrepancies and phase-sensitive outliers; combined moving player/AI comparison supports distinct motion time bases |
| body.momentum | Linear momentum | readable in live captures; semantics partly inherited/static |
| body.angular_momentum | Angular momentum | readable in live captures; semantics partly inherited/static |
| body.inverse_mass | Inverse mass | readable in live captures; semantics partly inherited/static |
| body.flags_raw | Body flags including physical derailment and resting | readable in live captures; semantics partly inherited/static |
| body.derailed | Physical derailment flag | readable in live captures; semantics partly inherited/static |
| body.resting | Resting flag | readable in live captures; semantics partly inherited/static |
| engine.definition | Engine definition | readable in live captures; semantics partly inherited/static |
| engine.max_power | Configured maximum power | readable in live captures; semantics partly inherited/static |
| engine.max_force | Configured maximum force | readable in live captures; semantics partly inherited/static |
| player.control_type | Steam/diesel/electric controller type | Existing1steam/2diesel/3electric mapping;teardown3->0 and restart0->3 observed with controller clearing/rebuild |
| player.throttle | Throttle/regulator fraction | readable in live captures; semantics partly inherited/static |
| player.reverser | Signed reverser setting | readable in live captures; semantics partly inherited/static |
| monitor.event_type | Upcoming track-monitor element type | readable in live captures; semantics partly inherited/static |
| monitor.distance | Distance to upcoming element | readable in live captures; semantics partly inherited/static |
| monitor.radius | Radius associated with element | readable in live captures; semantics partly inherited/static |
| monitor.gradient | Gradient associated with element | readable in live captures; semantics partly inherited/static |
| monitor.desired_velocity | Desired velocity associated with element, not necessarily posted limit | readable in live captures; semantics partly inherited/static |
| monitor.object | Referenced route/signal object identity | readable in live captures; semantics partly inherited/static |
| signal.flags_raw | Referenced signal flags; full aspect mapping unresolved | readable in live captures; semantics partly inherited/static |
| car.mass | Vehicle mass | Implemented in read_live.py; bounded consist aggregate observation retained |
| car.longitudinal_speed | Speed projected along body axis | Implemented stored-vector projection in read_live.py;moving player/AI comparisons retained,not universal trajectory speed validation |
| train.car_count | Number of connected vehicles | Player coupling/separation fixture validates connected chain1->6->1 while physical-list count remains40 |
| train.total_mass | Connected consist mass | 23-car player physics-body sum2551687.039209917 observed beside stored definition aggregate2551687.0 |
| car.speed_magnitude | Total 3D speed | Mathematical stored-vector magnitude;moving comparisons expose producer-phase and clock differences |
| car.acceleration | Sampled acceleration | Derived hypothesis; distinct player/AI clock comparisons invalidate assuming one universal gameplay-time denominator |
| car.heading_pitch_roll | Orientation angles | Orientation-angle hypothesis;no universal Euler convention or HUD agreement established |
| train.relative_motion | Relative train separation and closing speed | Derived relative-motion hypothesis;origin rebase and stored-vector discrepancies constrain interpretation |
| train.lifecycle_events | Spawn/despawn, coupling/splitting and player selection changes | Representative player coupling/separation,AI physical removal and player reload identity behavior observed |
| car.wheel_rotation_estimate | Rolling wheel speed estimate | Kinematic hypothesis only;native stored wheel rate and animation callbacks are separately traced |
| cab.ALERTER_DISPLAY | alerter display native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.AMMETER | ammeter native cab input/display channel | native diesel current producer traced; after-acknowledgement N1 cab225amps matches stored225.0000152588;not rail-force validation |
| cab.ASPECT_DISPLAY | aspect display native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.BELL | bell native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.BLOWER | blower native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.BOILER_WATER | boiler water native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.BRAKE_CYL | brake cyl native cab input/display channel | native diesel pressure producer traced; paused pressures matched cab display; broader dynamics require the relevant pressure/control capture |
| cab.BRAKE_PIPE | brake pipe native cab input/display channel | native diesel pressure producer traced; paused pressures matched cab display; broader dynamics require the relevant pressure/control capture |
| cab.CLOCK | clock native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.CPH_DISPLAY | cph display native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.CP_HANDLE | cp handle native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.CUTOFF | cutoff native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.CYL_COCKS | cyl cocks native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.DAMPERS_FRONT | dampers front native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.DIRECTION | direction native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.DIRECTION_DISPLAY | direction display native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.DYNAMIC_BRAKE | dynamic brake native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.DYNAMIC_BRAKE_DISPLAY | dynamic brake display native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.EMERGENCY_BRAKE | emergency brake native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.ENGINE_BRAKE | engine brake native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.ENGINE_BRAKING_BUTTON | engine braking button native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.EQ_RES | eq res native cab input/display channel | native diesel pressure producer traced; paused pressures matched cab display; broader dynamics require the relevant pressure/control capture |
| cab.FIREBOX | firebox native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.FIREHOLE | firehole native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.FRICTION_BRAKING | friction braking native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.FRONT_HLIGHT | front hlight native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.GEARS | gears native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.HORN | horn native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.LINE_VOLTAGE | line voltage native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.LOAD_METER | load meter native cab input/display channel | native diesel branch shares AMMETER producer;no independent LOAD_METER display agreement established by the cited pressure snapshot |
| cab.MAIN_RES | main res native cab input/display channel | native diesel pressure producer traced; paused pressures matched cab display; broader dynamics require the relevant pressure/control capture |
| cab.OVERSPEED | overspeed native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.PANTOGRAPH | pantograph native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.PANTO_DISPLAY | panto display native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.PENALTY_APP | penalty app native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.REGULATOR | regulator native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.RESET | reset native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.REVERSER_PLATE | reverser plate native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.SANDERS | sanders native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.SANDING | sanding native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.SMALL_EJECTOR | small ejector native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.SPEEDLIM_DISPLAY | speedlim display native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.SPEEDOMETER | speedometer native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.STEAMCHEST_PR | steamchest pr native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.STEAMHEAT_PRESSURE | steamheat pressure native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.STEAM_INJ1 | steam inj1 native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.STEAM_INJ2 | steam inj2 native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.STEAM_PR | steam pr native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.TENDER_WATER | tender water native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.THROTTLE | throttle native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.THROTTLE_DISPLAY | throttle display native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.TRACTION_BRAKING | traction braking native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.TRAIN_BRAKE | train brake native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.VACUUM_RESERVOIR_PRESSURE | vacuum reservoir pressure native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.WATER_INJECTOR1 | water injector1 native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.WATER_INJECTOR2 | water injector2 native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.WHEELSLIP | wheelslip native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.WHISTLE | whistle native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.WIPERS | wipers native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| config..act:Tr_Activity.Serial | Tr_Activity.Serial configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.Activation_Level | Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.Activation_Level configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.EventTypeLocation | Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.EventTypeLocation configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.ID | Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.ID configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.Location | Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.Location configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.Name | Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.Name configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.Outcomes.ActivitySuccess | Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.Outcomes.ActivitySuccess configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.Outcomes.DisplayMessage | Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.Outcomes.DisplayMessage configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.TriggerOnStop | Tr_Activity.Tr_Activity_File.Events.EventCategoryLocation.TriggerOnStop configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.NextActivityObjectUID | Tr_Activity.Tr_Activity_File.NextActivityObjectUID configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.NextServiceUID | Tr_Activity.Tr_Activity_File.NextServiceUID configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Player_Service_Definition | Tr_Activity.Tr_Activity_File.Player_Service_Definition configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Player_Service_Definition.Player_Traffic_Definition | Tr_Activity.Tr_Activity_File.Player_Service_Definition.Player_Traffic_Definition configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Player_Service_Definition.UiD | Tr_Activity.Tr_Activity_File.Player_Service_Definition.UiD configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Traffic_Definition | Tr_Activity.Tr_Activity_File.Traffic_Definition configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Traffic_Definition.Service_Definition | Tr_Activity.Tr_Activity_File.Traffic_Definition.Service_Definition configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_File.Traffic_Definition.Service_Definition.UiD | Tr_Activity.Tr_Activity_File.Traffic_Definition.Service_Definition.UiD configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.Animals | Tr_Activity.Tr_Activity_Header.Animals configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.Briefing | Tr_Activity.Tr_Activity_Header.Briefing configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.CompleteActivity | Tr_Activity.Tr_Activity_Header.CompleteActivity configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.Description | Tr_Activity.Tr_Activity_Header.Description configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.Difficulty | Tr_Activity.Tr_Activity_Header.Difficulty configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.Duration | Tr_Activity.Tr_Activity_Header.Duration configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.FuelCoal | Tr_Activity.Tr_Activity_Header.FuelCoal configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.FuelDiesel | Tr_Activity.Tr_Activity_Header.FuelDiesel configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.FuelWater | Tr_Activity.Tr_Activity_Header.FuelWater configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.Mode | Tr_Activity.Tr_Activity_Header.Mode configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.Name | Tr_Activity.Tr_Activity_Header.Name configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.PathID | Tr_Activity.Tr_Activity_Header.PathID configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.RouteID | Tr_Activity.Tr_Activity_Header.RouteID configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.Season | Tr_Activity.Tr_Activity_Header.Season configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.StartTime | Tr_Activity.Tr_Activity_Header.StartTime configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.StartingSpeed | Tr_Activity.Tr_Activity_Header.StartingSpeed configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.Type | Tr_Activity.Tr_Activity_Header.Type configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.Weather | Tr_Activity.Tr_Activity_Header.Weather configured value | static configuration extracted; not a live changing value |
| config..act:Tr_Activity.Tr_Activity_Header.Workers | Tr_Activity.Tr_Activity_Header.Workers configured value | static configuration extracted; not a live changing value |
| config..eng:Engine | Engine configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AWSMonitor.MonitoringDeviceAlarmTimeLimit | Engine.AWSMonitor.MonitoringDeviceAlarmTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AWSMonitor.MonitoringDeviceAppliesCutsPower | Engine.AWSMonitor.MonitoringDeviceAppliesCutsPower configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AWSMonitor.MonitoringDeviceAppliesEmergencyBrake | Engine.AWSMonitor.MonitoringDeviceAppliesEmergencyBrake configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AWSMonitor.MonitoringDeviceAppliesFullBrake | Engine.AWSMonitor.MonitoringDeviceAppliesFullBrake configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AWSMonitor.MonitoringDeviceAppliesShutsDownEngine | Engine.AWSMonitor.MonitoringDeviceAppliesShutsDownEngine configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AWSMonitor.MonitoringDeviceCriticalLevel | Engine.AWSMonitor.MonitoringDeviceCriticalLevel configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AWSMonitor.MonitoringDeviceMonitorTimeLimit | Engine.AWSMonitor.MonitoringDeviceMonitorTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AWSMonitor.MonitoringDevicePenaltyTimeLimit | Engine.AWSMonitor.MonitoringDevicePenaltyTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AWSMonitor.MonitoringDeviceResetLevel | Engine.AWSMonitor.MonitoringDeviceResetLevel configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AirBrakesAirCompressorPowerRating | Engine.AirBrakesAirCompressorPowerRating configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AirBrakesAirCompressorWattage | Engine.AirBrakesAirCompressorWattage configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AirBrakesAirUsedPerPoundsOfBrakePipePressure | Engine.AirBrakesAirUsedPerPoundsOfBrakePipePressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AirBrakesCompressorRestartPressure | Engine.AirBrakesCompressorRestartPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AirBrakesHasLowPressureTest | Engine.AirBrakesHasLowPressureTest configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AirBrakesIsCompressorElectricOrMechanical | Engine.AirBrakesIsCompressorElectricOrMechanical configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AirBrakesMainMaxAirPressure | Engine.AirBrakesMainMaxAirPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AirBrakesMainMinResAirPressure | Engine.AirBrakesMainMinResAirPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AirBrakesMainResVolume | Engine.AirBrakesMainResVolume configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.AirBrakesSteamUsageRate | Engine.AirBrakesSteamUsageRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.BasicCoalUsage | Engine.BasicCoalUsage configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.BasicSteamUsage | Engine.BasicSteamUsage configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.BlastExponent | Engine.BlastExponent configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.BoilerEffectivity | Engine.BoilerEffectivity configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.BoilerLength | Engine.BoilerLength configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.BoilerResponsiveness | Engine.BoilerResponsiveness configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.BoilerVolume | Engine.BoilerVolume configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.BrakeCutsPowerAtBrakeCylinderPressure | Engine.BrakeCutsPowerAtBrakeCylinderPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.BrakesEngineBrakeType | Engine.BrakesEngineBrakeType configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.BrakesEngineControllers | Engine.BrakesEngineControllers configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.BrakesTrainBrakeType | Engine.BrakesTrainBrakeType configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.CabView | Engine.CabView configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.CoalBurnage | Engine.CoalBurnage configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.CutoffMaxForward | Engine.CutoffMaxForward configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.CutoffMaxReverse | Engine.CutoffMaxReverse configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.CylinderCocksPowerEfficiency | Engine.CylinderCocksPowerEfficiency configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.CylinderDiameter | Engine.CylinderDiameter configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.CylinderEffectivity | Engine.CylinderEffectivity configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.CylinderStroke | Engine.CylinderStroke configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.CylinderVolume | Engine.CylinderVolume configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Description | Engine.Description configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselEngineIdleRPM | Engine.DieselEngineIdleRPM configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselEngineMaxRPM | Engine.DieselEngineMaxRPM configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselEngineMaxRPMChangeRate | Engine.DieselEngineMaxRPMChangeRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselEngineSpeedOfMaxTractiveEffort | Engine.DieselEngineSpeedOfMaxTractiveEffort configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselEngineStallRPM | Engine.DieselEngineStallRPM configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselEngineType | Engine.DieselEngineType configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselSmokeEffectInitialMagnitude | Engine.DieselSmokeEffectInitialMagnitude configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselSmokeEffectInitialSmokeRate | Engine.DieselSmokeEffectInitialSmokeRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselSmokeEffectMaxMagnitude | Engine.DieselSmokeEffectMaxMagnitude configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselSmokeEffectMaxSmokeRate | Engine.DieselSmokeEffectMaxSmokeRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselUsedPerHourAtIdle | Engine.DieselUsedPerHourAtIdle configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DieselUsedPerHourAtMaxPower | Engine.DieselUsedPerHourAtMaxPower configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DoesBrakeCutPower | Engine.DoesBrakeCutPower configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DoesHornTriggerBell | Engine.DoesHornTriggerBell configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DraftingEffect | Engine.DraftingEffect configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakeHasAutoBailOff | Engine.DynamicBrakeHasAutoBailOff configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesCutInSpeed | Engine.DynamicBrakesCutInSpeed configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesDelayTimeBeforeEngaging | Engine.DynamicBrakesDelayTimeBeforeEngaging configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesEffectAtMaximumFadeOut | Engine.DynamicBrakesEffectAtMaximumFadeOut configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesFadingSpeed | Engine.DynamicBrakesFadingSpeed configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesHigherSpeedCurveExponent | Engine.DynamicBrakesHigherSpeedCurveExponent configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesLowerSpeedCurveExponent | Engine.DynamicBrakesLowerSpeedCurveExponent configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesMaxAirBrakePressure | Engine.DynamicBrakesMaxAirBrakePressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesMaximumEffectiveSpeed | Engine.DynamicBrakesMaximumEffectiveSpeed configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesMaximumForce | Engine.DynamicBrakesMaximumForce configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesMaximumSpeedForFadeOut | Engine.DynamicBrakesMaximumSpeedForFadeOut configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesMinUsableSpeed | Engine.DynamicBrakesMinUsableSpeed configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesNumberOfControllerNotches | Engine.DynamicBrakesNumberOfControllerNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.DynamicBrakesResistorCurrentLimit | Engine.DynamicBrakesResistorCurrentLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Effects.DieselSpecialEffects.Exhaust1 | Engine.Effects.DieselSpecialEffects.Exhaust1 configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Effects.SteamSpecialEffects.CylindersFX | Engine.Effects.SteamSpecialEffects.CylindersFX configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Effects.SteamSpecialEffects.DrainpipeFX | Engine.Effects.SteamSpecialEffects.DrainpipeFX configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Effects.SteamSpecialEffects.SafetyValvesFX | Engine.Effects.SteamSpecialEffects.SafetyValvesFX configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Effects.SteamSpecialEffects.StackFX | Engine.Effects.SteamSpecialEffects.StackFX configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Effects.SteamSpecialEffects.WhistleFX | Engine.Effects.SteamSpecialEffects.WhistleFX configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EmergencyStopMonitor.MonitoringDeviceAlarmTimeLimit | Engine.EmergencyStopMonitor.MonitoringDeviceAlarmTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EmergencyStopMonitor.MonitoringDeviceAppliesCutsPower | Engine.EmergencyStopMonitor.MonitoringDeviceAppliesCutsPower configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EmergencyStopMonitor.MonitoringDeviceAppliesEmergencyBrake | Engine.EmergencyStopMonitor.MonitoringDeviceAppliesEmergencyBrake configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EmergencyStopMonitor.MonitoringDeviceAppliesFullBrake | Engine.EmergencyStopMonitor.MonitoringDeviceAppliesFullBrake configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EmergencyStopMonitor.MonitoringDeviceAppliesShutsDownEngine | Engine.EmergencyStopMonitor.MonitoringDeviceAppliesShutsDownEngine configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EmergencyStopMonitor.MonitoringDeviceCriticalLevel | Engine.EmergencyStopMonitor.MonitoringDeviceCriticalLevel configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EmergencyStopMonitor.MonitoringDeviceMonitorTimeLimit | Engine.EmergencyStopMonitor.MonitoringDeviceMonitorTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EmergencyStopMonitor.MonitoringDevicePenaltyTimeLimit | Engine.EmergencyStopMonitor.MonitoringDevicePenaltyTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EmergencyStopMonitor.MonitoringDeviceResetLevel | Engine.EmergencyStopMonitor.MonitoringDeviceResetLevel configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineBrakesControllerDirectControlExponent | Engine.EngineBrakesControllerDirectControlExponent configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineBrakesControllerEmergencyApplicationRate | Engine.EngineBrakesControllerEmergencyApplicationRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineBrakesControllerEmergencyBrakeTimePenalty | Engine.EngineBrakesControllerEmergencyBrakeTimePenalty configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineBrakesControllerFullServicePressureDrop | Engine.EngineBrakesControllerFullServicePressureDrop configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineBrakesControllerHasProportionalBrake | Engine.EngineBrakesControllerHasProportionalBrake configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineBrakesControllerMaxApplicationRate | Engine.EngineBrakesControllerMaxApplicationRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineBrakesControllerMaxReleaseRate | Engine.EngineBrakesControllerMaxReleaseRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineBrakesControllerMaxSystemPressure | Engine.EngineBrakesControllerMaxSystemPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineBrakesControllerMinPressureReduction | Engine.EngineBrakesControllerMinPressureReduction configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineBrakesControllerMinSystemPressure | Engine.EngineBrakesControllerMinSystemPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineBrakesProportionalBrakeLag | Engine.EngineBrakesProportionalBrakeLag configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.AWS | Engine.EngineControllers.AWS configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.BailOffButton | Engine.EngineControllers.BailOffButton configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.BellToggle | Engine.EngineControllers.BellToggle configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Blower | Engine.EngineControllers.Blower configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Blower.NumNotches | Engine.EngineControllers.Blower.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Brake_Dynamic | Engine.EngineControllers.Brake_Dynamic configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Brake_Dynamic.NumNotches | Engine.EngineControllers.Brake_Dynamic.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Brake_Dynamic.NumNotches.Notch | Engine.EngineControllers.Brake_Dynamic.NumNotches.Notch configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Brake_Engine | Engine.EngineControllers.Brake_Engine configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Brake_Engine.NumNotches | Engine.EngineControllers.Brake_Engine.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Brake_Engine.NumNotches.Notch | Engine.EngineControllers.Brake_Engine.NumNotches.Notch configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Brake_Hand | Engine.EngineControllers.Brake_Hand configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Brake_Hand.NumNotches | Engine.EngineControllers.Brake_Hand.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Brake_Train | Engine.EngineControllers.Brake_Train configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Brake_Train.NumNotches | Engine.EngineControllers.Brake_Train.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Brake_Train.NumNotches.Notch | Engine.EngineControllers.Brake_Train.NumNotches.Notch configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Combined_Control | Engine.EngineControllers.Combined_Control configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Cutoff | Engine.EngineControllers.Cutoff configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Cutoff.NumNotches | Engine.EngineControllers.Cutoff.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.CylinderCocks | Engine.EngineControllers.CylinderCocks configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.DampersBack | Engine.EngineControllers.DampersBack configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.DampersBack.NumNotches | Engine.EngineControllers.DampersBack.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.DampersFront | Engine.EngineControllers.DampersFront configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.DampersFront.NumNotches | Engine.EngineControllers.DampersFront.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.DirControl | Engine.EngineControllers.DirControl configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.EmergencyStopResetToggle | Engine.EngineControllers.EmergencyStopResetToggle configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.EmergencyStopToggle | Engine.EngineControllers.EmergencyStopToggle configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.EngineBrakingButton | Engine.EngineControllers.EngineBrakingButton configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.FireDoor | Engine.EngineControllers.FireDoor configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.FireDoor.NumNotches | Engine.EngineControllers.FireDoor.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Gear | Engine.EngineControllers.Gear configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Gear.NumNotches | Engine.EngineControllers.Gear.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Gear.NumNotches.Notch | Engine.EngineControllers.Gear.NumNotches.Notch configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Headlights | Engine.EngineControllers.Headlights configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.HeatingTap | Engine.EngineControllers.HeatingTap configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.HeatingTap.NumNotches | Engine.EngineControllers.HeatingTap.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.HighLowAcceleration | Engine.EngineControllers.HighLowAcceleration configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.HighLowAcceleration.NumNotches | Engine.EngineControllers.HighLowAcceleration.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Horn | Engine.EngineControllers.Horn configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Injector1Steam | Engine.EngineControllers.Injector1Steam configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Injector1Water | Engine.EngineControllers.Injector1Water configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Injector1Water.NumNotches | Engine.EngineControllers.Injector1Water.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Injector2Steam | Engine.EngineControllers.Injector2Steam configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Injector2Water | Engine.EngineControllers.Injector2Water configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Injector2Water.NumNotches | Engine.EngineControllers.Injector2Water.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.PantographToggle1 | Engine.EngineControllers.PantographToggle1 configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Regulator | Engine.EngineControllers.Regulator configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Regulator.NumNotches | Engine.EngineControllers.Regulator.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Sanding | Engine.EngineControllers.Sanding configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Shovel | Engine.EngineControllers.Shovel configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Shovel.NumNotches | Engine.EngineControllers.Shovel.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.SmallEjectorOrCompressor | Engine.EngineControllers.SmallEjectorOrCompressor configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Throttle | Engine.EngineControllers.Throttle configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Throttle.NumNotches | Engine.EngineControllers.Throttle.NumNotches configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Throttle.NumNotches.Notch | Engine.EngineControllers.Throttle.NumNotches.Notch configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Vigilance | Engine.EngineControllers.Vigilance configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.WaterScoop | Engine.EngineControllers.WaterScoop configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Whistle | Engine.EngineControllers.Whistle configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineControllers.Wipers | Engine.EngineControllers.Wipers configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineOperatingProcedures | Engine.EngineOperatingProcedures configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.EngineVariables | Engine.EngineVariables configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.ExhaustLimit | Engine.ExhaustLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.GearBoxBackLoadForce | Engine.GearBoxBackLoadForce configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.GearBoxCoastingForce | Engine.GearBoxCoastingForce configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.GearBoxDirectDriveGear | Engine.GearBoxDirectDriveGear configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.GearBoxDownGearProportion | Engine.GearBoxDownGearProportion configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.GearBoxEngineBraking | Engine.GearBoxEngineBraking configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.GearBoxMaxSpeedForGears | Engine.GearBoxMaxSpeedForGears configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.GearBoxMaxTractiveForceForGears | Engine.GearBoxMaxTractiveForceForGears configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.GearBoxNumberOfGears | Engine.GearBoxNumberOfGears configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.GearBoxOperation | Engine.GearBoxOperation configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.GearBoxOverspeedPercentageForFailure | Engine.GearBoxOverspeedPercentageForFailure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.GearBoxUpGearProportion | Engine.GearBoxUpGearProportion configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.HeadOut | Engine.HeadOut configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.IdealFireMass | Engine.IdealFireMass configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.InjectorLimits1 | Engine.InjectorLimits1 configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.InjectorLimits2 | Engine.InjectorLimits2 configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.InjectorSizes | Engine.InjectorSizes configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.InjectorTypes | Engine.InjectorTypes configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.IsTenderRequired | Engine.IsTenderRequired configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxBoilerOutput | Engine.MaxBoilerOutput configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxBoilerPressure | Engine.MaxBoilerPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxContinuousForce | Engine.MaxContinuousForce configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxCurrent | Engine.MaxCurrent configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxDieselLevel | Engine.MaxDieselLevel configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxFireMass | Engine.MaxFireMass configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxForce | Engine.MaxForce configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxOilPressure | Engine.MaxOilPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxPower | Engine.MaxPower configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxSandingTime | Engine.MaxSandingTime configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxSteamHeatingPressure | Engine.MaxSteamHeatingPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxTemperature | Engine.MaxTemperature configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxTenderCoalMass | Engine.MaxTenderCoalMass configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxTenderWaterMass | Engine.MaxTenderWaterMass configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxVelocity | Engine.MaxVelocity configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.MaxWaterMass | Engine.MaxWaterMass configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Name | Engine.Name configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.NumCylinders | Engine.NumCylinders configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.NumWheels | Engine.NumWheels configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.NumberOfDamperSteps | Engine.NumberOfDamperSteps configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceAlarmTimeBeforeOverSpeed | Engine.OverspeedMonitor.MonitoringDeviceAlarmTimeBeforeOverSpeed configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceAlarmTimeLimit | Engine.OverspeedMonitor.MonitoringDeviceAlarmTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceAppliesCutsPower | Engine.OverspeedMonitor.MonitoringDeviceAppliesCutsPower configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceAppliesEmergencyBrake | Engine.OverspeedMonitor.MonitoringDeviceAppliesEmergencyBrake configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceAppliesFullBrake | Engine.OverspeedMonitor.MonitoringDeviceAppliesFullBrake configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceAppliesShutsDownEngine | Engine.OverspeedMonitor.MonitoringDeviceAppliesShutsDownEngine configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceCriticalLevel | Engine.OverspeedMonitor.MonitoringDeviceCriticalLevel configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceDoesSuppressionReset | Engine.OverspeedMonitor.MonitoringDeviceDoesSuppressionReset configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceMonitorTimeLimit | Engine.OverspeedMonitor.MonitoringDeviceMonitorTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDevicePenaltyTimeLimit | Engine.OverspeedMonitor.MonitoringDevicePenaltyTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceResetLevel | Engine.OverspeedMonitor.MonitoringDeviceResetLevel configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceResetOnResetButton | Engine.OverspeedMonitor.MonitoringDeviceResetOnResetButton configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceResetOnZeroSpeed | Engine.OverspeedMonitor.MonitoringDeviceResetOnZeroSpeed configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceTriggerOnOverspeed | Engine.OverspeedMonitor.MonitoringDeviceTriggerOnOverspeed configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceTriggerOnTrackOverspeed | Engine.OverspeedMonitor.MonitoringDeviceTriggerOnTrackOverspeed configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.OverspeedMonitor.MonitoringDeviceTriggerOnTrackOverspeedMargin | Engine.OverspeedMonitor.MonitoringDeviceTriggerOnTrackOverspeedMargin configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.PrimingFactor | Engine.PrimingFactor configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.RegulatorMainValveInitialOpenning | Engine.RegulatorMainValveInitialOpenning configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.RegulatorPilotValveExponent | Engine.RegulatorPilotValveExponent configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.RegulatorPilotValveFullOpenning | Engine.RegulatorPilotValveFullOpenning configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.RegulatorSecondValveExponent | Engine.RegulatorSecondValveExponent configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.RegulatorSecondValveStartPosition | Engine.RegulatorSecondValveStartPosition configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.RegulatorValveType | Engine.RegulatorValveType configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.RunUpTimeToMaxForce | Engine.RunUpTimeToMaxForce configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SafetyValvePressureDifference | Engine.SafetyValvePressureDifference configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SafetyValvesSteamUsage | Engine.SafetyValvesSteamUsage configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Sanding | Engine.Sanding configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.ShovelCoalMass | Engine.ShovelCoalMass configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Skip | Engine.Skip configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SmokeCombustion | Engine.SmokeCombustion configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Sound | Engine.Sound configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamBlowerEffectExponent | Engine.SteamBlowerEffectExponent configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamBlowerEfficiencyExponent | Engine.SteamBlowerEfficiencyExponent configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamBlowerMaxProportionOfBlastEffect | Engine.SteamBlowerMaxProportionOfBlastEffect configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamBlowerMaxSteamUsageRate | Engine.SteamBlowerMaxSteamUsageRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamCylinderCocksOperation | Engine.SteamCylinderCocksOperation configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamFiremanMaxPossibleFiringRate | Engine.SteamFiremanMaxPossibleFiringRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamGaugeGlassHeight | Engine.SteamGaugeGlassHeight configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamMaxSmokeUnitsReleaseRate | Engine.SteamMaxSmokeUnitsReleaseRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamSmallestCutoff | Engine.SteamSmallestCutoff configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamSmokeUnitsPerPoundOfFuel | Engine.SteamSmokeUnitsPerPoundOfFuel configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamWaterScoopMaxPickupRate | Engine.SteamWaterScoopMaxPickupRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamWaterScoopMaxPickupSpeed | Engine.SteamWaterScoopMaxPickupSpeed configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamWaterScoopMinPickupSpeed | Engine.SteamWaterScoopMinPickupSpeed configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SteamWaterScoopResistance | Engine.SteamWaterScoopResistance configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.SuperHeater | Engine.SuperHeater configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.TrainBrakesControllerEmergencyApplicationRate | Engine.TrainBrakesControllerEmergencyApplicationRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.TrainBrakesControllerEmergencyBrakeTimePenalty | Engine.TrainBrakesControllerEmergencyBrakeTimePenalty configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.TrainBrakesControllerFullServicePressureDrop | Engine.TrainBrakesControllerFullServicePressureDrop configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.TrainBrakesControllerMaxApplicationRate | Engine.TrainBrakesControllerMaxApplicationRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.TrainBrakesControllerMaxPressureDropInNormalApplication | Engine.TrainBrakesControllerMaxPressureDropInNormalApplication configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.TrainBrakesControllerMaxReleaseRate | Engine.TrainBrakesControllerMaxReleaseRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.TrainBrakesControllerMaxSystemPressure | Engine.TrainBrakesControllerMaxSystemPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.TrainBrakesControllerMinPressureReduction | Engine.TrainBrakesControllerMinPressureReduction configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.TrainBrakesControllerMinSystemPressure | Engine.TrainBrakesControllerMinSystemPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Type | Engine.Type configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VacuumBrakesHasVacuumPump | Engine.VacuumBrakesHasVacuumPump configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VacuumBrakesLargeEjectorUsageRate | Engine.VacuumBrakesLargeEjectorUsageRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VacuumBrakesMinBoilerPressureMaxVacuum | Engine.VacuumBrakesMinBoilerPressureMaxVacuum configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VacuumBrakesSmallEjectorPowerRating | Engine.VacuumBrakesSmallEjectorPowerRating configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VacuumBrakesSmallEjectorUsageRate | Engine.VacuumBrakesSmallEjectorUsageRate configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VigilanceMonitor.MonitoringDeviceAlarmTimeLimit | Engine.VigilanceMonitor.MonitoringDeviceAlarmTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VigilanceMonitor.MonitoringDeviceAppliesCutsPower | Engine.VigilanceMonitor.MonitoringDeviceAppliesCutsPower configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VigilanceMonitor.MonitoringDeviceAppliesEmergencyBrake | Engine.VigilanceMonitor.MonitoringDeviceAppliesEmergencyBrake configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VigilanceMonitor.MonitoringDeviceAppliesFullBrake | Engine.VigilanceMonitor.MonitoringDeviceAppliesFullBrake configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VigilanceMonitor.MonitoringDeviceAppliesShutsDownEngine | Engine.VigilanceMonitor.MonitoringDeviceAppliesShutsDownEngine configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VigilanceMonitor.MonitoringDeviceCriticalLevel | Engine.VigilanceMonitor.MonitoringDeviceCriticalLevel configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VigilanceMonitor.MonitoringDeviceMonitorTimeLimit | Engine.VigilanceMonitor.MonitoringDeviceMonitorTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VigilanceMonitor.MonitoringDevicePenaltyTimeLimit | Engine.VigilanceMonitor.MonitoringDevicePenaltyTimeLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VigilanceMonitor.MonitoringDeviceResetLevel | Engine.VigilanceMonitor.MonitoringDeviceResetLevel configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.VigilanceMonitor.MonitoringDeviceResetOnResetButton | Engine.VigilanceMonitor.MonitoringDeviceResetOnResetButton configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.Wagon | Engine.Wagon configured value | static configuration extracted; not a live changing value |
| config..eng:Engine.WheelRadius | Engine.WheelRadius configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon | Wagon configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Adheasion | Wagon.Adheasion configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.AntiSlip | Wagon.AntiSlip configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.BrakeAirPressureGainInResForOnePoundFromPipe | Wagon.BrakeAirPressureGainInResForOnePoundFromPipe configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.BrakeCylinderPressureForMaxBrakeBrakeForce | Wagon.BrakeCylinderPressureForMaxBrakeBrakeForce configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.BrakeDistributorApplicationRate | Wagon.BrakeDistributorApplicationRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.BrakeDistributorEmergencyResPressure | Wagon.BrakeDistributorEmergencyResPressure configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.BrakeDistributorFullServicePressure | Wagon.BrakeDistributorFullServicePressure configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.BrakeDistributorMaxAuxilaryResPressure | Wagon.BrakeDistributorMaxAuxilaryResPressure configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.BrakeDistributorNormalFullReleasePressure | Wagon.BrakeDistributorNormalFullReleasePressure configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.BrakeDistributorReleaseRate | Wagon.BrakeDistributorReleaseRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.BrakeDistributorTrainPipeControlRatio | Wagon.BrakeDistributorTrainPipeControlRatio configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.BrakeEquipmentType | Wagon.BrakeEquipmentType configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.BrakeSystemType | Wagon.BrakeSystemType configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Buffers.Angle | Wagon.Buffers.Angle configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Buffers.Centre | Wagon.Buffers.Centre configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Buffers.Radius | Wagon.Buffers.Radius configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Buffers.Spring.Damping | Wagon.Buffers.Spring.Damping configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Buffers.Spring.Stiffness | Wagon.Buffers.Spring.Stiffness configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Buffers.Spring.r0 | Wagon.Buffers.Spring.r0 configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Centre | Wagon.Centre configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.CentreOfGravity | Wagon.CentreOfGravity configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Coupling.CouplingHasRigidConnection | Wagon.Coupling.CouplingHasRigidConnection configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Coupling.CouplingUniqueType | Wagon.Coupling.CouplingUniqueType configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Coupling.Spring.Break | Wagon.Coupling.Spring.Break configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Coupling.Spring.Damping | Wagon.Coupling.Spring.Damping configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Coupling.Spring.Stiffness | Wagon.Coupling.Spring.Stiffness configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Coupling.Spring.r0 | Wagon.Coupling.Spring.r0 configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Coupling.Type | Wagon.Coupling.Type configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Coupling.Velocity | Wagon.Coupling.Velocity configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.DerailBufferForce | Wagon.DerailBufferForce configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.DerailRailForce | Wagon.DerailRailForce configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.DerailRailHeight | Wagon.DerailRailHeight configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.EmergencyBrakeResMaxPressure | Wagon.EmergencyBrakeResMaxPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.EmergencyResCapacity | Wagon.EmergencyResCapacity configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.EmergencyResChargingRate | Wagon.EmergencyResChargingRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.EmergencyResVolumeMultiplier | Wagon.EmergencyResVolumeMultiplier configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.Friction | Wagon.Friction configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.InertiaTensor.Box | Wagon.InertiaTensor.Box configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Inside.PassengerCabinFile | Wagon.Inside.PassengerCabinFile configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Inside.PassengerCabinHeadPos | Wagon.Inside.PassengerCabinHeadPos configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Inside.RotationLimit | Wagon.Inside.RotationLimit configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Inside.Sound | Wagon.Inside.Sound configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Inside.StartDirection | Wagon.Inside.StartDirection configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.IntakePoint | Wagon.IntakePoint configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights | Wagon.Lights configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.Conditions.Control | Wagon.Lights.Light.Conditions.Control configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.Conditions.Headlight | Wagon.Lights.Light.Conditions.Headlight configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.Conditions.Service | Wagon.Lights.Light.Conditions.Service configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.Conditions.TimeOfDay | Wagon.Lights.Light.Conditions.TimeOfDay configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.Conditions.Unit | Wagon.Lights.Light.Conditions.Unit configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.Cycle | Wagon.Lights.Light.Cycle configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.FadeIn | Wagon.Lights.Light.FadeIn configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.FadeOut | Wagon.Lights.Light.FadeOut configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.States | Wagon.Lights.Light.States configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.States.State.Angle | Wagon.Lights.Light.States.State.Angle configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.States.State.Azimuth | Wagon.Lights.Light.States.State.Azimuth configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.States.State.Duration | Wagon.Lights.Light.States.State.Duration configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.States.State.Elevation | Wagon.Lights.Light.States.State.Elevation configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.States.State.LightColour | Wagon.Lights.Light.States.State.LightColour configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.States.State.Position | Wagon.Lights.Light.States.State.Position configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.States.State.Radius | Wagon.Lights.Light.States.State.Radius configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.States.State.Transition | Wagon.Lights.Light.States.State.Transition configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Lights.Light.Type | Wagon.Lights.Light.Type configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Mass | Wagon.Mass configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.MaxApplicationRate | Wagon.MaxApplicationRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.MaxAuxilaryChargingRate | Wagon.MaxAuxilaryChargingRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.MaxBrakeForce | Wagon.MaxBrakeForce configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.MaxHandbrakeForce | Wagon.MaxHandbrakeForce configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.MaxReleaseRate | Wagon.MaxReleaseRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.NumWheels | Wagon.NumWheels configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.NumberOfHandbrakeLeverSteps | Wagon.NumberOfHandbrakeLeverSteps configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.PassengerCapacity | Wagon.PassengerCapacity configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Size | Wagon.Size configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Skip | Wagon.Skip configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Sound | Wagon.Sound configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Thumbnail | Wagon.Thumbnail configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.TripleValveRatio | Wagon.TripleValveRatio configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..eng:Wagon.Type | Wagon.Type configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.WagonShape | Wagon.WagonShape configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.WheelRadius | Wagon.WheelRadius configured value | static configuration extracted; not a live changing value |
| config..pat:Serial | Serial configured value | static configuration extracted; not a live changing value |
| config..pat:TrackPDPs.TrackPDP | TrackPDPs.TrackPDP configured value | static configuration extracted; not a live changing value |
| config..pat:TrackPath.Name | TrackPath.Name configured value | static configuration extracted; not a live changing value |
| config..pat:TrackPath.TrPathEnd | TrackPath.TrPathEnd configured value | static configuration extracted; not a live changing value |
| config..pat:TrackPath.TrPathName | TrackPath.TrPathName configured value | static configuration extracted; not a live changing value |
| config..pat:TrackPath.TrPathNodes | TrackPath.TrPathNodes configured value | static configuration extracted; not a live changing value |
| config..pat:TrackPath.TrPathNodes.TrPathNode | TrackPath.TrPathNodes.TrPathNode configured value | static configuration extracted; not a live changing value |
| config..pat:TrackPath.TrPathStart | TrackPath.TrPathStart configured value | static configuration extracted; not a live changing value |
| config..srv:Service_Definition.Efficiency | Service_Definition.Efficiency configured value | static configuration extracted; not a live changing value |
| config..srv:Service_Definition.MaxWheelAcceleration | Service_Definition.MaxWheelAcceleration configured value | static configuration extracted; not a live changing value |
| config..srv:Service_Definition.Name | Service_Definition.Name configured value | static configuration extracted; not a live changing value |
| config..srv:Service_Definition.PathID | Service_Definition.PathID configured value | static configuration extracted; not a live changing value |
| config..srv:Service_Definition.Serial | Service_Definition.Serial configured value | static configuration extracted; not a live changing value |
| config..srv:Service_Definition.TimeTable.EndInWorld | Service_Definition.TimeTable.EndInWorld configured value | static configuration extracted; not a live changing value |
| config..srv:Service_Definition.TimeTable.EndingSpeed | Service_Definition.TimeTable.EndingSpeed configured value | static configuration extracted; not a live changing value |
| config..srv:Service_Definition.TimeTable.StartInWorld | Service_Definition.TimeTable.StartInWorld configured value | static configuration extracted; not a live changing value |
| config..srv:Service_Definition.TimeTable.StartingSpeed | Service_Definition.TimeTable.StartingSpeed configured value | static configuration extracted; not a live changing value |
| config..srv:Service_Definition.Train_Config | Service_Definition.Train_Config configured value | static configuration extracted; not a live changing value |
| config..trf:Traffic_Definition | Traffic_Definition configured value | static configuration extracted; not a live changing value |
| config..trf:Traffic_Definition.Serial | Traffic_Definition.Serial configured value | static configuration extracted; not a live changing value |
| config..trf:Traffic_Definition.Service_Definition | Traffic_Definition.Service_Definition configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon | Wagon configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.#Size | Wagon.#Size configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Adheasion | Wagon.Adheasion configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.AntiSlip | Wagon.AntiSlip configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.AuxilaryLeakRate | Wagon.AuxilaryLeakRate configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.BrakeCylinderPressureForMaxBrakeBrakeForce | Wagon.BrakeCylinderPressureForMaxBrakeBrakeForce configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.BrakeDistributorApplicationRate | Wagon.BrakeDistributorApplicationRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.BrakeDistributorEmergencyResPressure | Wagon.BrakeDistributorEmergencyResPressure configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.BrakeDistributorFullServicePressure | Wagon.BrakeDistributorFullServicePressure configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.BrakeDistributorMaxAuxilaryResPressure | Wagon.BrakeDistributorMaxAuxilaryResPressure configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.BrakeDistributorNormalFullReleasePressure | Wagon.BrakeDistributorNormalFullReleasePressure configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.BrakeDistributorReleaseRate | Wagon.BrakeDistributorReleaseRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.BrakeDistributorTrainPipeControlRatio | Wagon.BrakeDistributorTrainPipeControlRatio configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.BrakeEquipmentType | Wagon.BrakeEquipmentType configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.BrakeSystemType | Wagon.BrakeSystemType configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Buffers.Angle | Wagon.Buffers.Angle configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Buffers.Centre | Wagon.Buffers.Centre configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Buffers.Radius | Wagon.Buffers.Radius configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Buffers.Spring.Damping | Wagon.Buffers.Spring.Damping configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Buffers.Spring.Stiffness | Wagon.Buffers.Spring.Stiffness configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Buffers.Spring.r0 | Wagon.Buffers.Spring.r0 configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.CentreOfGravity | Wagon.CentreOfGravity configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Coupling.CouplingHasRigidConnection | Wagon.Coupling.CouplingHasRigidConnection configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Coupling.CouplingUniqueType | Wagon.Coupling.CouplingUniqueType configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Coupling.Spring.Break | Wagon.Coupling.Spring.Break configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Coupling.Spring.Damping | Wagon.Coupling.Spring.Damping configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Coupling.Spring.Stiffness | Wagon.Coupling.Spring.Stiffness configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Coupling.Spring.r0 | Wagon.Coupling.Spring.r0 configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Coupling.Type | Wagon.Coupling.Type configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Coupling.Velocity | Wagon.Coupling.Velocity configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.DerailBufferForce | Wagon.DerailBufferForce configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.DerailRailForce | Wagon.DerailRailForce configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.DerailRailHeight | Wagon.DerailRailHeight configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Door | Wagon.Door configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.EmergencyBrakeResMaxPressure | Wagon.EmergencyBrakeResMaxPressure configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.EmergencyBrakeTriggerRate | Wagon.EmergencyBrakeTriggerRate configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.EmergencyResCapacity | Wagon.EmergencyResCapacity configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.EmergencyResChargingRate | Wagon.EmergencyResChargingRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.ExtraParameters | Wagon.ExtraParameters configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.FreightAnim | Wagon.FreightAnim configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction | Wagon.Friction configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights | Wagon.Friction.Lights configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.Conditions.Headlight | Wagon.Friction.Lights.Light.Conditions.Headlight configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.Conditions.Unit | Wagon.Friction.Lights.Light.Conditions.Unit configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.Cycle | Wagon.Friction.Lights.Light.Cycle configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.FadeIn | Wagon.Friction.Lights.Light.FadeIn configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.FadeOut | Wagon.Friction.Lights.Light.FadeOut configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.States | Wagon.Friction.Lights.Light.States configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.States.State.Azimuth | Wagon.Friction.Lights.Light.States.State.Azimuth configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.States.State.Duration | Wagon.Friction.Lights.Light.States.State.Duration configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.States.State.LightColour | Wagon.Friction.Lights.Light.States.State.LightColour configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.States.State.Position | Wagon.Friction.Lights.Light.States.State.Position configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.States.State.Radius | Wagon.Friction.Lights.Light.States.State.Radius configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.States.State.Transition | Wagon.Friction.Lights.Light.States.State.Transition configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Friction.Lights.Light.Type | Wagon.Friction.Lights.Light.Type configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Id | Wagon.Id configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.InertiaTensor.Box | Wagon.InertiaTensor.Box configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Inside.PassengerCabinFile | Wagon.Inside.PassengerCabinFile configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Inside.PassengerCabinHeadPos | Wagon.Inside.PassengerCabinHeadPos configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Inside.RotationLimit | Wagon.Inside.RotationLimit configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Inside.Sound | Wagon.Inside.Sound configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Inside.StartDirection | Wagon.Inside.StartDirection configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.IntakePoint | Wagon.IntakePoint configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights | Wagon.Lights configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.Conditions.Headlight | Wagon.Lights.Light.Conditions.Headlight configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.Conditions.Unit | Wagon.Lights.Light.Conditions.Unit configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.Cycle | Wagon.Lights.Light.Cycle configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.FadeIn | Wagon.Lights.Light.FadeIn configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.FadeOut | Wagon.Lights.Light.FadeOut configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.States | Wagon.Lights.Light.States configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.States.State.Azimuth | Wagon.Lights.Light.States.State.Azimuth configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.States.State.Duration | Wagon.Lights.Light.States.State.Duration configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.States.State.LightColour | Wagon.Lights.Light.States.State.LightColour configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.States.State.Position | Wagon.Lights.Light.States.State.Position configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.States.State.Radius | Wagon.Lights.Light.States.State.Radius configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.States.State.Transition | Wagon.Lights.Light.States.State.Transition configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Lights.Light.Type | Wagon.Lights.Light.Type configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Mass | Wagon.Mass configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.MaxApplicationRate | Wagon.MaxApplicationRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.MaxAuxilaryChargingRate | Wagon.MaxAuxilaryChargingRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.MaxBrakeForce | Wagon.MaxBrakeForce configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.MaxHandbrakeForce | Wagon.MaxHandbrakeForce configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.MaxReleaseRate | Wagon.MaxReleaseRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.MaxTilt | Wagon.MaxTilt configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Mirror | Wagon.Mirror configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.NumWheels | Wagon.NumWheels configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.NumberOfHandbrakeLeverSteps | Wagon.NumberOfHandbrakeLeverSteps configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Pantograph | Wagon.Pantograph configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.QuickApplicationMagnification | Wagon.QuickApplicationMagnification configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.QuickApplicationTriggerRate | Wagon.QuickApplicationTriggerRate configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.QuickReleaseMagnification | Wagon.QuickReleaseMagnification configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.QuickReleaseTriggerRate | Wagon.QuickReleaseTriggerRate configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Relaxation | Wagon.Relaxation configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.RetainingValveSlowReleaseRate | Wagon.RetainingValveSlowReleaseRate configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.Size | Wagon.Size configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Sound | Wagon.Sound configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Thumbnail | Wagon.Thumbnail configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.TrainPipeLeakRate | Wagon.TrainPipeLeakRate configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.TripleValveRatio | Wagon.TripleValveRatio configured value | static configuration extracted; not a live changing value; native token/destination mapped and Acela loaded values read |
| config..wag:Wagon.Type | Wagon.Type configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.WagonShape | Wagon.WagonShape configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.WheelRadius | Wagon.WheelRadius configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Wheelset | Wagon.Wheelset configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Wiper | Wagon.Wiper configured value | static configuration extracted; not a live changing value |
| cab.ACCELEROMETER | accelerometer native cab channel name | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.ACCELERATE_HILO | accelerate hilo native cab channel name | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.GEARS_DISPLAY | gears display native cab channel name | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.DYNAMIC_BRAKE_FORCE | dynamic brake force native cab channel name | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.CAB_RADIO | cab radio native cab channel name | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.DAMPERS_BACK | dampers back native cab channel name | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.TAILLIGHTS | taillights native cab channel name | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.CAB_SWITCH | cab switch native cab channel name | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.FUEL_GAUGE | fuel gauge native cab channel name | native name and static dispatcher mapping; runtime support depends on channel and engine |
| signal.next_iterator | Player next-signal track iterator | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear;paused forward head joins to databaseitem318 and same-run421sample0->7 clearance history;601-sample stationary-player paired series has unique head/definition joins and zero aspect disagreements;forward player next-signal selection transition observed after clearance;multiple normal-head fixture aspects4and0 selects4 under traced maximum rule |
| signal.next_distance | Distance to player next signal | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear;paused forward head joins to databaseitem318 and same-run421sample0->7 clearance history;601-sample stationary-player paired series has unique head/definition joins and zero aspect disagreements;forward player next-signal selection transition observed after clearance |
| signal.head_identity | Directional signal head identity | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear;paused forward head joins to databaseitem318 and same-run421sample0->7 clearance history;601-sample stationary-player paired series has unique head/definition joins and zero aspect disagreements;forward player next-signal selection transition observed after clearance;multiple normal-head fixture aspects4and0 selects4 under traced maximum rule |
| signal.function_type | Signal head function selector | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear |
| signal.aspect | Live aspect of directional head; select maximum aspect among normal heads for monitor | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear;paused forward head joins to databaseitem318 and same-run421sample0->7 clearance history;601-sample stationary-player paired series has unique head/definition joins and zero aspect disagreements;forward player next-signal selection transition observed after clearance;multiple normal-head fixture aspects4and0 selects4 under traced maximum rule |
| signal.aspect_speed | Speed associated with current signal aspect | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear;multiple normal-head fixture aspects4and0 selects4 under traced maximum rule |
| signal.aspect_flags | Flags associated with aspect definition | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear;multiple normal-head fixture aspects4and0 selects4 under traced maximum rule |
| service.posted_speed_cap | Posted speed restriction retained by the service | native setters and effective selection traced; all three paused service caps reproduced exactly; posted-limit crossing transition not captured;AI activation gate0to1 accompanies posted/effective cap initialization;player cap unchanged |
| service.additional_speed_cap | Additional retained cap set by certain speedposts and service initialization | native setters and effective selection traced; all three paused service caps reproduced exactly; posted-limit crossing transition not captured |
| service.scheduled_start | Loaded service scheduled activation time | native scheduler semantics traced and bytes verified; paused active/inactive AI corroborated; exact gate transition not captured |
| service.update_active | Gate admitting AI service to scheduled kinematic update | native scheduler semantics traced and bytes verified; paused active/inactive AI corroborated; exact gate transition not captured;AI activation gate0to1 accompanies posted/effective cap initialization;player cap unchanged;Tokyo AI9 physical removal, path-end flag and subsequent gate-off/progress-zero/station-reselection captured |
| service.integration_interval | Service scheduler integration interval | native scheduler semantics traced and bytes verified; paused active/inactive AI corroborated; exact gate transition not captured;47 consecutive positive-sign one-second AI service integration predictions match float32 stored speed exactly |
| service.last_update_time | AI kinematic scheduler last-update time; player has different observed time base | native scheduler semantics traced and bytes verified; paused active/inactive AI corroborated; exact gate transition not captured;47 consecutive positive-sign one-second AI service integration predictions match float32 stored speed exactly;Tokyo AI9 physical removal, path-end flag and subsequent gate-off/progress-zero/station-reselection captured |
| service.travel_sign_selector | Kinematic travel sign selector | native scheduler semantics traced and bytes verified; paused active/inactive AI corroborated; exact gate transition not captured |
| service.registry | Loaded AI service list, including services without instantiated trains | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven |
| service.key | Service asset key | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.display_name | Service display name | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.train_config | Configured consist reference | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.path_id | Configured path reference | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.id | Service identifier used by native lookup | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.train_id | Associated train identifier, allocated before physical train exists | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.train_pointer | Physical train backlink; may be null | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven |
| service.physicalized_raw | AI physical-instance lifecycle flag | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven;Tokyo AI9 physical removal, path-end flag and subsequent gate-off/progress-zero/station-reselection captured |
| service.flags_raw | Service state flags | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven |
| service.speed | Service signed current speed | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven;47 consecutive positive-sign one-second AI service integration predictions match float32 stored speed exactly;Tokyo AI9 physical removal, path-end flag and subsequent gate-off/progress-zero/station-reselection captured |
| service.target_speed | AI target speed used by kinematic integrator | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven;47 consecutive positive-sign one-second AI service integration predictions match float32 stored speed exactly |
| service.acceleration | AI target-capped kinematic acceleration input | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven;47 consecutive positive-sign one-second AI service integration predictions match float32 stored speed exactly |
| service.efficiency_candidate | Effective service speed and acceleration scaling multiplier | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated;service loader binds Efficiency token40411 to baseline204;station-stop loader binds record0 PlatformStartID,14 DistanceDownPath,1c uint16 SkipCount;Maryland player has two populated records matching platform/skip/efficiency declarations;first record selected;2026-10-10 Maryland moving departure:record10=28855.400390625,flags0x62->0x6a,selected Baltimore->Edgewood and previous=Baltimore;effective208 remains0.75;Tokyo player ENTER writes arrival and activates countdown;paused42.25 stable;expiry then departure/next-stop observed;AI populated records and selected-null-reselection observed without timed-stop claim |
| service.effective_speed_limit | Combined effective speed cap used by driver and player UI | native setters and effective selection traced; all three paused service caps reproduced exactly; posted-limit crossing transition not captured;AI activation gate0to1 accompanies posted/effective cap initialization;player cap unchanged |
| service.signal_speed_cap | Signal-related cap retained by driver | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.configured_speed_cap_candidate | Base speed cap before service efficiency scaling | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.stop_timer_remaining | Timed stop countdown candidate | Winter Tokyo AI positive platform countdown,decrements,pause stability,active zero and expiry observed;all falling pairs1second in this fixture;automatic player loading-duration branch reconstructed;later-input model matches opening timer after quarter step |
| service.stop_timer_active | Timed stop countdown gate | Winter Tokyo AI0->1->0 platform holds captured with braking,stationary progress and movement resumption;physical and abstract service contexts observed;automatic player loading-duration branch reconstructed;later-input model matches opening timer after quarter step |
| service.path_end_stop | Path-end stop condition candidate | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated;Tokyo AI9 physical removal, path-end flag and subsequent gate-off/progress-zero/station-reselection captured |
| service.wait_braking | Waiting sequence braking state candidate | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated;AI189zero-duration path-node boundary stop/resumption observed,elapsed0->1,duration0;neither braking nor dwell gate sampled nonzero |
| service.wait_active | Waiting sequence dwell state candidate | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated;AI189zero-duration path-node boundary stop/resumption observed,elapsed0->1,duration0;neither braking nor dwell gate sampled nonzero |
| service.wait_elapsed | Waiting sequence elapsed time | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated;AI189zero-duration path-node boundary stop/resumption observed,elapsed0->1,duration0;neither braking nor dwell gate sampled nonzero |
| service.wait_duration | Waiting sequence duration threshold | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated;AI189zero-duration path-node boundary stop/resumption observed,elapsed0->1,duration0;neither braking nor dwell gate sampled nonzero |
| track.geometry_length | Current section geometry length | native geometry parser/traversal traced and bytes verified; four definitions matched installed assets; grade remains a scoped derived candidate |
| track.geometry_radius | Current section curve radius; zero denotes straight in native traversal | native geometry parser/traversal traced and bytes verified; four definitions matched installed assets; grade remains a scoped derived candidate |
| track.geometry_curve_angle | Signed total section curve angle | native geometry parser/traversal traced and bytes verified; four definitions matched installed assets; grade remains a scoped derived candidate |
| track.geometry_width | Configured section width from SectionSize | native geometry parser/traversal traced and bytes verified; four definitions matched installed assets; grade remains a scoped derived candidate |
| track.geometry_skew | Configured section skew angle | native geometry parser/traversal traced and bytes verified; four definitions matched installed assets; grade remains a scoped derived candidate |
| track.geometry_flags_raw | Geometry definition flags | native geometry parser/traversal traced and bytes verified; four definitions matched installed assets; grade remains a scoped derived candidate |
| track.section_angles | Orientation at section origin | native geometry parser/traversal traced and bytes verified; four definitions matched installed assets; grade remains a scoped derived candidate |
| track.curvature_magnitude | Nominal geometry curvature magnitude | native geometry parser/traversal traced and bytes verified; four definitions matched installed assets; grade remains a scoped derived candidate |
| track.straight_grade_candidate | Grade along increasing node distance on a straight section | native geometry parser/traversal traced and bytes verified; four definitions matched installed assets; grade remains a scoped derived candidate |
| track.origin_tile | Current simulation origin tile pair | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.node | Track node identity | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending;eight matched player car/body pairs cross a node boundary with local direction1to0 during positive motion;39loose vehicle track records have valid node/section joins and bounded distances |
| track.section_index | Section ordinal within track node | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending;eight matched player car/body pairs cross a node boundary with local direction1to0 during positive motion;39loose vehicle track records have valid node/section joins and bounded distances |
| track.section | Track section instance identity | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending;eight matched player car/body pairs cross a node boundary with local direction1to0 during positive motion;39loose vehicle track records have valid node/section joins and bounded distances |
| track.direction | Track traversal direction | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending;eight matched player car/body pairs cross a node boundary with local direction1to0 during positive motion;39loose vehicle track records have valid node/section joins and bounded distances |
| track.node_distance | Distance along current node | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending;eight matched player car/body pairs cross a node boundary with local direction1to0 during positive motion;39loose vehicle track records have valid node/section joins and bounded distances |
| track.section_distance | Distance along current section | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending;eight matched player car/body pairs cross a node boundary with local direction1to0 during positive motion;39loose vehicle track records have valid node/section joins and bounded distances |
| track.local_position | Track reference point in current local coordinates | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending;39loose vehicle track records have valid node/section joins and bounded distances |
| track.angles_candidate | Track orientation angles | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.section_origin_tile | Section origin tile indices | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.section_origin_offset | Section origin offset inside tile | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.section_definition_index | Track geometry definition reference | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending;39loose vehicle track records have valid node/section joins and bounded distances |
| track.node_length | Total track-node length | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending;39loose vehicle track records have valid node/section joins and bounded distances |
| track.node_section_count | Number of sections in node | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending;39loose vehicle track records have valid node/section joins and bounded distances |
| track.route_position_candidate | Origin-independent route coordinate reconstruction | Native conversion traced;two runs of the same originX+1boundary retain45matched player/AIcar-body identities and stable origin rereads;other boundaries/geographic conversion remain unvalidated |
| topology.reachable_graph | Track graph reachable from loaded service positions | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.node_kind | Native track node kind | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.links | Connected node pointers and traversal direction bytes | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.input_pin_count | Endpoint input-side pin count | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.output_pin_count | Endpoint output-side pin count | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.selected_branch | Junction branch selector consumed by native track traversal | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.selected_connection | Junction connection selected when entering from input side | Native direction-dependent pin selection traced;earlier726-node traversal superseded by full732-node registry and route-ID validation;selected branch remains distinct from authority/occupancy |
| topology.route_node_id_candidate | TDB node ID derived by geometry and connectivity matching | all 732 registry-derived route IDs validated in current route; earlier geometry ambiguity resolved |
| infrastructure.route_databases | Loaded track database registry | native traversal/release traced; complete 732-node route match; paused presence and associations readable |
| infrastructure.all_nodes | All registered track nodes including disconnected components | native traversal/release traced; complete 732-node route match; paused presence and associations readable |
| infrastructure.track_items | Database-wide track-item registry | native traversal/release traced; complete 732-node route match; paused presence and associations readable |
| infrastructure.item_kind | Native track-item subtype discriminator | all 2970 live item indexes matched TDB subtype names; native serializer supports observed mapping |
| infrastructure.signal_service_association | Service associated with a signal object | native traversal/release traced; complete 732-node route match; paused presence and associations readable;005c4e55 acquisition traced,including null-owner/flag8000 success without store;moving AI within-node presence observed,typed infrastructure transitions not yet captured;restart capture observes junction/vector/signal association acquisition and independent aspect transitions;421sample run observes22AIpresence crossings,release and player acquisition with selected-branch changes;paused forward head joins to databaseitem318 and same-run421sample0->7 clearance history;601-sample stationary-player paired series has unique head/definition joins and zero aspect disagreements |
| infrastructure.vector_presence | Abstract per-car position records linked to a vector track segment | native traversal/release traced; complete 732-node route match; paused presence and associations readable;moving AI within-node presence observed,typed infrastructure transitions not yet captured;typed record writer,stored-service and physical-car producer paths traced;paused extrapolation agrees within0.000342m;later paused45-car pointer/backlink join confirms individual-car correspondence;261sample series observes physical AI removal while22abstract presence records continue moving;421sample run observes22AIpresence crossings,release and player acquisition with selected-branch changes |
| infrastructure.presence_service | Service identity attached to track-presence record | native traversal/release traced; complete 732-node route match; paused presence and associations readable;moving AI within-node presence observed,typed infrastructure transitions not yet captured;later paused45-car pointer/backlink join confirms individual-car correspondence;261sample series observes physical AI removal while22abstract presence records continue moving;421sample run observes22AIpresence crossings,release and player acquisition with selected-branch changes |
| infrastructure.presence_node_distance | Position of abstract car record along its track node | native traversal/release traced; complete 732-node route match; paused presence and associations readable;moving AI within-node presence observed,typed infrastructure transitions not yet captured;typed record writer,stored-service and physical-car producer paths traced;paused extrapolation agrees within0.000342m;later paused45-car pointer/backlink join confirms individual-car correspondence;261sample series observes physical AI removal while22abstract presence records continue moving;421sample run observes22AIpresence crossings,release and player acquisition with selected-branch changes |
| train.definition_mass_sum | Stored sum of connected vehicle definition masses | paused23-car player sum and two installed definitions matched exactly; changing load/AI untested |
| train.definition_length_sum | Stored sum of connected vehicle definition lengths | paused23-car player sum and two installed definitions matched exactly; coupling changes untested |
| sound.region_count | Allocated per-train sound-region table count | native allocation traced; paused count10 |
| sound.region_handles | Per-region pair of opaque sound handles | native allocation/release traced; only default player handles nonzero in paused capture |
| sound.region_last_interaction_tick | Most recent sound-region interaction timer tick | native writer/expiry traced; all paused timestamps0, changing timestamp untested |
| pickup.eligibility_flags | Pickup proximity and speed eligibility flags | native traced; paused route pickup flags0 |
| pickup.candidate_vehicle | Last vehicle selected by pickup eligibility scan | native writer traced; paused value null; nonnull transition untested |
| hazard.state_candidate | Hazard current-state candidate | native consumer traced; live world object unavailable |
| hazard.requested_state | Hazard requested state | native writer traced; live world object unavailable |
| hazard.trigger_latch | Hazard trigger latch candidate | native read/write traced; reset and live transition unverified |
| crossing.request_state | Aggregated crossing request; animation meaning unverified | native traced; no linked crossing objects in paused capture |
| crossing.flags_raw | Crossing flags including player warning logic | native traced; no linked crossing objects in paused capture |
| sound.region_item_index | Region index used by sound interaction handler | 1030 paused item reads; playback not validated |
| sound.reference_distance_candidate | Sound-region reference distance candidate | native consumer traced; paused player readable |
| sound.nearest_distance_candidate | Nearest sound-region boundary distance candidate | native minimum-selection writer traced; paused player readable |
| sound.selected_region | Selected sound-region index | native selection writer traced; paused player readable |
| track_item.node_distance | Track-item distance along its associated track segment | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.flags | Common track-item data flags | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.platform_name | Platform display name | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.station_name | Station name for platform | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.platform_flags | Platform subtype flags | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.platform_paired_item | Other platform endpoint item ID | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.platform_minimum_wait | Stored minimum platform waiting time | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.platform_waiting_passengers | Stored waiting passenger count | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances;automatic player loading-duration branch reconstructed;later-input model matches opening timer after quarter step;manual duration numerator and physical-vehicle membership/position counting traced in current-byte-verified00586f58 |
| track_item.siding_name | Siding display name | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.siding_flags | Siding subtype flags | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.siding_paired_item | Other siding endpoint item ID | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.speedpost_flags | Speed-post subtype/control flags | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.speedpost_byte_value | Conditional speed-post byte payload | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances; native restriction conversion traced, crossing transition untested |
| track_item.speedpost_float_value | Conditional speed-post floating payload | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| track_item.speedpost_angle | Stored speed-post orientation angle | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
| environment.pointer | Active render environment identity | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.precipitation.flags | Precipitation type and screen-mode flags | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.precipitation.frame_count | Precipitation texture animation frame count | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.precipitation.density | Configured particle allocation count; not precipitation rate | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.precipitation.radius | Camera-relative precipitation volume radius | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.precipitation.height | Relative precipitation volume half-height | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.precipitation.speed_parameter | Native fall-speed parameter; not complete particle velocity | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.precipitation.reset | Particle reset flag | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.particles.capacity | Particle system capacity | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.particles.count | Native particle count | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.particles.allocated | Allocated particle record count | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.particles.near_bias | Precipitation near-depth bias | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.particle.flags | Particle activity, edge, culling and screen state | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.particle.frame | Current precipitation texture frame | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.particle.position | Particle position; world-local or screen based on flag | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.particle.size | Native particle size | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.particle.colour | Particle packed colour | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.particle.screen_timer | Screen-animation timer | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.wind.layer_count | Number of wind layers | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.wind.layer_height | Layer height ceiling | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.wind.layer_direction | Layer base wind direction | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.wind.layer_jitter | Layer current direction jitter | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.wind.layer_speed | Layer base speed | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.wind.layer_speed_jitter | Layer speed jitter | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.wind.vortex_probability | Layer vortex creation probability parameter | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.wind.active_vortices | Active vortex count | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.wind.vortex_state | Vortex centre, radius, axis, angular parameter and lifetime | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.lighting.ambient_rgb | Current render ambient colour | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.lighting.ambient_packed | Current packed render ambient colour | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.lighting.directional_rgb | Current directional light colour | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.lighting.direction | Current incoming light direction | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.fog.start | Current fog start distance | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.fog.end | Current fog end distance | inherited native research plus current paused read; scene transitions not tested in this phase |
| environment.fog.scale | Fog interpolation scale | inherited native research plus current paused read; scene transitions not tested in this phase |
| activity.event_registry | Loaded activity event list | Tokyo baseline50events:14time,34location,2action;representative time/location and event0 AllStops success transitions observed |
| activity.event.id | Activity-defined event ID | Tokyo IDs connect loaded definitions to the ACT fixture; native lookup and outcome2 target changes corroborated |
| activity.event.category | Native event category | Tokyo loaded category0/time,1/action,2/location matches fixture categories |
| activity.event.type | Native event type | Dispatcher0059b083 selects time0/location1;type2 AllStops predicate0059b27b and event0 final-loading success validated;raw type3 present |
| activity.event.state_10 | Event trigger latch | Time/location latches0->1 and non-reversible location persistence;AllStops event0 latches after final loading expiry and alongside success result;UI restart reconstructs event0/32/42/44 with latch0 |
| activity.event.state_20 | Activation-level reset baseline | Native reset source traced; targets42/44 retain baseline1 while activation1->0 |
| activity.event.activation_level | Mutable current activation level | Source32 decrements targets42/44 from1 to0 while their latches and baseline are unchanged;UI restart restores42/44 activation1 with latch0 and baseline1 |
| activity.event.location_tile | Location trigger tile pair | Signed tile pair read from installed location definitions and joined with current origin |
| activity.event.location_offset | Location trigger X/Z inside tile | Float X/Z offsets match fixture and feed horizontal reconstruction |
| activity.event.location_radius | Location trigger radius | 10m event13 crossing and60m stop-event32 fixture corroborate radius use |
| activity.event.trigger_on_stop | Location event requires stopping | Event13 fires while moving with flag0;event32 remains unlatched inside radius while moving and fires after slowing with flag1 |
| activity.event.outcome_count | Number of event outcomes | Tokyo baseline contains0..3inline outcomes; native handler loops stored count |
| activity.event.outcomes | Outcome records: type, argument and payload reference | Stored types2/5/6 observed;type2 activation decrement,type5 message and type6 ActivitySuccess executed in representative Tokyo tests |
| activity.event.reversible_candidate | Reversible event latch behavior | Native nonzero branch permits reevaluation/clearing;Tokyo event13 has0 and retains latch after exit |
| activity.event_evaluation_stop | Activity flag that suppresses further event evaluation | Native guard/outcome writers traced;0->1 with event0 ActivitySuccess,retained while Activity complete alert is open;dismissal/teardown clears0 while debrief retains independent evaluation records;UI restart0 |
| activity.event_outcome_success | Success value set by event outcome handler | Outcome6 native write1 corroborated by0->1 alongside stop1 and Activity complete UI;earlier interrupted station loading remains0x1a;dismissal/teardown clears0 while debrief retains independent evaluation records;UI restart0 |
| activity.time_event_clock | Elapsed clock accumulator used by time-event conditions | Producer/reset traced;time45 and48 latches cross declared elapsed thresholds468 and618;normal UI restart captures1212.6500244140625->0 alongside day-clock64800; native elapsed continues3599.949951171875->3600.074951171875 across normal-speed Explore midnight |
| activity.event.horizontal_distance | Horizontal distance from first player car to location trigger | Finite reconstruction supports event13 radius crossing and stop-event32 distance41.41465m |
| activity.event.location_condition | Reconstructed location-event spatial and optional stop predicate | Event13 moving radius crossing and event32 stop-required predicate/latch transitions corroborated |
| session.internal_calendar | Internal clock day/month/year | Clock fields traced;3/6/2000 retained across observed Tokyo teardown and restart; remained3/6/2000 across captured Explore midnight while HMS wrapped; helper return-address replacement bypasses calendar carry;69helper instructions/207bytes match disk/live |
| session.clock_components | Internal clock second/minute/hour | 18:20:12->18:00:00->18:00:01 observed across normal UI restart; normal-speed Explore23:59:59->00:00:00 observed with same player/start and advancing native elapsed |
| car.brake_cylinder_pressure | Per-car brake cylinder pressure | Native sources traced;Acela release and diesel emergency/reset observations retained. Diesel stop series covers23player and22AI cars;player pressures change while sampled AI pipe90/cylinder0 remain unchanged. |
| car.brake_pipe_pressure | Per-car brake-pipe pressure | Native sources traced;Acela release and diesel emergency/reset observations retained. Diesel stop series covers23player and22AI cars;player pressures change while sampled AI pipe90/cylinder0 remain unchanged. |
| car.brake_force_candidate | Per-car requested brake-force quantity before adhesion limiting | Native request/adhesion consumers traced;player brake release observations retained. Moving AI400005 series includes zero requested-force values alongside changing service speed;zero is not absence of AI braking. |
| car.max_brake_force | Loaded MaxBrakeForce configuration | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| car.brake_reference_pressure_candidate | Brake pressure used to scale configured force | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| car.connection_force_candidate | Stored magnitude for current-to-following vehicle connection force | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| car.connection_break_threshold_candidate | Coupling-force threshold used to uncouple | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| body.force_accumulator_candidate | Body force accumulator | static source tracing plus stopped-player values during running simulation; independent AI force evolution unvalidated;guarded paused capture covers23player and22AI bodies with stable local rereads;one unpaused37vehicle snapshot:11player nonzero force,8moving AI and18ownerless zero force;all guarded rereads agree;181sample unpaused series:15clock-crossing samples excluded;22player body identities vary in force,16AI vary in velocity but retain zero force,36ownerless remain zero;body swaps split car identities;current0062ad6a entry and clear predicates traced:8AI fail entry,18ownerless satisfy clear,11player pass without clear;917instructions match current disk/live |
| body.torque_accumulator_candidate | Body torque accumulator | Paused and unpaused population reads plus181sample moving series retained. Guard-qualified torque vectors remainzero;15clock-crossing samples excluded. Current native entry/clear predicates traced without execution attribution. |
| body.inverse_inertia_world | World inverse inertia tensor | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| session.weather_raw | Loaded activity weather selection | loaded values match ACT; elapsed is derived and midnight semantics untested |
| session.season_raw | Loaded activity season selection | loaded values match ACT; elapsed is derived and midnight semantics untested |
| session.start_hms | Loaded activity starting clock | loaded values match ACT; elapsed is derived and midnight semantics untested |
| session.duration_hm | Configured activity duration | loaded values match ACT; elapsed is derived and midnight semantics untested |
| session.start_seconds | Activity start clock in seconds | loaded values match ACT; elapsed is derived and midnight semantics untested |
| session.elapsed_candidate | Elapsed simulation time since activity start | Observed -82799.921875 after Explore midnight versus native elapsed3600.074951171875 |
| evaluation.speed_episode_count | Completed speed-violation episode count | Earlier active-to-closed22.4140625s episode validated;Tokyo debrief retains3closed records totaling47.125s matching UI3/47s;restart empties lists/count/duration and active details |
| evaluation.speed_episode_duration | Total duration of closed speed-violation episodes | Earlier active-to-closed22.4140625s episode validated;Tokyo debrief retains3closed records totaling47.125s matching UI3/47s;restart empties lists/count/duration and active details |
| evaluation.speed_episode_active | Current speed-violation episode state and retained details | Earlier active-to-closed22.4140625s episode validated;Tokyo debrief retains3closed records totaling47.125s matching UI3/47s;restart empties lists/count/duration and active details |
| evaluation.speed_episode_records | Completed speed-violation episode records | Earlier active-to-closed22.4140625s episode validated;Tokyo debrief retains3closed records totaling47.125s matching UI3/47s;restart empties lists/count/duration and active details |
| evaluation.operational_error_count | Retained operational-error record count | Installed code labels traced;prior vigilance code2 corroborated;Tokyo debrief code64/time65526.7734375/location5.3583502769470215 matches interrupted loading and UI;restart count0/list empty |
| evaluation.operational_error_records | Operational-error records with time, marker location and raw code | Installed code labels traced;prior vigilance code2 corroborated;Tokyo debrief code64/time65526.7734375/location5.3583502769470215 matches interrupted loading and UI;restart count0/list empty |
| evaluation.freight_durability_count | Freight durability exceedance record count | native collector and installed display labels traced; empty paused lists read, no exceedance emission observed |
| evaluation.freight_durability_records | Freight durability exceedance time and marker-location records | native collector and installed display labels traced; empty paused lists read, no exceedance emission observed |
| evaluation.passenger_comfort_count | Passenger comfort exceedance record count | native collector and installed display labels traced; empty paused lists read, no exceedance emission observed |
| evaluation.passenger_comfort_records | Passenger comfort exceedance time and marker-location records | native collector and installed display labels traced; empty paused lists read, no exceedance emission observed |
| car.stored_velocity | Native stored car signed speed | native sources traced; moving/braking player and changing-speed physical AI sampled; intact consists; no reader errors |
| car.stored_acceleration | Native stored car signed acceleration | native sources traced; moving/braking player and changing-speed physical AI sampled; intact consists; no reader errors |
| car.loaded_durability | Durability copied from service/consist definition | native sources traced; moving/braking player and changing-speed physical AI sampled; intact consists; no reader errors |
| evaluation.durability_acceleration_ceiling | Loaded shared evaluation acceleration ceiling | constructor/parser/consumer traced; source values exactly match loaded float32 |
| evaluation.durability_acceleration_scale | Loaded shared evaluation acceleration normalization scale | constructor/parser/consumer traced; source values exactly match loaded float32 |
| camera.mode | Player view mode raw enum | native consumers traced; cab/front/rear/trackside/cab switches observed with matching post-input snapshots |
| camera.tracking | Player camera tracking state used by native debug display | native consumers traced; cab/front/rear/trackside/cab switches observed with matching post-input snapshots |
| camera.render_position | Current render-camera position | native consumers traced; cab/front/rear/trackside/cab switches observed with matching post-input snapshots |
| camera.render_basis | Current render-camera basis vectors | native consumers traced; cab/front/rear/trackside/cab switches observed with matching post-input snapshots |
| steam.fire_temperature | Native fire temperature | native debug labels and cab consumer traced; positive Scotsman snapshot |
| steam.fire_mass | Current fire mass | native debug labels and cab consumer traced; positive Scotsman snapshot |
| steam.ideal_fire_mass | Loaded ideal fire mass | native debug labels and cab consumer traced; positive Scotsman snapshot |
| steam.maximum_fire_mass | Loaded maximum fire mass | native debug labels and cab consumer traced; positive Scotsman snapshot |
| steam.water_mass | Native steam debug water mass | native debug label and source traced; positive paused read only |
| steam.generation_rate | Native steam debug generation rate | native debug label and source traced; positive paused read only |
| steam.usage_rate | Native steam debug usage rate | native debug label and source traced; positive paused read only |
| steam.cylinder_rate | Native steam debug cylinder rate | native debug label and source traced; positive paused read only |
| steam.exhaust_usage_rate | Native steam debug exhaust usage rate | native debug label and source traced; positive paused read only |
| steam.wheel_omega | Native steam debug wheel omega | native debug label and source traced; positive paused read only |
| steam.smoke_colour | Native steam debug smoke colour | native debug label and source traced; positive paused read only |
| steam.smoke_release_rate | Native steam debug smoke release rate | native debug label and source traced; positive paused read only |
| steam.priming | Native steam debug priming | native debug label and source traced; positive paused read only |
| steam.blowback | Native steam debug blowback | native debug label and source traced; positive paused read only |
| steam.critical_blowback | Native steam debug critical blowback | native debug label and source traced; positive paused read only |
| steam.tender_water_capacity | Native steam debug tender water capacity | native debug label and source traced; positive paused read only |
| steam.tender_coal_mass | Native steam debug tender coal mass | native debug label and source traced; positive paused read only |
| steam.tender_coal_capacity | Native steam debug tender coal capacity | native debug label and source traced; positive paused read only |
| steam.coal_burn_rate_raw | Native steam debug coal burn rate raw | native debug label and source traced; positive paused read only |
| steam.energy_output | Native steam debug energy output | native debug label and source traced; positive paused read only |
| steam.wheel_slip | Native steam debug wheel slip | native debug label and source traced; positive paused read only |
| steam.usage_exceeds_exhaust_limit | Native steam debug usage exceeds exhaust limit | native debug label and source traced; positive paused read only |
| steam.maximum_steam_rate | Native steam debug maximum steam rate | native debug label and source traced; positive paused read only |
| train.engine_update_accumulator | Pending engine-update time accumulator | native producer/scheduler traced; positive paused read only |
| train.engine_update_interval | Configured engine-update interval | native producer/scheduler traced; positive paused read only |
| steam.injector1_working | Injector 1 working branch state | native producer/scheduler traced; positive paused read only |
| steam.injector2_working | Injector 2 working branch state | native producer/scheduler traced; positive paused read only |
| electric.route_voltage | Loaded route supply voltage source | native display consumers traced; Acela pantograph-down transition and separate restored snapshot |
| electric.voltage_gate_enabled | Native electric voltage-display gate enabled setting | native display consumers traced; Acela pantograph-down transition and separate restored snapshot |
| electric.voltage_consist_condition | Consist condition used by patched native voltage display helper | native display consumers traced; Acela pantograph-down transition and separate restored snapshot |
| electric.traction_calculation_gate | Sampled bit used inside electric traction calculation; not a reliable cache freshness indicator | native producers traced; stationary controls/stale-cache observations plus released-brake low-speed movement |
| electric.cached_force_limit | Cached electric speed-dependent force calculation limit | native producers traced; stationary controls/stale-cache observations plus released-brake low-speed movement |
| electric.cached_throttle | Throttle copied during enabled electric force calculation | native producers traced; stationary controls/stale-cache observations plus released-brake low-speed movement |
| event.receiver_mask_1_32 | Retained receiver event bits for ordinary event IDs1..32 | native receiver stores traced; stable paused Acela read |
| event.receiver_mask_33_64 | Retained receiver event bits for ordinary event IDs33..64 | native receiver stores traced; stable paused Acela read |
| event.receiver_scalar1 | Receiver retained scalar variable1 | electric broadcast producer traced; both lead receiver values0->2.5->0 match throttle actuation |
| event.receiver_scalar2 | Receiver retained scalar variable2 | native receiver stores traced; stable paused Acela read |
| event.receiver_scalar3 | Receiver retained scalar variable3 | native receiver stores traced; stable paused Acela read |
| event.receiver_previous_scalar1 | Scalar1 retained at previous completed normal receiver processing | native processing stores traced; paused tick advances with unchanged simulation time |
| event.receiver_previous_scalar2 | Scalar2 retained at previous completed normal receiver processing | native processing stores traced; paused tick advances with unchanged simulation time |
| event.receiver_previous_scalar3 | Scalar3 retained at previous completed normal receiver processing | native processing stores traced; paused tick advances with unchanged simulation time |
| event.receiver_last_processing_tick | Windows tick saved by normal receiver processing | native processing stores traced; paused tick advances with unchanged simulation time |
| event.receiver_list | Native processing-list receiver identities and physical-car handle matches | native traversal/allocation/label sources traced;20 live receivers with48 streams |
| event.receiver_definition_label | Loaded receiver definition label | native traversal/allocation/label sources traced;20 live receivers with48 streams |
| event.receiver_stream_count | Loaded definition stream count | native traversal/allocation/label sources traced;20 live receivers with48 streams |
| event.receiver_trigger_state_slots | Loaded definition indexed trigger-state allocation count | native traversal/allocation/label sources traced;20 live receivers with48 streams |
| event.receiver_position | Receiver position used by audio distance calculation | vector producer traced;19 non-skipped live distance comparisons,13 exact; Acela threshold/file correspondence |
| event.listener_position | Listener position used by receiver distance calculation | vector producer traced;19 non-skipped live distance comparisons,13 exact; Acela threshold/file correspondence |
| event.receiver_squared_distance | Stored squared receiver-to-listener separation | vector producer traced;19 non-skipped live distance comparisons,13 exact; Acela threshold/file correspondence |
| event.receiver_activation_distance_threshold | Loaded activation squared-distance threshold | vector producer traced;19 non-skipped live distance comparisons,13 exact; Acela threshold/file correspondence |
| event.receiver_deactivation_distance_threshold | Loaded deactivation squared-distance threshold | vector producer traced;19 non-skipped live distance comparisons,13 exact; Acela threshold/file correspondence |
| event.receiver_inactive_condition | Receiver inactive-condition bit selected by camera/distance conditions | set/clear native writers traced;12 of20 flags change during cab/external/cab and all20 restore |
| event.brake_pressure_reference | Retained cylinder-pressure reference for brake sound events | native producer and caller traced; eight-car series; lead rising latch and reference transition observed; subsequent Acela release-mode transition observed, eight cars settled cylinder0/pipe110 PSI; falling latch0/1 and timer0..1.5 |
| event.brake_pressure_rise_latch | Latch suppressing repeated rising-pressure sound events | native producer and caller traced; eight-car series; lead rising latch and reference transition observed |
| event.brake_pressure_fall_latch | Latch suppressing repeated falling-pressure sound events | native producer and caller traced; eight-car series; lead rising latch and reference transition observed; subsequent Acela release-mode transition observed, eight cars settled cylinder0/pipe110 PSI; falling latch0/1 and timer0..1.5 |
| event.brake_pressure_rise_timer | Shared rising-pressure event timer | native producer and caller traced; eight-car series; lead rising latch and reference transition observed |
| event.brake_pressure_fall_timer | Shared falling-pressure event timer | native producer and caller traced; eight-car series; lead rising latch and reference transition observed; subsequent Acela release-mode transition observed, eight cars settled cylinder0/pipe110 PSI; falling latch0/1 and timer0..1.5 |
| car.auxiliary_reservoir_pressure | Current distributor auxiliary-reservoir pressure | native reservoir consumers and configuration limits traced; live paused values read |
| car.emergency_reservoir_pressure | Current distributor emergency-reservoir pressure | native reservoir consumers and configuration limits traced; live paused values read |
| brake.train_selected_mode | Selected train brake controller mode after loaded-range lookup | native caller/selector traced; paused loaded-range reconstruction matches stored1000hex mode; subsequent Acela release-mode transition observed, eight cars settled cylinder0/pipe110 PSI; falling latch0/1 and timer0..1.5 |
| brake.train_selected_fraction | Within-mode train brake controller fraction | native caller/selector traced; paused loaded-range reconstruction matches stored1000hex mode; subsequent Acela release-mode transition observed, eight cars settled cylinder0/pipe110 PSI; falling latch0/1 and timer0..1.5 |
| service.efficiency_baseline | Baseline source for effective service efficiency | native source selection traced; all three paused services baseline/effective0.75;service loader binds Efficiency token40411 to baseline204;station-stop loader binds record0 PlatformStartID,14 DistanceDownPath,1c uint16 SkipCount;Maryland player has two populated records matching platform/skip/efficiency declarations;first record selected |
| service.ordered_operational_records | Ordered station-stop records used by distance selector and efficiency override | Player/AI list extraction,player boarding/departure,AI path-end reset and final-selected AllStops success validated;teardown leaves stale selection with null list;restart rebuilds records;winter AI platform countdown begins as selection advances,with hold at previous platform and unchanged station time/flag fields;AI traffic loader schedule merge traced;automatic player-driver station flag writer distinguished from traffic update;terminal ITR baseline retained |
| station.recorded_arrival | Recorded station arrival time; may be synthesized from schedule | Accepted loading writes arrival in representative Tokyo stops,including final65979.2734375;alternate native synthesis branches retained;restarted initial record has synthetic64805 while clock64801.2265625;all five winter AI services retain0 through observed platform countdown/stop/resumption;AI traffic loader schedule merge traced;automatic player-driver station flag writer distinguished from traffic update;terminal ITR baseline retained;automatic-player opening hold captures platform66flags0to2,countdown onset/release and unchanged zero recorded times |
| station.recorded_departure | Recorded station departure-related event time | Normal and unfinished-loading departure writes observed;final-stop success retains recorded departure0 with final record still selected;all five winter AI services retain0 through observed platform countdown/stop/resumption;AI traffic loader schedule merge traced;automatic player-driver station flag writer distinguished from traffic update;terminal ITR baseline retained;automatic-player opening hold captures platform66flags0to2,countdown onset/release and unchanged zero recorded times |
| station.scheduled_arrival | Scheduled station arrival time | Native loader/merge traced;Maryland and Tokyo player schedules match declarations;Tokyo AI fields are0;winter AI IDs1/2 retain repeated60120/60600 schedules,IDs70/71/72 retain0,matching TRF groups throughout platform holds;AI traffic loader schedule merge traced;automatic player-driver station flag writer distinguished from traffic update;terminal ITR baseline retained |
| station.scheduled_departure | Scheduled station departure time | Native loader/merge traced;Maryland and Tokyo player schedules match declarations;Tokyo AI fields are0;winter AI IDs1/2 retain repeated60120/60600 schedules,IDs70/71/72 retain0,matching TRF groups throughout platform holds;AI traffic loader schedule merge traced;automatic player-driver station flag writer distinguished from traffic update;terminal ITR baseline retained |
| station.state_flags | Station record branch-local arrival, loading, departure and cue state | Arrival2,normal expiry/cue0x62,normal departure0x6a,interruption0x1a;final0x62 precedes AllStops success while still selected and without departure;winter AI IDs1/2 flags1 and70/71/72 flags0 remain unchanged through platform holds;AI traffic loader schedule merge traced;automatic player-driver station flag writer distinguished from traffic update;terminal ITR baseline retained;automatic-player opening hold captures platform66flags0to2,countdown onset/release and unchanged zero recorded times |
| station.boarding_active | Player activity boarding countdown active state | Tokyo0->1->0 for normal expiry and interruption;final expiry observed before AllStops result;paused active samples stable;manual duration numerator and physical-vehicle membership/position counting traced in current-byte-verified00586f58 |
| station.boarding_remaining | Player activity remaining boarding countdown | Positive/decreasing/paused/expired/cancelled values;final first-positive33.20833206176758 reaches0 before event0 success;first read is not necessarily initial duration;manual duration numerator and physical-vehicle membership/position counting traced in current-byte-verified00586f58 |
| car.connection_endpoints | Native coupling-solver endpoint positions reconstructed from vehicle definition and body transform | native geometry path traced;8paused connections reconstructed at approximately0.14942..0.15048m; combined moving player/AI endpoint analysis preserves discrepancies and phase-sensitive outliers |
| car.connection_endpoint_distance | Nonnegative distance between current end0 and following end1 solver connection points | native geometry path traced;8paused connections reconstructed at approximately0.14942..0.15048m; combined moving player/AI endpoint analysis preserves discrepancies and phase-sensitive outliers |
| car.connection_endpoint_velocity | Connection endpoint velocity including body rotation | native vector helpers traced;8paused pairs yield near-zero residual rates,all angular velocity zero;preserved moving player/AI observations reveal orientation changes with zero stored angular velocity and nonzero position/velocity discrepancies; combined moving player/AI endpoint analysis preserves discrepancies and phase-sensitive outliers; combined moving player/AI comparison supports distinct motion time bases |
| car.connection_separation_rate | Projected relative stored-state velocity of connected solver endpoints; not universal gap derivative | native vector helpers traced;8paused pairs yield near-zero residual rates,all angular velocity zero;preserved moving player/AI observations reveal orientation changes with zero stored angular velocity and nonzero position/velocity discrepancies; combined moving player/AI endpoint analysis preserves discrepancies and phase-sensitive outliers; combined moving player/AI comparison supports distinct motion time bases |
| physics_integrator.time | Stored physics integrator time accumulator | native setter/getter/integrator traced;11paused samples stable at distinct physics/game elapsed times; combined moving player/AI comparison supports distinct motion time bases |
| physics_integrator.configured_step | Configured physics integration step | native setter/getter/integrator traced;11paused samples stable at distinct physics/game elapsed times; combined moving player/AI comparison supports distinct motion time bases |
| physics_integrator.current_step | Current or last physics integration step | native setter/getter/integrator traced;11paused samples stable at distinct physics/game elapsed times; combined moving player/AI comparison supports distinct motion time bases |
| physics_integrator.mode_raw | Physics solver selection code | native setter/getter/integrator traced;11paused samples stable at distinct physics/game elapsed times; combined moving player/AI comparison supports distinct motion time bases |
| physics_integrator.status_raw | Last simulation-object operation status code | native setter/getter/integrator traced;11paused samples stable at distinct physics/game elapsed times; combined moving player/AI comparison supports distinct motion time bases |
| physics_integrator.body_count | Registered integration body count | native setter/getter/integrator traced;11paused samples stable at distinct physics/game elapsed times; combined moving player/AI comparison supports distinct motion time bases |
| physics_integrator.enabled_raw | Physics loop continuation gate | native setter/getter/integrator traced;11paused samples stable at distinct physics/game elapsed times; combined moving player/AI comparison supports distinct motion time bases |
| infrastructure.junction_service_association | Junction matching-service association used by release path | typed release/native layout traced and verified;246junctions408vectors read;3junctions and5vector lists join services; typed two-pass route claim and directional vector check/commit paths traced;moving AI within-node presence observed,typed infrastructure transitions not yet captured;restart capture observes junction/vector/signal association acquisition and independent aspect transitions;421sample run observes22AIpresence crossings,release and player acquisition with selected-branch changes |
| infrastructure.junction_flags4e | Junction raw flags containing cleanup-cleared bit2 | typed release/native layout traced and verified;246junctions408vectors read;3junctions and5vector lists join services; typed two-pass route claim and directional vector check/commit paths traced;moving AI within-node presence observed,typed infrastructure transitions not yet captured |
| infrastructure.vector_service_associations | Service values in vector-node routing list,distinct from per-car presence | typed release/native layout traced and verified;246junctions408vectors read;3junctions and5vector lists join services; typed two-pass route claim and directional vector check/commit paths traced;moving AI within-node presence observed,typed infrastructure transitions not yet captured;restart capture observes junction/vector/signal association acquisition and independent aspect transitions;421sample run observes22AIpresence crossings,release and player acquisition with selected-branch changes |
| infrastructure.vector_state35_raw | Vector-node byte set to3 when service list becomes empty | typed release/native layout traced and verified;246junctions408vectors read;3junctions and5vector lists join services; typed two-pass route claim and directional vector check/commit paths traced;moving AI within-node presence observed,typed infrastructure transitions not yet captured;restart capture observes junction/vector/signal association acquisition and independent aspect transitions;421sample run observes22AIpresence crossings,release and player acquisition with selected-branch changes |
| infrastructure.vector_constraint34_raw | Vector-node directional claim constraint/state input | native claim-check consumer traced;408paused nodes read with values0/1/3/4;moving AI within-node presence observed,typed infrastructure transitions not yet captured;restart capture observes junction/vector/signal association acquisition and independent aspect transitions;421sample run observes22AIpresence crossings,release and player acquisition with selected-branch changes |
| infrastructure.presence_physical_car | Presence record association to physical car | native access paths and paused bidirectional identity joins verified;261sample series observes physical AI removal while22abstract presence records continue moving |
| car.presence_backlink | Physical-car backlink to abstract presence record | native access paths and paused bidirectional identity joins verified;261sample series observes physical AI removal while22abstract presence records continue moving |
| infrastructure.presence_direction_raw | Stored direction byte in abstract presence record | native access paths and paused bidirectional identity joins verified;261sample series observes physical AI removal while22abstract presence records continue moving |
| camera.view_position | Player view-state position used by AI physicalization gate | native comparison/removal paths traced;paused distance inputs and disk/live threshold match |
| service.physicalization_distance_squared_threshold | Native squared-distance threshold for AI physicalization | native comparison/removal paths traced;paused distance inputs and disk/live threshold match |
| service.physicalization_endpoint_distances | Distances from both stored service endpoints to player view | native comparison/removal paths traced;paused distance inputs and disk/live threshold match |
| environment.selection.season_selector | Season selector consumed by ENV filename selection | native selector/path setup traced and live bytes verified;paused12-slot table and selected name match installed route |
| environment.selection.weather_selector | Weather selector consumed by ENV filename selection | native selector/path setup traced and live bytes verified;paused12-slot table and selected name match installed route |
| environment.selection.editor_override | Raw selector override choosing editor.env | native selector/path setup traced and live bytes verified;paused12-slot table and selected name match installed route |
| environment.selection.route_filename_table | Loaded route season/weather ENV filename table | native selector/path setup traced and live bytes verified;paused12-slot table and selected name match installed route |
| environment.selection.selected_filename | Current selected ENV filename buffer | native selector/path setup traced and live bytes verified;paused12-slot table and selected name match installed route |
| environment.selection.route_directory | Route directory buffer used by path setup | native selector/path setup traced and live bytes verified;paused12-slot table and selected name match installed route |
| environment.selection.env_directory | ENV directory buffer constructed by route setup | native selector/path setup traced and live bytes verified;paused12-slot table and selected name match installed route |
| environment.selection.env_texture_directory | ENV texture directory buffer constructed by route setup | native selector/path setup traced and live bytes verified;paused12-slot table and selected name match installed route |
| environment.sky.pointer | Loaded sky object identity | native parser allocation/layout verified against disk/live;paused3layers2satellites and split2 sampled |
| environment.sky.layer_count | Loaded sky layer record count | native parser allocation/layout verified against disk/live;paused3layers2satellites and split2 sampled |
| environment.sky.layer_split | Stored satellite insertion split selector | native parser allocation/layout verified against disk/live;paused3layers2satellites and split2 sampled |
| environment.sky.layer_array | Loaded sky layer record identities | native parser allocation/layout verified against disk/live;paused3layers2satellites and split2 sampled |
| environment.sky.satellite_count | Loaded sky satellite record count | native parser allocation/layout verified against disk/live;paused3layers2satellites and split2 sampled |
| environment.sky.satellite_array | Loaded satellite record identities | native parser allocation/layout verified against disk/live;paused3layers2satellites and split2 sampled |
| environment.satellite.low_scale | Loaded low satellite scale | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.high_scale | Loaded high satellite scale | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.rise_position | Loaded satellite rise azimuth | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.rise_time | Loaded satellite rise clock | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.set_time | Loaded satellite set clock | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.fade_time | Loaded satellite fade duration | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.dir_rise_colour | Loaded directional rise colour key | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.dir_high_colour | Loaded directional high colour key | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.dir_set_colour | Loaded directional set colour key | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.amb_rise_colour | Loaded ambient rise colour key | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.amb_high_colour | Loaded ambient high colour key | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.amb_set_colour | Loaded ambient set colour key | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.light_pointer | Satellite-created light object identity | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.satellite.fog | Loaded satellite fog byte | native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact |
| environment.layer.top_faces | Stored layer top face parameter | native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match |
| environment.layer.top_radius | Loaded layer top radius | native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match |
| environment.layer.top_height | Loaded layer top height | native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match |
| environment.layer.edge_count | Loaded edge-step count | native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match |
| environment.layer.edge_array | Loaded edge-step record identities | native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match |
| environment.layer.edge_height | Loaded edge-step height | native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match |
| environment.layer.edge_radius | Loaded edge-step radius | native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match |
| environment.layer.fadein_start | Loaded layer fade-in start | native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match |
| environment.layer.fadein_end | Loaded layer fade-in end | native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match |
| environment.layer.fadeout_start | Loaded layer fade-out start | native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match |
| environment.layer.fadeout_end | Loaded layer fade-out end | native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match |
| environment.render.vertex_count | Allocated sky draw-object vertex count | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| environment.render.vertex_array | Sky CPU vertex buffer identity | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| environment.render.vertex_position | Stored local sky mesh vertex position | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| environment.render.vertex_diffuse | Stored sky vertex diffuse colour | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| environment.render.vertex_secondary | Stored sky vertex secondary/specular word | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| environment.render.vertex_uv | Stored mutable sky texture coordinates | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| environment.render.frame_count | Loaded sky animated-shader frame count | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| environment.render.frame_duration | Loaded sky animated-shader frame duration | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| environment.render.animation_clock | Stored sky shader animation phase accumulator | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| environment.render.selected_frame | Raw selected sky shader frame index | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| environment.render.frame_array | Loaded sky shader frame records | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| environment.render.frame_scroll | Selected frame texture scroll coefficients | native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes |
| audio.stream.state_identity | Per-receiver stream runtime record identity | native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved |
| audio.stream.backend_identity | Native stream backend object identity | native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved |
| audio.stream.backend_flags | Native stream backend flags | native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved |
| audio.stream.queue_head | Stream linked pending-record head | native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved |
| audio.stream.queue_count | Number of linked stream pending records when traversal completes | native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved |
| audio.stream.cached_volume_curve | Cached stream volume-curve result | native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved |
| audio.stream.cached_frequency_curve | Cached stream frequency-curve result | native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved |
| audio.stream.trigger_enable_words | Stream trigger-enable mask words | native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved |
| audio.stream.volume_factor | Stored stream volume factor | native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved |
| audio.stream.interface_identities | Stored buffer and spatial-interface identities | native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved |
| audio.stream.trigger_count | Loaded per-stream trigger record count | native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved |
| audio.pending.kind | Pending audio record type discriminator | typed constructors/load helper match disk/live;262nodes and5kind1 sample objects read with stable rereads |
| audio.pending.control_bytes | Pending audio record raw control bytes | typed constructors/load helper match disk/live;262nodes and5kind1 sample objects read with stable rereads |
| audio.pending.sample_identity | Type1 requested sample-reference identity | typed constructors/load helper match disk/live;262nodes and5kind1 sample objects read with stable rereads |
| audio.pending.sample_path_parts | Loaded directory and filename labels for requested sample | typed constructors/load helper match disk/live;262nodes and5kind1 sample objects read with stable rereads |
| audio.pending.acquisition_counter | Sample load/acquisition reference counter candidate | typed constructors/load helper match disk/live;262nodes and5kind1 sample objects read with stable rereads |
| audio.pending.resource_identity | Loaded resource object for requested sample | typed constructors/load helper match disk/live;262nodes and5kind1 sample objects read with stable rereads |
| audio.pending.nested_children | Type2 pending-record child ring identities | verified native construction rule;4wrappers3children each with stable full-record rereads |
| audio.pending.nested_child_count | Child count for a completely traversed type2 pending record | verified native construction rule;4wrappers3children each with stable full-record rereads |
| input.mode | Raw native input mode/gate | layout reused from pinned clean NEMT source;native list/binding/listener helpers verified;paused238-entry keyboard read |
| input.devices | Native input device registry identities | layout reused from pinned clean NEMT source;native list/binding/listener helpers verified;paused238-entry keyboard read |
| input.device_kind | Input object device kind | layout reused from pinned clean NEMT source;native list/binding/listener helpers verified;paused238-entry keyboard read |
| input.keyboard_count | Native keyboard entry count | layout reused from pinned clean NEMT source;native list/binding/listener helpers verified;paused238-entry keyboard read |
| input.keyboard_held | Native keyboard held-state bitset | layout reused from pinned clean NEMT source;native list/binding/listener helpers verified;paused238-entry keyboard read;one paused Shift_L press yields2distinct native records in3samples;5394samples0errors,held bits always zero |
| input.bindings | Native scan binding records and modifier words | layout reused from pinned clean NEMT source;native list/binding/listener helpers verified;paused238-entry keyboard read |
| input.action_id | Bound input action opaque identifier | layout reused from pinned clean NEMT source;native list/binding/listener helpers verified;paused238-entry keyboard read |
| input.action_flags | Native bound-action state flags | layout reused from pinned clean NEMT source;native list/binding/listener helpers verified;paused238-entry keyboard read |
| input.listeners | Bound action listener target/context/mask/flags | layout reused from pinned clean NEMT source;native list/binding/listener helpers verified;paused238-entry keyboard read |
| input.action_value | Stored action event value or button-reference count | disk dispatcher semantics traced with existing live entry patch;keyboard update/getter ranges match disk/live;capacity12emptybuffer observed |
| input.action_filter | Action dispatch filter word | disk dispatcher semantics traced with existing live entry patch;keyboard update/getter ranges match disk/live;capacity12emptybuffer observed |
| input.buffer_capacity | Keyboard native event buffer capacity | disk dispatcher semantics traced with existing live entry patch;keyboard update/getter ranges match disk/live;capacity12emptybuffer observed;one paused Shift_L press yields2distinct native records in3samples;5394samples0errors,held bits always zero |
| input.buffer_cursor | Keyboard event consumption cursor | disk dispatcher semantics traced with existing live entry patch;keyboard update/getter ranges match disk/live;capacity12emptybuffer observed;one paused Shift_L press yields2distinct native records in3samples;5394samples0errors,held bits always zero |
| input.buffer_count | Keyboard current buffered record count | disk dispatcher semantics traced with existing live entry patch;keyboard update/getter ranges match disk/live;capacity12emptybuffer observed;one paused Shift_L press yields2distinct native records in3samples;5394samples0errors,held bits always zero |
| input.buffer_records | Keyboard buffered native input records | disk dispatcher semantics traced with existing live entry patch;keyboard update/getter ranges match disk/live;capacity12emptybuffer observed;one paused Shift_L press yields2distinct native records in3samples;5394samples0errors,held bits always zero |
| session.route_display_label | Loaded route display label | writer argument sources match disk/live;6live strings with stable pointer/root rereads;stored ASV title/basename corroboration |
| session.route_identifier_label | Loaded route identifier label used by header | writer argument sources match disk/live;6live strings with stable pointer/root rereads;stored ASV title/basename corroboration |
| session.activity_context_label04 | Loaded activity context label at+4 | writer argument sources match disk/live;6live strings with stable pointer/root rereads;stored ASV title/basename corroboration |
| session.activity_context_label08 | Loaded optional activity context label at+8 | writer argument sources match disk/live;6live strings with stable pointer/root rereads;stored ASV title/basename corroboration |
| session.activity_title | Loaded activity title used by save header | writer argument sources match disk/live;6live strings with stable pointer/root rereads;stored ASV title/basename corroboration |
| session.activity_path | Loaded activity source path;header emits basename | writer argument sources match disk/live;6live strings with stable pointer/root rereads;stored ASV title/basename corroboration |
| resource.path_version_word | Loaded path raw word emitted in native Version_Path list | writer callbacks match disk/live;paused player and2AI service sources readable;9distinct stored/live name-word pairs agree |
| resource.consist_version_word | Loaded consist raw word emitted in native Version_Consist list | writer callbacks match disk/live;paused player and2AI service sources readable;9distinct stored/live name-word pairs agree |
| resource.service_version_word | Loaded service raw word emitted in native Version_Service list | writer callbacks match disk/live;paused player and2AI service sources readable;9distinct stored/live name-word pairs agree |
| resource.traffic_version_word | Loaded traffic raw word emitted in native Version_Traffic block | writer callbacks match disk/live;paused player and2AI service sources readable;9distinct stored/live name-word pairs agree |
| car.physical_registry | Physical-object list independently of train-owned consist chains | native consumers and exact constant-return methods traced;45paused objects match connected train membership;positive yard fixture has39owner-null loose vehicles outside train chains in6linked components;player coupling and F9 separation validate chain1to6to1 and five loose owners0toPlayerTo0;stored physical count40 |
| car.native_kind | Native vehicle class discriminator | native consumers and exact constant-return methods traced;45paused objects match connected train membership;positive yard fixture has39owner-null loose vehicles outside train chains in6linked components |
| car.object_id | Native vehicle identifier used by object lookup and save references | native consumers and exact constant-return methods traced;45paused objects match connected train membership;positive yard fixture has39owner-null loose vehicles outside train chains in6linked components;player coupling and F9 separation validate chain1to6to1 and five loose owners0toPlayerTo0;stored physical count40 |
| car.physical_registry_stored_count | Stored manager physical-object list count | insertion/removal consumers traced;45paused vehicles have bit4 and storedcount45;positive yard fixture has39owner-null loose vehicles outside train chains in6linked components;player coupling and F9 separation validate chain1to6to1 and five loose owners0toPlayerTo0;stored physical count40 |
| car.registered_bit | Object registration flag used by insertion and teardown | insertion/removal consumers traced;45paused vehicles have bit4 and storedcount45;positive yard fixture has39owner-null loose vehicles outside train chains in6linked components |
| car.wheel_rate_stored | Stored ordinary wheel angular-rate candidate | Native producers and selected constants traced;populated player/AI snapshots and short moving sequences retained. Engine rates vary;sampled player adhesion cache668360.0625 and AI0 do not establish delivered force or slip. |
| engine.driver_rotation_rate | Stored powered driver rotation-rate candidate | Native producers and selected constants traced;populated player/AI snapshots and short moving sequences retained. Engine rates vary;sampled player adhesion cache668360.0625 and AI0 do not establish delivered force or slip. |
| engine.adhesion_force_limit | Stored powered-vehicle adhesion limit candidate | Native producers and selected constants traced;populated player/AI snapshots and short moving sequences retained. Engine rates vary;sampled player adhesion cache668360.0625 and AI0 do not establish delivered force or slip. |
| engine.driver_animation_phase | Stored powered-driver animation phase accumulator | native consumer/store verified;no live phase or visual-transition observation; populated player/AI reads and short moving sequences retained |
| car.shape_animation_time | Stored current shape animation scalar | native constructor/setter/dispatch traced and bytes verified;no loaded shape values sampled; populated player/AI reads and short moving sequences retained |
| car.shape_animation_processed_time | Stored previous processed shape animation scalar | native constructor/setter/dispatch traced and bytes verified;no loaded shape values sampled; populated player/AI reads and short moving sequences retained |
| car.shape_node_count | Stored animation node count | native slot/transform layout traced;paused four-engine snapshot with24wheel nodes and matching owners |
| car.shape_node_callbacks | Per-node animation callback bindings and ordinary-wheel context | native slot/transform layout traced;paused four-engine snapshot with24wheel nodes and matching owners |
| car.shape_node_transform | Stored per-node animation transform | native slot/transform layout traced;paused four-engine snapshot with24wheel nodes and matching owners;two moving/paused series validate representative player/AI locomotive and wagon matrix transitions |
| car.wheel_transform_groups | Type-4 per-vehicle wheel transform groups | native bounded type4branch and base-transform consumer traced;paused41vehicle snapshot reads82groups164wheelmatrices82basematrices;two moving/paused series validate representative player/AI locomotive and wagon matrix transitions |
| engine.aws_monitor_state | AWSMonitor runtime state | native parser/initializer/selected consumers traced and bytes matched;paused lead-state snapshot;retained player reload comparison preserves enable/definition indexes for four slots on two engines;lead pointers rebuilt;all eight emitted60-byte monitor payloads/indexes match pre-save source on two engines |
| engine.vigilance_monitor_state | VigilanceMonitor runtime state | native parser/initializer/selected consumers traced and bytes matched;paused lead-state snapshot;UI-enabled player vigilance penalty sequence and retained evaluation record observed;retained player reload comparison preserves enable/definition indexes for four slots on two engines;lead pointers rebuilt;all eight emitted60-byte monitor payloads/indexes match pre-save source on two engines |
| engine.emergency_stop_monitor_state | EmergencyStopMonitor runtime state | native parser/initializer/selected consumers traced and bytes matched;paused lead-state snapshot;UIZ acknowledgement clears emergency action/alarm/penalty with stable local rereads;subsequentN1current225A observed;retained player reload comparison preserves enable/definition indexes for four slots on two engines;lead pointers rebuilt;all eight emitted60-byte monitor payloads/indexes match pre-save source on two engines |
| engine.overspeed_monitor_state | OverspeedMonitor runtime state | native parser/initializer/selected consumers traced and bytes matched;paused lead-state snapshot |
| engine.unnamed_monitor_slot3_state | Unnamed fifth engine monitor runtime state | native layout,initializer disable and diesel conditional current trigger traced;paused disabled state read with valid definition;retained player reload comparison preserves enable/definition indexes for four slots on two engines;lead pointers rebuilt;all eight emitted60-byte monitor payloads/indexes match pre-save source on two engines |
| session.vigilance_update_suppressed | Vigilance update suppression gate | native alerter handler and suppression branches traced;running/paused gate sampled1;UI-enabled player vigilance penalty sequence and retained evaluation record observed |
| session.aws_update_suppressed | AWS update suppression gate | native alerter handler and suppression branches traced;running/paused gate sampled1;UI-enabled player vigilance penalty sequence and retained evaluation record observed |
| car.collision_callback_state | Collision flags and callback binding (native CollideFlags/CollideFunction) | disk/live callback table and stubs agree;selected native targets verified;45vehicle paused capture has callback402bc6,state5 and stable local rereads;native parser labels,flags consumers,initializer and load callback reconstruction traced and byte-verified |
| physics.collision_work_buffer | Transient collision processing buffer | Allocation/rebuild/teardown and current native dispatch, classifier, callback arguments and null-body guards traced. Populated ITR snapshots contain25 and3 records with equal sequential rereads;all sampled body pointers null. Shared simulation owns dispatch table773280. Later object-header/type follow-up resolves class index6 to native kind4000b. No runtime callback execution or physical contact validity demonstrated. |
| activity.event.time_threshold | Time-event elapsed-clock threshold | 14stored thresholds read;468matches time45 fixture and captured elapsed-clock transition |
| evaluation.report_success | Final report copy of activity success | Native exported ranges match disk/live;0on manual exit;positive report copy unvalidated |
| evaluation.report_presence_flags | Raw report presence flags | Native exported ranges match disk/live;1read before/after exit;full flag vocabulary unresolved |
| evaluation.report_termination_code | Final report selected termination code | Native exported ranges match disk/live;0on manual exit;nonzero reason/payload mapping unvalidated;not whole source bitmask |
| evaluation.report_duration | Finalized day-clock difference from activity start | Native exported ranges match disk/live;10.8515625matches UI11seconds in early-exit example;midnight/save semantics open |
| evaluation.late_arrival_count | Final count of arrived station records beyond arrival tolerance | Native exported ranges match disk/live;0observed;positive late count not tested by this reader |
| evaluation.missed_stop_count | Final count of station records marked missed or without arrival bit | Native exported ranges match disk/live;4matches copied flags and UI;includes future unvisited stations on early exit |
| evaluation.last_arrival_deviation | Last qualifying finalized arrival deviation after tolerance adjustment | Native exported ranges match disk/live;0observed;native overwrite is not a sum;nonzero/edge inputs unvalidated |
| evaluation.last_departure_deviation | Last qualifying finalized departure deviation after tolerance adjustment | Native exported ranges match disk/live;0observed;may retain prior eligible value when later records lack departure;not a sum |
| evaluation.final_station_records | Copied finalized station evaluation records | Native exported ranges match disk/live;empty during gameplay;5final records exactly match source times/flags;string pointers not decoded |
| evaluation.final_station_count | Finalized station-summary record count | Native exported ranges match disk/live;0->5matches final list length;not continuously updated gameplay total |
| evaluation.final_action_records | Finalized action-type6..9 summary records | Native exported ranges match disk/live;native layout traced;empty list only;positive action extraction and string ownership unvalidated |
| evaluation.final_action_count | Finalized action-type6..9 summary count | Native exported ranges match disk/live;0matches empty list;positive counts unvalidated |
| evaluation.unlatched_action_count | Final action summaries whose source trigger latch is zero | Native exported ranges match disk/live;0observed with no eligible actions;not universal incomplete-objective count |
| evaluation.distance_unit_flag | Final report distance display unit selector | Native exported ranges match disk/live;0before finalization,1after Tokyo exit;not a route coordinate conversion |
| train.stored_acceleration | Stored mean car acceleration, additionally history-filtered and rate-limited for player | Static producer and native unit label traced;current inspected code/constants match disk/live;stationary and moving runtime samples retained;199stationary unpaused samples,0errors,eight-car traversal,all10history indices observed;199moving samples,11cars,speed18.664..24.942m/s,stored acceleration-0.6722..0.4653,zero flagged read inconsistencies |
| car.collision_pass_accumulators | Body collision preparation accumulators | Native reset/aggregation producer verified;100samples1100body rows11player cars,zero errors/unstable checks,all four accumulators zero |
| electric.secondary_pantograph_control | Secondary electric pantograph command record | Static electric source/control routes traced;current bounded record snapshot zero-filled with gate0,not enabled transition validation |
| electric.pantograph_selector | Electric multi-position pantograph selector record | Static electric source/control routes traced;current bounded record snapshot zero-filled with gate0,not enabled transition validation |
| session.automatic_driver_enabled | Automatic player-driver mode gate | Set1/clear0/toggle and gated control dispatch traced;1 observed at ITR completion alert;automatic-player opening hold captures platform66flags0to2,countdown onset/release and unchanged zero recorded times |
| activity.platform_loading_count_overrides | Activity platform-ID loading-count override list | Lookup and caller precedence traced;current introductory list empty with stable root |
| station.boarding_vehicle_fraction | Stored fraction of eligible physical vehicles contributing to manual boarding | Current native instructions verified;negative automatic-driving fixture reads0;positive stored ratio not validated;manual tutorial initial station has6eligible/6contributing and storedfraction1;first station already loaded,no positive timer |
| station.eligible_vehicle_count | Reconstructed number of physical vehicles eligible for manual boarding | Seven synthetic edge/guard tests pass;11negative live samples show10eligible and0contributing among11vehicles;manual tutorial initial station has6eligible/6contributing and storedfraction1;first station already loaded,no positive timer |
| station.contributing_vehicle_count | Reconstructed eligible physical vehicles within selected platform endpoint interval | Seven synthetic edge/guard tests pass;11negative live samples show10eligible and0contributing among11vehicles;manual tutorial initial station has6eligible/6contributing and storedfraction1;first station already loaded,no positive timer |
