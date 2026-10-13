"""Summarize preserved electric snapshots without asserting an atomic timeline."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
names=['electric-traction-paused-01','electric-traction-braked-01','electric-traction-down-running-01','electric-traction-down-idle-01','electric-traction-restored-idle-01']
rows=[]
for name in names:
    s=json.loads((root/'captures'/name/'traction.json').read_text(encoding='utf-8'))['snapshot'];f=s['fields']
    rows.append(dict(capture=name,time=s['time'],paused=s['paused'],stable=s['stable'],cross_step=s['time']!=s['time_after'],sampled_gate_bit=s['traction_gate'],speed=f['lead_1bc'],throttle=f['controller_8c'],cached_throttle=f['lead_492'],cache_matches=f['controller_8c']==f['lead_492'],cached_limit=f['lead_496'],stored_force=f['lead_29e'],stored_power_input=f['lead_2a2'],current_source=f['lead_2c2'],cylinder=f['lead_230'],cutoff=f['definition_640']))
result=dict(snapshots=rows,limitations='Separate snapshots, no transition latency measurement. A sampled set gate bit did not guarantee cache freshness in this run. Force/power fields are internal producer outputs, not independently measured delivery.')
(root/'electric-traction-summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
