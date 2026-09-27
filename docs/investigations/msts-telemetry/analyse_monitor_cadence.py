"""Summarize monitor sequence changes, distinguishing paused and running samples."""
import argparse,json,struct,collections
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();root=Path(__file__).resolve().parent
if Path(a.name).name!=a.name:p.error('Invalid name')
rows=[json.loads(x) for x in (root/'captures'/a.name/'samples.jsonl').read_text().splitlines()];ok=[x for x in rows if 'error' not in x];result=dict(capture=a.name,samples=len(rows),errors=sum('error'in x for x in rows),unstable_context=sum(not x['context_stable'] for x in ok),paused_samples=sum(bool(x['paused']) for x in ok),day_range=[min(x['day'] for x in ok),max(x['day'] for x in ok)],physics_range=[min(x['physics_time'] for x in ok),max(x['physics_time'] for x in ok)],intervals=sorted(set(x['interval'] for x in ok)),monitors={})
for name in ('aws','vigilance','emergency','unnamed','overspeed'):
 raw=[bytes.fromhex(x['monitors'][name]['raw']) for x in ok];fields={}
 for label,off,fmt in [('enable',0,'I'),('action',4,'I'),('alarm',8,'I'),('penalty_latch',12,'I'),('monitor_remaining',16,'f'),('alarm_remaining',20,'f'),('penalty_remaining',24,'f'),('overspeed_remaining',28,'f'),('input',32,'f')]:
  values=[struct.unpack_from('<'+fmt,b,off)[0] for b in raw];deltas=collections.Counter(round(b-a,8) for a,b in zip(values,values[1:]) if a!=b)
  fields[label]=dict(min=min(values),max=max(values),changes=sum(deltas.values()),deltas=dict(deltas.most_common(12)))
 result['monitors'][name]=dict(fields=fields,unstable_reads=sum(not x['monitors'][name]['stable'] for x in ok),changes_between_paused_samples=sum(raw[i]!=raw[i-1] for i in range(1,len(ok)) if ok[i]['paused'] and ok[i-1]['paused']))
result['limitations']='Sequential50ms samples may miss intermediate changes;no direct alarm audibility,intervention or AI-monitor test. Paused transitions are separated but not atomic. Compare clocks without assuming identical cadence.'
(root/(a.name+'-summary.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result))
