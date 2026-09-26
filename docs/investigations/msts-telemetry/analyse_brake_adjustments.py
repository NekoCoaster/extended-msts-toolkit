"""Summarize brake changes without inferring atomicity or sub-sample latency."""
import json,struct
from pathlib import Path
root=Path(__file__).resolve().parent
rows=[json.loads(x) for x in (root/'captures/brake-adjustments-01/samples.jsonl').read_text(encoding='utf-8').splitlines()]
valid=[x for x in rows if 'error' not in x];cars=lambda r:r['trains'][0]['cars'];f32=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
changes=[];last=None
for r in valid:
    v=r['train_brake']
    if v!=last:changes.append(dict(elapsed=r['elapsed'],sim_time=r['sim_time'],command=v));last=v
res=[]
for r in valid:
    for c in cars(r):
        f=c['floats'];d=c['definition_floats'];expected=f32(f32(f['0x230']/d['0x954'])*d['0x918']);res.append(abs(expected-f['0x22c']))
output=dict(samples=len(rows),errors=len(rows)-len(valid),sim_time_range=[valid[0]['sim_time'],valid[-1]['sim_time']],non_atomic_time_changes=sum(r['sim_time']!=r['sim_time_after'] for r in valid),command_changes=changes,speed_range=[min(r['speed'] for r in valid),max(r['speed'] for r in valid)],cylinder_ranges=[[min(cars(r)[i]['floats']['0x230'] for r in valid),max(cars(r)[i]['floats']['0x230'] for r in valid)] for i in range(8)],pipe_ranges=[[min(cars(r)[i]['floats']['0x238'] for r in valid),max(cars(r)[i]['floats']['0x238'] for r in valid)] for i in range(8)],unequal_cylinder_samples=sum(len(set(c['floats']['0x230'] for c in cars(r)))>1 for r in valid),unequal_pipe_samples=sum(len(set(c['floats']['0x238'] for c in cars(r)))>1 for r in valid),force_formula_max_abs_residual=max(res),force_formula_exact_count=res.count(0),force_comparisons=len(res),lead_reference_values=sorted(set(cars(r)[0]['floats']['0x268'] for r in valid)),lead_rise_latch_values=sorted(set(cars(r)[0]['integers']['0x26c'] for r in valid)),lead_fall_latch_values=sorted(set(cars(r)[0]['integers']['0x270'] for r in valid)),timer_ranges=[[min(r['timers'][i] for r in valid),max(r['timers'][i] for r in valid)] for i in range(2)],limitations='External non-atomic reads at requested50ms; no measured physical propagation speed. Simplified f32 arithmetic is not identical to x87 intermediates. Controlled keyboard actions changed self-lap setting, not a full release. No AI present.')
(root/'brake-adjustments-summary.json').write_text(json.dumps(output,indent=2),encoding='utf-8');print(json.dumps(output))
