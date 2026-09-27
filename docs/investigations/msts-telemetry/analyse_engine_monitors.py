"""Decode only traced monitor fields from the immutable paused capture."""
import json,struct
from pathlib import Path
root=Path(__file__).resolve().parent;data=json.loads((root/'captures/engine-monitor-state-01/monitors.json').read_text());rows=[]
for engine in data['engines']:
    for m in engine['monitors']:
        if not m['available']:continue
        raw=bytes.fromhex(m['raw']);definition=bytes.fromhex(m['definition_raw'])
        u=lambda b,o:struct.unpack_from('<I',b,o)[0]
        f=lambda b,o:struct.unpack_from('<f',b,o)[0]
        rows.append(dict(engine=engine['object_id'],monitor=m['name'],enable=u(raw,0),action=u(raw,4),
            reset_loaded_values={name:f(raw,o) for name,o in [('monitor_limit',0x10),('alarm_limit',0x14),('penalty_limit',0x18),('alarm_before_overspeed',0x1c)]},
            trigger_caches={name:u(raw,o) for name,o in [('overspeed',0x24),('high_current',0x28),('low_main_reservoir',0x2c),('over_rpm',0x30),('track_overspeed',0x34)]},
            configured_actions={name:u(definition,o) for name,o in [('full_brake',0x18),('emergency_brake',0x1c),('cuts_power',0x20),('shutdown_engine',0x24)]}))
report=dict(capture='engine-monitor-state-01',clock=data['clock'],rows=rows,limitations='Reset-source and cached-trigger interpretation only;not timer countdown units,fresh conditions or actual penalty actions. Fifth slot remains unnamed.')
(root/'engine-monitor-state-summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
