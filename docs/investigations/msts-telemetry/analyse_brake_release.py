"""Summarize confirmed release and settling, keeping capture gaps explicit."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent;output={}
for name in ('brake-release-02','brake-release-settling-01'):
 rows=[json.loads(x) for x in (root/'captures'/name/'samples.jsonl').read_text().splitlines()];v=[x for x in rows if 'error' not in x];cars=lambda r:r['trains'][0]['cars'];changes=[];last=None
 for r in v:
  if r['selected_mode']!=last:changes.append(dict(time=r['sim_time'],mode=hex(r['selected_mode']),handle=r['train_brake']));last=r['selected_mode']
 output[name]=dict(samples=len(rows),errors=len(rows)-len(v),sim_time_range=[v[0]['sim_time'],v[-1]['sim_time']],mode_transitions=changes,paused_end=v[-1]['paused'],speed_range=[min(r['speed'] for r in v),max(r['speed'] for r in v)],cylinder_ranges=[[min(cars(r)[i]['floats']['0x230'] for r in v),max(cars(r)[i]['floats']['0x230'] for r in v)] for i in range(8)],final_cylinders=[c['floats']['0x230'] for c in cars(v[-1])],final_pipe=[c['floats']['0x238'] for c in cars(v[-1])],fall_latch_values=sorted(set(cars(r)[0]['integers']['0x270'] for r in v)),fall_timer_range=[min(r['timers'][1] for r in v),max(r['timers'][1] for r in v)],lead_reference_range=[min(cars(r)[0]['floats']['0x268'] for r in v),max(cars(r)[0]['floats']['0x268'] for r in v)],unequal_pipe_samples=sum(len(set(c['floats']['0x238'] for c in cars(r)))>1 for r in v),unequal_cylinder_samples=sum(len(set(c['floats']['0x230'] for c in cars(r)))>1 for r in v),crossed_time_reads=sum(r['sim_time']!=r['sim_time_after'] for r in v))
output['limitations']='Separate bounded captures have an unobserved gap; do not concatenate as continuous. Sequential50ms reads do not measure physical propagation speed. Modes4/10hex/1000hex validated for this player Acela; AI and other brake types untested. Latch transitions are not proof of audible playback.'
(root/'brake-release-summary.json').write_text(json.dumps(output,indent=2),encoding='utf-8');print(json.dumps(output))
