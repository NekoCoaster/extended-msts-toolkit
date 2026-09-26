# Telemetry discovery inventory (work in progress)

{'runtime_direct': 215, 'runtime_derived': 16, 'cab_channels': 68, 'installed_cab_channels': 59, 'config_paths': 507, 'config_leaf_paths': 474, 'config_mixed_paths': 37, 'files_scanned': 126, 'total': 806}

No priorities or keep/drop decisions. See inventory.json for full provenance and per-field limitations.

| Candidate | Meaning | Evidence status |
|---|---|---|
| simulation.time | Simulation time value; observed near activity seconds since midnight | readable in live captures; semantics partly inherited/static |
| simulation.step | Simulation frame delta | readable in live captures; semantics partly inherited/static |
| simulation.paused | Pause state | readable in live captures; semantics partly inherited/static |
| train.registry | Currently registered train identities; future unspawned services excluded | readable in live captures; semantics partly inherited/static |
| train.identity | Native train identifier | readable in live captures; semantics partly inherited/static |
| train.kind_raw | Native train kind byte; player observed 3 and AI 1 | readable in live captures; semantics partly inherited/static |
| train.is_player | Train matches selected player global | readable in live captures; semantics partly inherited/static |
| train.speed | Native signed train speed; compare with per-body speed | readable in live captures; semantics partly inherited/static |
| train.first_car | First car pointer | readable in live captures; semantics partly inherited/static |
| train.last_car | Last car pointer | readable in live captures; semantics partly inherited/static |
| train.lead_car | Lead/controlled car pointer | readable in live captures; semantics partly inherited/static |
| train.service_pointer | Associated service/runtime object; fields not decoded yet | readable in live captures; semantics partly inherited/static |
| car.identity | Vehicle instance address | readable in live captures; semantics partly inherited/static |
| car.train_owner | Owning train | readable in live captures; semantics partly inherited/static |
| car.links | Connections at both ends | readable in live captures; semantics partly inherited/static |
| car.definition | Shared vehicle definition | readable in live captures; semantics partly inherited/static |
| car.asset_directory | Trainset directory/name string | readable in live captures; semantics partly inherited/static |
| car.powered | Definition identifies powered vehicle | readable in live captures; semantics partly inherited/static |
| car.body_pointer | Current integration body pointer | readable in live captures; semantics partly inherited/static |
| body.position | Simulation physics position vector; world/tile origin mapping unresolved | readable in live captures; semantics partly inherited/static |
| body.right | Orientation right basis | readable in live captures; semantics partly inherited/static |
| body.up | Orientation up basis | readable in live captures; semantics partly inherited/static |
| body.forward | Orientation forward basis | readable in live captures; semantics partly inherited/static |
| body.velocity | Linear velocity vector | readable in live captures; semantics partly inherited/static |
| body.angular_velocity | Angular velocity | readable in live captures; semantics partly inherited/static |
| body.momentum | Linear momentum | readable in live captures; semantics partly inherited/static |
| body.angular_momentum | Angular momentum | readable in live captures; semantics partly inherited/static |
| body.inverse_mass | Inverse mass | readable in live captures; semantics partly inherited/static |
| body.flags_raw | Body flags including physical derailment and resting | readable in live captures; semantics partly inherited/static |
| body.derailed | Physical derailment flag | readable in live captures; semantics partly inherited/static |
| body.resting | Resting flag | readable in live captures; semantics partly inherited/static |
| engine.definition | Engine definition | readable in live captures; semantics partly inherited/static |
| engine.max_power | Configured maximum power | readable in live captures; semantics partly inherited/static |
| engine.max_force | Configured maximum force | readable in live captures; semantics partly inherited/static |
| player.control_type | Steam/diesel/electric controller type | readable in live captures; semantics partly inherited/static |
| player.throttle | Throttle/regulator fraction | readable in live captures; semantics partly inherited/static |
| player.reverser | Signed reverser setting | readable in live captures; semantics partly inherited/static |
| monitor.event_type | Upcoming track-monitor element type | readable in live captures; semantics partly inherited/static |
| monitor.distance | Distance to upcoming element | readable in live captures; semantics partly inherited/static |
| monitor.radius | Radius associated with element | readable in live captures; semantics partly inherited/static |
| monitor.gradient | Gradient associated with element | readable in live captures; semantics partly inherited/static |
| monitor.desired_velocity | Desired velocity associated with element, not necessarily posted limit | readable in live captures; semantics partly inherited/static |
| monitor.object | Referenced route/signal object identity | readable in live captures; semantics partly inherited/static |
| signal.flags_raw | Referenced signal flags; full aspect mapping unresolved | readable in live captures; semantics partly inherited/static |
| car.mass | Vehicle mass | derived candidate; not all computations implemented |
| car.longitudinal_speed | Speed projected along body axis | derived candidate; not all computations implemented |
| train.car_count | Number of connected vehicles | derived candidate; not all computations implemented |
| train.total_mass | Connected consist mass | derived candidate; not all computations implemented |
| car.speed_magnitude | Total 3D speed | derived candidate; not all computations implemented |
| car.acceleration | Sampled acceleration | derived candidate; not all computations implemented |
| car.heading_pitch_roll | Orientation angles | derived candidate; not all computations implemented |
| train.relative_motion | Relative train separation and closing speed | derived candidate; not all computations implemented |
| train.lifecycle_events | Spawn/despawn, coupling/splitting and player selection changes | derived candidate; not all computations implemented |
| car.wheel_rotation_estimate | Rolling wheel speed estimate | derived candidate; not all computations implemented |
| cab.ALERTER_DISPLAY | alerter display native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.AMMETER | ammeter native cab input/display channel | native diesel producer traced; paused pressures matched cab display; dynamic transitions recorded separately |
| cab.ASPECT_DISPLAY | aspect display native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.BELL | bell native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.BLOWER | blower native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.BOILER_WATER | boiler water native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.BRAKE_CYL | brake cyl native cab input/display channel | native diesel producer traced; paused pressures matched cab display; dynamic transitions recorded separately |
| cab.BRAKE_PIPE | brake pipe native cab input/display channel | native diesel producer traced; paused pressures matched cab display; dynamic transitions recorded separately |
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
| cab.EQ_RES | eq res native cab input/display channel | native diesel producer traced; paused pressures matched cab display; dynamic transitions recorded separately |
| cab.FIREBOX | firebox native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.FIREHOLE | firehole native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.FRICTION_BRAKING | friction braking native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.FRONT_HLIGHT | front hlight native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.GEARS | gears native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.HORN | horn native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.LINE_VOLTAGE | line voltage native cab input/display channel | native name and static dispatcher mapping; runtime support depends on channel and engine |
| cab.LOAD_METER | load meter native cab input/display channel | native diesel producer traced; paused pressures matched cab display; dynamic transitions recorded separately |
| cab.MAIN_RES | main res native cab input/display channel | native diesel producer traced; paused pressures matched cab display; dynamic transitions recorded separately |
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
| config..eng:Wagon.BrakeAirPressureGainInResForOnePoundFromPipe | Wagon.BrakeAirPressureGainInResForOnePoundFromPipe configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.BrakeCylinderPressureForMaxBrakeBrakeForce | Wagon.BrakeCylinderPressureForMaxBrakeBrakeForce configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.BrakeDistributorApplicationRate | Wagon.BrakeDistributorApplicationRate configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.BrakeDistributorEmergencyResPressure | Wagon.BrakeDistributorEmergencyResPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.BrakeDistributorFullServicePressure | Wagon.BrakeDistributorFullServicePressure configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.BrakeDistributorMaxAuxilaryResPressure | Wagon.BrakeDistributorMaxAuxilaryResPressure configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.BrakeDistributorNormalFullReleasePressure | Wagon.BrakeDistributorNormalFullReleasePressure configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.BrakeDistributorReleaseRate | Wagon.BrakeDistributorReleaseRate configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.BrakeDistributorTrainPipeControlRatio | Wagon.BrakeDistributorTrainPipeControlRatio configured value | static configuration extracted; not a live changing value |
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
| config..eng:Wagon.EmergencyResCapacity | Wagon.EmergencyResCapacity configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.EmergencyResChargingRate | Wagon.EmergencyResChargingRate configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.EmergencyResVolumeMultiplier | Wagon.EmergencyResVolumeMultiplier configured value | static configuration extracted; not a live changing value |
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
| config..eng:Wagon.MaxApplicationRate | Wagon.MaxApplicationRate configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.MaxAuxilaryChargingRate | Wagon.MaxAuxilaryChargingRate configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.MaxBrakeForce | Wagon.MaxBrakeForce configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.MaxHandbrakeForce | Wagon.MaxHandbrakeForce configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.MaxReleaseRate | Wagon.MaxReleaseRate configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.NumWheels | Wagon.NumWheels configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.NumberOfHandbrakeLeverSteps | Wagon.NumberOfHandbrakeLeverSteps configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.PassengerCapacity | Wagon.PassengerCapacity configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Size | Wagon.Size configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Sound | Wagon.Sound configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.Thumbnail | Wagon.Thumbnail configured value | static configuration extracted; not a live changing value |
| config..eng:Wagon.TripleValveRatio | Wagon.TripleValveRatio configured value | static configuration extracted; not a live changing value |
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
| config..wag:Wagon.BrakeCylinderPressureForMaxBrakeBrakeForce | Wagon.BrakeCylinderPressureForMaxBrakeBrakeForce configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.BrakeDistributorApplicationRate | Wagon.BrakeDistributorApplicationRate configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.BrakeDistributorEmergencyResPressure | Wagon.BrakeDistributorEmergencyResPressure configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.BrakeDistributorFullServicePressure | Wagon.BrakeDistributorFullServicePressure configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.BrakeDistributorMaxAuxilaryResPressure | Wagon.BrakeDistributorMaxAuxilaryResPressure configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.BrakeDistributorNormalFullReleasePressure | Wagon.BrakeDistributorNormalFullReleasePressure configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.BrakeDistributorReleaseRate | Wagon.BrakeDistributorReleaseRate configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.BrakeDistributorTrainPipeControlRatio | Wagon.BrakeDistributorTrainPipeControlRatio configured value | static configuration extracted; not a live changing value |
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
| config..wag:Wagon.EmergencyResCapacity | Wagon.EmergencyResCapacity configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.EmergencyResChargingRate | Wagon.EmergencyResChargingRate configured value | static configuration extracted; not a live changing value |
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
| config..wag:Wagon.MaxApplicationRate | Wagon.MaxApplicationRate configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.MaxAuxilaryChargingRate | Wagon.MaxAuxilaryChargingRate configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.MaxBrakeForce | Wagon.MaxBrakeForce configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.MaxHandbrakeForce | Wagon.MaxHandbrakeForce configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.MaxReleaseRate | Wagon.MaxReleaseRate configured value | static configuration extracted; not a live changing value |
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
| config..wag:Wagon.RetainingValveSlowReleaseRate | Wagon.RetainingValveSlowReleaseRate configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Size | Wagon.Size configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Sound | Wagon.Sound configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.Thumbnail | Wagon.Thumbnail configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.TrainPipeLeakRate | Wagon.TrainPipeLeakRate configured value | static configuration extracted; not a live changing value |
| config..wag:Wagon.TripleValveRatio | Wagon.TripleValveRatio configured value | static configuration extracted; not a live changing value |
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
| signal.next_iterator | Player next-signal track iterator | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear |
| signal.next_distance | Distance to player next signal | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear |
| signal.head_identity | Directional signal head identity | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear |
| signal.function_type | Signal head function selector | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear |
| signal.aspect | Live aspect of directional head; select maximum aspect among normal heads for monitor | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear |
| signal.aspect_speed | Speed associated with current signal aspect | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear |
| signal.aspect_flags | Flags associated with aspect definition | native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear |
| service.posted_speed_cap | Posted speed restriction retained by the service | native setters and effective selection traced; all three paused service caps reproduced exactly; posted-limit crossing transition not captured |
| service.additional_speed_cap | Additional retained cap set by certain speedposts and service initialization | native setters and effective selection traced; all three paused service caps reproduced exactly; posted-limit crossing transition not captured |
| service.scheduled_start | Loaded service scheduled activation time | native scheduler semantics traced and bytes verified; paused active/inactive AI corroborated; exact gate transition not captured |
| service.update_active | Gate admitting AI service to scheduled kinematic update | native scheduler semantics traced and bytes verified; paused active/inactive AI corroborated; exact gate transition not captured |
| service.integration_interval | Service scheduler integration interval | native scheduler semantics traced and bytes verified; paused active/inactive AI corroborated; exact gate transition not captured |
| service.last_update_time | AI kinematic scheduler last-update time; player has different observed time base | native scheduler semantics traced and bytes verified; paused active/inactive AI corroborated; exact gate transition not captured |
| service.travel_sign_selector | Kinematic travel sign selector | native scheduler semantics traced and bytes verified; paused active/inactive AI corroborated; exact gate transition not captured |
| service.registry | Loaded AI service list, including services without instantiated trains | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven |
| service.key | Service asset key | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.display_name | Service display name | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.train_config | Configured consist reference | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.path_id | Configured path reference | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.id | Service identifier used by native lookup | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.train_id | Associated train identifier, allocated before physical train exists | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.train_pointer | Physical train backlink; may be null | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven |
| service.physicalized_raw | AI physical-instance lifecycle flag | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven |
| service.flags_raw | Service state flags | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven |
| service.speed | Service signed current speed | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven |
| service.target_speed | AI target speed used by kinematic integrator | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven |
| service.acceleration | AI acceleration used by kinematic integrator | native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven |
| service.efficiency_candidate | Speed and acceleration scaling factor; matches configured Efficiency in observed services | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.effective_speed_limit | Combined effective speed cap used by driver and player UI | native setters and effective selection traced; all three paused service caps reproduced exactly; posted-limit crossing transition not captured |
| service.signal_speed_cap | Signal-related cap retained by driver | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.configured_speed_cap_candidate | Base speed cap before service efficiency scaling | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.stop_timer_remaining | Timed stop countdown candidate | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.stop_timer_active | Timed stop countdown gate | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.path_end_stop | Path-end stop condition candidate | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.wait_braking | Waiting sequence braking state candidate | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.wait_active | Waiting sequence dwell state candidate | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.wait_elapsed | Waiting sequence elapsed time | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
| service.wait_duration | Waiting sequence duration threshold | native code traced and paused values readable; lifecycle and changing driver transitions not yet validated |
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
| track.node | Track node identity | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.section_index | Section ordinal within track node | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.section | Track section instance identity | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.direction | Track traversal direction | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.node_distance | Distance along current node | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.section_distance | Distance along current section | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.local_position | Track reference point in current local coordinates | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.angles_candidate | Track orientation angles | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.section_origin_tile | Section origin tile indices | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.section_origin_offset | Section origin offset inside tile | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.section_definition_index | Track geometry definition reference | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.node_length | Total track-node length | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.node_section_count | Number of sections in node | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| track.route_position_candidate | Origin-independent route coordinate reconstruction | native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending |
| topology.reachable_graph | Track graph reachable from loaded service positions | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.node_kind | Native track node kind | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.links | Connected node pointers and traversal direction bytes | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.input_pin_count | Endpoint input-side pin count | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.output_pin_count | Endpoint output-side pin count | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.selected_branch | Junction branch selector consumed by native track traversal | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.selected_connection | Junction connection selected when entering from input side | native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested |
| topology.route_node_id_candidate | TDB node ID derived by geometry and connectivity matching | all 732 registry-derived route IDs validated in current route; earlier geometry ambiguity resolved |
| infrastructure.route_databases | Loaded track database registry | native traversal/release traced; complete 732-node route match; paused presence and associations readable |
| infrastructure.all_nodes | All registered track nodes including disconnected components | native traversal/release traced; complete 732-node route match; paused presence and associations readable |
| infrastructure.track_items | Database-wide track-item registry | native traversal/release traced; complete 732-node route match; paused presence and associations readable |
| infrastructure.item_kind | Native track-item subtype discriminator | all 2970 live item indexes matched TDB subtype names; native serializer supports observed mapping |
| infrastructure.signal_service_association | Service associated with a signal object | native traversal/release traced; complete 732-node route match; paused presence and associations readable |
| infrastructure.vector_presence | Abstract per-car position records linked to a vector track segment | native traversal/release traced; complete 732-node route match; paused presence and associations readable |
| infrastructure.presence_service | Service identity attached to track-presence record | native traversal/release traced; complete 732-node route match; paused presence and associations readable |
| infrastructure.presence_node_distance | Position of abstract car record along its track node | native traversal/release traced; complete 732-node route match; paused presence and associations readable |
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
| track_item.platform_waiting_passengers | Stored waiting passenger count | native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances |
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
| activity.event_registry | Loaded activity event list | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.id | Activity-defined event ID | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.category | Native event category | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.type | Native event type | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.state_10 | Runtime event state used by work-order display | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.state_20 | Runtime activation-related state candidate | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.activation_level | Stored activation level | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.location_tile | Location trigger tile pair | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.location_offset | Location trigger X/Z inside tile | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.location_radius | Location trigger radius | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.trigger_on_stop | Location event requires stopping | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.outcome_count | Number of event outcomes | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.outcomes | Outcome records: type, argument and payload reference | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| activity.event.reversible_candidate | Reversible-event marker candidate | three loaded location events corroborated against ACT file; runtime trigger/state transitions untested |
| car.brake_cylinder_pressure | Per-car brake cylinder pressure | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| car.brake_pipe_pressure | Per-car brake-pipe pressure | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| car.brake_force_candidate | Per-car requested brake-force quantity before adhesion limiting | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| car.max_brake_force | Loaded MaxBrakeForce configuration | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| car.brake_reference_pressure_candidate | Brake pressure used to scale configured force | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| car.connection_force_candidate | Connection-force quantity at one consist end | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| car.connection_break_threshold_candidate | Coupling-force threshold used to uncouple | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| body.force_accumulator_candidate | Body force accumulator | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| body.torque_accumulator_candidate | Body torque accumulator | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| body.inverse_inertia_world | World inverse inertia tensor | static source tracing plus stopped-player values during running simulation; independent AI population untested |
| session.weather_raw | Loaded activity weather selection | loaded values match ACT; elapsed is derived and midnight semantics untested |
| session.season_raw | Loaded activity season selection | loaded values match ACT; elapsed is derived and midnight semantics untested |
| session.start_hms | Loaded activity starting clock | loaded values match ACT; elapsed is derived and midnight semantics untested |
| session.duration_hm | Configured activity duration | loaded values match ACT; elapsed is derived and midnight semantics untested |
| session.start_seconds | Activity start clock in seconds | loaded values match ACT; elapsed is derived and midnight semantics untested |
| session.elapsed_candidate | Elapsed simulation time since activity start | loaded values match ACT; elapsed is derived and midnight semantics untested |
| camera.mode | Player view mode raw enum | native consumers traced; cab/front/rear/trackside/cab switches observed with matching post-input snapshots |
| camera.tracking | Player camera tracking state used by native debug display | native consumers traced; cab/front/rear/trackside/cab switches observed with matching post-input snapshots |
| camera.render_position | Current render-camera position | native consumers traced; cab/front/rear/trackside/cab switches observed with matching post-input snapshots |
| camera.render_basis | Current render-camera basis vectors | native consumers traced; cab/front/rear/trackside/cab switches observed with matching post-input snapshots |
