"""Summarize diesel reset attempt and bracketing signal observations."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent;name='diesel-emergency-reset-01';rows=[json.loads(l) for l in (root/'captures'/name/'samples.jsonl').read_text().splitlines()];v=[r for r in rows if 'error'not in r];trans=[];last=None
for r in v:
 key=(r['selected_mode'],r['train_brake'])
 if key!=last:trans.append(dict(day=r['sim_time'],mode=hex(key[0]),handle=key[1]));last=key
signals=[]
for n in ['approach-stopped-signal-01','diesel-reset-signal-paused-01']:
 r=json.loads((root/'captures'/n/'details.jsonl').read_text().splitlines()[-1]);signals.append(dict(capture=n,day=r['sim_time'],paused=r['paused'],speed=r['player']['speed'],throttle=r['diesel_cab']['throttle'],signal=r['next_signal']))
report=dict(samples=len(rows),errors=len(rows)-len(v),day_range=[v[0]['sim_time'],v[-1]['sim_time']],paused_samples=sum(r['paused']!=0 for r in v),clock_crossings=sum(r['sim_time']!=r['sim_time_after'] for r in v),speed_range=[min(r['speed'] for r in v),max(r['speed'] for r in v)],transitions=trans,final={k:v[-1][k] for k in ['sim_time','paused','speed','selected_mode','train_brake','pipe_command']},signals=signals,limitations='Three semicolon presses after throttleIdle and Backspace. Two lever drags did not yield release. Selector/control updates can straddle reads. Signal sampled only at interval endpoints;exact clearance time and exclusive causal attribution unproven. No successful passage or brake release.')
(root/'diesel-emergency-reset-summary.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:z for k,z in report.items() if k!='signals'}))
p=Path('C:/MSTS/TRAINS/TRAINSET/DASH9/CABVIEW/dash9.cvf');b=p.read_bytes();s=b.decode('utf-16') if b[:2]==b'\xff\xfe' else b.decode('cp1252');ls=s.splitlines();i=next(i for i,l in enumerate(ls) if 'TRAIN_BRAKE LEVER' in l)
(root/'diesel-brake-cab-provenance.json').write_text(json.dumps(dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),first_line=i+1,excerpt=ls[i:i+12],limitation='Installed cab declaration;does not by itself prove scaled mouse interaction or release direction.'),indent=2))
