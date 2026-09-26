"""Summarize paired service and car observations without inferring force semantics."""
import argparse,json
from collections import defaultdict
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('capture');a=p.parse_args()
root=Path(__file__).resolve().parent;rows=[json.loads(x) for x in (root/'captures'/a.capture/'samples.jsonl').read_text(encoding='utf-8').splitlines()]
groups=defaultdict(list)
for row in rows:
    for t in row.get('trains',[]):groups[(t['id'],t['is_player'])].append(t)
def bounds(v):return [min(v),max(v)] if v else None
out=dict(capture=a.capture,samples=len(rows),errors=sum('error' in r for r in rows),clock_crossings=sum(r.get('sim_time')!=r.get('sim_time_after') for r in rows if 'error' not in r),trains=[])
for (tid,player),ts in groups.items():
    cs=[c for t in ts for c in t['cars']];pc=[c for c in cs if c['powered']]
    out['trains'].append(dict(id=tid,is_player=player,samples=len(ts),car_counts=sorted(set(len(t['cars']) for t in ts)),speed=bounds([t['speed_raw'] for t in ts]),service={k:bounds([t['service'][k] for t in ts]) for k in ('speed','target','acceleration')},unstable_trains=sum(not t['service_stable'] or not t['chain_stable'] for t in ts),unstable_cars=sum(not c['stable'] for c in cs),car_fields={k:bounds([c['fields'][k] for c in cs]) for k in cs[0]['fields']} if cs else {},powered_fields={k:bounds([c['powered_fields'][k] for c in pc]) for k in pc[0]['powered_fields']} if pc else {},flags84=sorted(set(c['flags84'] for c in cs))))
out['paused_samples']=sum(r.get('paused',0)!=0 for r in rows)
out['sim_time_range']=bounds([r['sim_time'] for r in rows if 'sim_time' in r])
out['ai_stable_subset']=[]
for (tid,player),ts in groups.items():
    if player:continue
    cs=[c for t in ts for c in t['cars'] if c['stable']];pc=[c for c in cs if c['powered']]
    out['ai_stable_subset'].append(dict(id=tid,car_observations=len(cs),powered_observations=len(pc),brake_force=bounds([c['fields']['0x22c'] for c in cs]),cylinder_pressure=bounds([c['fields']['0x230'] for c in cs]),powered_fields={k:bounds([c['powered_fields'][k] for c in pc]) for k in pc[0]['powered_fields']} if pc else {}))
out['limitations']='Ranges combine vehicles and samples; not per-car transitions. Sequential reads, not atomic. Stability failure combines owner/definition/body checks and cannot uniquely diagnose a lifecycle change. No inference that zero/unmoving fields mean actual zero force or pressure.'
dest=root/(a.capture+'-summary.json');dest.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out))
