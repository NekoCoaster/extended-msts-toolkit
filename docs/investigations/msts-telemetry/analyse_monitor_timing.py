"""Summarize paused monitor timing context without changing retained capture files."""
import json,struct
from pathlib import Path
root=Path(__file__).resolve().parent
capture='captures/engine-monitor-timing-paused-01/monitors.json'
data=json.loads((root/capture).read_text())
rows=[]
for engine in data['engines']:
 for m in engine['monitors']:
  if not m['available']:continue
  raw=bytes.fromhex(m['raw']);cfg=bytes.fromhex(m['definition_raw'])
  f=lambda b,o:struct.unpack_from('<f',b,o)[0]
  rows.append(dict(engine=engine['object_id'],monitor=m['name'],enable=m['enable_raw'],state_input=f(raw,0x20),critical_level=f(cfg,0x10),reset_level=f(cfg,0x14),speed=engine['stored_speed'],speed_times_native_mph_factor=engine['stored_speed']*2.236936092376709,state_stable=m['state_stable'],definition_stable=m['definition_stable']))
report=dict(capture=capture,clock=data['clock'],paused=data['paused'],timing=data['player_timing'],rows=rows,limitations='Paused sequential snapshot; only diesel overspeed input producer traced here. Speed and cached input need not refer to the same integration step. Seconds interpretation inherits prior scheduler runtime corroboration; no monitor running-rate or penalty test.')
(root/'monitor-timing-summary.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
