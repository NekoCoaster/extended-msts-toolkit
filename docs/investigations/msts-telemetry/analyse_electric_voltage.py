"""Summarize electric display-gate transitions without treating them as physics power."""
from pathlib import Path
import json
root=Path(__file__).resolve().parent
records=[json.loads(l) for l in (root/'captures/electric-voltage-transition-01/samples.jsonl').read_text(encoding='utf-8').splitlines()]
rows=[r['snapshot'] for r in records if 'snapshot' in r];events=[];last=None
for i,r in enumerate(rows):
 state=(r['pantograph_control'],r['gate_passed'],r['derived_display_voltage'])
 if state!=last:events.append(dict(index=i,time=r['time'],pantograph=state[0],gate=state[1],derived_voltage=state[2],cars_checked=len(r['car_checks'])));last=state
result=dict(samples=len(rows),errors=[r for r in records if 'error'in r],unstable=sum(not r['stable'] for r in rows),cross_step=sum(r['time']!=r['time_after'] for r in rows),paused=sum(bool(r['paused']) for r in rows),route_voltage_values=sorted(set(r['route_voltage'] for r in rows)),events=events,limitations='Derived native display rule, not direct cab-object output or traction power. Sample timing is external and non-atomic.')
(root/'electric-voltage-summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
