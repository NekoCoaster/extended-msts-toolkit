"""Summarize the retained yard ownership experiment; no live process access."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CAP=ROOT/'captures/yard-coupling-maneuver-01/samples.jsonl'
rows=[json.loads(s) for s in CAP.read_text().splitlines()]
ids={200000,200057,200058,200059,200060,200061}
def compact(i):
 r=rows[i]
 return dict(index=i,utc=r['utc'],sim_time=r['sim_time'],end_time=r['end_time'],paused=r['paused'],speed=r['player']['speed'],cars=[{k:c[k] for k in ('address','id','owner','body','links')} for c in r['cars'] if c['id'] in ids])
def player(r):return next(t for t in r['registry']['trains'] if t['is_player'])
edges=[]
for i in range(1,len(rows)):
 if player(rows[i])['cars']!=player(rows[i-1])['cars']:
  edges.append(dict(before=compact(i-1),after=compact(i)))
assert [len(player(rows[e['after']['index']])['cars']) for e in edges]==[6,1]
identity={str(n):sorted({(c['address'],c['body']) for r in rows for c in r['cars'] if c['id']==n}) for n in ids}
result=dict(samples=len(rows),errors=sum('error' in r for r in rows),edges=edges,
 registry_counts=sorted({r['registry']['count'] for r in rows}),
 incomplete_rows=[i for i,r in enumerate(rows) if len(r['cars'])!=r['registry']['count']],
 root_unstable=sum(not r['registry']['roots_stable'] for r in rows),
 full_clock_crossings=sum(r['sim_time']!=r['end_time'] for r in rows),
 origin_unstable=sum(not r['origin_stable'] for r in rows),
 car_unstable=sum(not c['stable'] for r in rows for c in r['cars']),
 body_unstable=sum(not c['body_stable'] for r in rows for c in r['cars']),
 identity_address_body_pairs=identity,final=compact(len(rows)-1),
 limitations='Sequential external reads are not atomic; same_sim_time covers the detail subread only. Body pointers are not stable identity. Five incomplete rows are not evidence of despawn. Transition times are sampled brackets, not native event timestamps.')
for e in edges:
 before={c['id']:c for c in e['before']['cars']};after={c['id']:c for c in e['after']['cars']}
 assert set(before)==set(after)==ids
 assert all(before[n]['address']==after[n]['address'] for n in ids)
 expected=63073680 if len(player(rows[e['after']['index']])['cars'])==6 else 0
 assert all(after[n]['owner']==expected for n in ids-{200000})
(ROOT/'coupling-transition-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('edges','identity_address_body_pairs','final')}))
