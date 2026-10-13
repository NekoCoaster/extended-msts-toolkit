"""Summarize emergency approach capture, retaining player/AI and sampling limits."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent;name='signal-approach-emergency-01';rows=[json.loads(x) for x in (root/'captures'/name/'samples.jsonl').read_text().splitlines()];valid=[x for x in rows if 'error' not in x];groups={};modes=[];last=None
for r in valid:
 if r['selected_mode']!=last:modes.append(dict(day=r['sim_time'],mode=hex(r['selected_mode']),handle=r['train_brake']));last=r['selected_mode']
 for t in r['trains']:
  key=('player' if t['is_player'] else 'AI')+':'+str(t['address']);g=groups.setdefault(key,dict(samples=0,car_counts=set(),unstable_owners=0,cylinder=[],pipe=[]));g['samples']+=1;g['car_counts'].add(len(t['cars']));g['unstable_owners']+=sum(not c['owner_stable'] for c in t['cars']);g['cylinder'].extend(c['floats']['0x230'] for c in t['cars']);g['pipe'].extend(c['floats']['0x238'] for c in t['cars'])
for g in groups.values():
 g['car_counts']=sorted(g['car_counts'])
 for k in ['cylinder','pipe']:g[k+'_range']=[min(g[k]),max(g[k])];del g[k]
running=[r for r in valid if not r['paused']];stopped=next((r for r in running if r['speed']==0),None)
report=dict(capture=name,samples=len(rows),errors=len(rows)-len(valid),paused_samples=sum(r['paused']!=0 for r in valid),day_range=[valid[0]['sim_time'],valid[-1]['sim_time']],speed_range=[min(r['speed'] for r in valid),max(r['speed'] for r in valid)],mode_transitions=modes,first_sampled_stop=None if stopped is None else stopped['sim_time'],crossed_clock_reads=sum(r['sim_time']!=r['sim_time_after'] for r in valid),groups=groups,final={k:valid[-1][k] for k in ['sim_time','paused','speed','selected_mode','train_brake','pipe_command']},limitation='Normal UI Backspace followed by cab view and Escape pause. Input wall time not logged in sampler. Sequential reads not atomic;first sampled zero not exact stop time. Paused final signal snapshot separate. No successful signal crossing,brake release,AI intervention or physical propagation timing claim.')
(root/'signal-approach-emergency-summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
