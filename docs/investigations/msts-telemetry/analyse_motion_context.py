"""Compare moving body and track increments with stored speed; descriptive only."""
import argparse,hashlib,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid name')
root=Path(__file__).resolve().parent;path=root/'captures'/a.name/'samples.jsonl'
rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines()];good=[r for r in rows if 'error' not in r]
norm=lambda v:math.sqrt(sum(x*x for x in v))
def stats(v):
    if not v:return None
    v=sorted(v);return dict(min=v[0],median=v[len(v)//2],p95=v[min(len(v)-1,int(.95*len(v)))],max=v[-1])
groups={};previous=None
for r in rows:
    if 'error' in r:previous=None;continue
    if previous is None:previous=r;continue
    dt=r['elapsed_clock']-previous['elapsed_clock']
    old={(t['id'],c['address']):(t,c) for t in previous['trains'] for c in t['cars']}
    for t in r['trains']:
        g=groups.setdefault(str(t['id']),dict(is_player=t['is_player'],eligible_moving_pairs=0,cross_clock_pairs=0,rejected_pairs=0,body_minus_speed=[],track_minus_speed=[],body_minus_track=[],stored_speed=[],day_elapsed_ratio=[],worst_body=None))
        for c in t['cars']:
            prior=old.get((t['id'],c['address']))
            if not prior:continue
            ot,oc=prior;avg=[(x+y)*.5 for x,y in zip(c['velocity'],oc['velocity'])];speed=norm(avg)
            stable=all(all(x.get(k,False) for k in ('body_pointer_stable','body_pointer_stable_after','definition_stable','links_stable','owner_stable')) and not x['derailed'] for x in (oc,c))
            same_origin=r['origin_stable'] and previous['origin_stable'] and r['origin_tile']==previous['origin_tile']
            same_track=all(c['track'][k]==oc['track'][k] for k in ('node','direction'))
            if not (0<dt<=1 and not r['paused'] and not previous['paused'] and speed>.5 and stable and same_origin and same_track and c['definition']==oc['definition'] and c['links']==oc['links'] and t['address']==ot['address']):g['rejected_pairs']+=1;continue
            body=norm([x-y for x,y in zip(c['position'],oc['position'])])/dt
            track=abs(c['track']['node_distance']-oc['track']['node_distance'])/dt
            same_clock=all(x['sim_time']==x['sim_time_after'] for x in (r,previous))
            g['eligible_moving_pairs']+=1;g['cross_clock_pairs']+=not same_clock
            for k,v in [('body_minus_speed',body-speed),('track_minus_speed',track-speed),('body_minus_track',body-track),('stored_speed',speed),('day_elapsed_ratio',(r['sim_time']-previous['sim_time'])/dt)]:g[k].append(v)
            if g['worst_body'] is None or abs(body-speed)>abs(g['worst_body']['difference']):g['worst_body']=dict(car=c['address'],time0=previous['sim_time'],time1=r['sim_time'],elapsed_dt=dt,body_speed=body,track_speed=track,stored_speed=speed,difference=body-speed,same_clock=same_clock)
    previous=r
for g in groups.values():
    for k in ('body_minus_speed','track_minus_speed','body_minus_track','stored_speed','day_elapsed_ratio'):g[k]=stats(g[k])
out=dict(capture=a.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),samples=len(rows),errors=len(rows)-len(good),sim_time_range=[good[0]['sim_time'],good[-1]['sim_time_after']],paused_samples=sum(bool(r['paused']) for r in good),max_read_seconds=max(r['monotonic_after']-r['monotonic'] for r in good),origin_tiles=sorted({tuple(r['origin_tile']) for r in good}),trains=groups,limitations='Eligible adjacent moving car pairs only:stored mean speed>0.5m/s,elapsed-clock delta0..1s,both unpaused,not derailed,stable pointers/links,unchanged origin,node and direction. Rejected pairs include stationary samples. Non-atomic;beginning clocks precede individual car reads. Norm displacement and absolute track increment are unsigned average speeds,not exact instantaneous velocity. No origin shift or node-crossing inference.')
dest=root/(a.name+'-summary.json');dest.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
