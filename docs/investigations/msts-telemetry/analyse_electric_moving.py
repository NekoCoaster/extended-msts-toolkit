"""Compare sampled electric outputs during released-brake movement."""
import json,struct
from pathlib import Path
root=Path(__file__).resolve().parent;rows=[json.loads(x) for x in (root/'captures/electric-moving-01/samples.jsonl').read_text().splitlines()];v=[r for r in rows if 'error' not in r];f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
fields=lambda key:[r['fields'][key] for r in v]
active=[r for r in v if r['fields']['controller_8c']>0 and r['fields']['lead_29e']>0]
res=[abs(r['fields']['lead_2c2']-f32(abs(r['fields']['lead_29e'])*r['fields']['definition_1da']/r['fields']['definition_102'])) for r in active]
changes=[];last=None
for r in v:
 t=r['fields']['controller_8c']
 if t!=last:changes.append(dict(time=r['time'],throttle=t,speed=r['train_speed'],force=r['fields']['lead_29e'],current=r['fields']['lead_2c2']));last=t
result=dict(samples=len(rows),errors=len(rows)-len(v),sim_time_range=[v[0]['time'],v[-1]['time']],unstable=sum(not r['stable'] for r in v),crossed_time_reads=sum(r['time']!=r['time_after'] for r in v),speed_range=[min(r['train_speed'] for r in v),max(r['train_speed'] for r in v)],changes=changes,field_ranges={k:[min(fields(k)),max(fields(k))] for k in ('lead_230','lead_29e','lead_2a2','lead_2c2','lead_492','lead_496')},active_samples=len(active),current_comparison_max_abs_error=max(res) if res else None,current_comparison_exact=sum(x==0 for x in res),last=dict(time=v[-1]['time'],paused=v[-1]['paused'],speed=v[-1]['train_speed'],fields=v[-1]['fields']),limitations='Read-only50ms asynchronous samples; current relation compared with stored shared force, not original return value. Low forward speed only. Earlier braked snapshot is separate, not simultaneous controlled crossover. No wheel-force or electrical-energy measurement; gate freshness discrepancy unresolved.')
(root/'electric-moving-summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
