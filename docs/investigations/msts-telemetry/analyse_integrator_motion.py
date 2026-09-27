"""Compare the same movement pairs using gameplay and physics elapsed time."""
import argparse,hashlib,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):raise ValueError('Invalid capture name')
root=Path(__file__).resolve().parent;src=root/'captures'/a.name/'samples.jsonl'
rows=[json.loads(s) for s in src.read_text(encoding='utf-8').splitlines()]
norm=lambda v:math.sqrt(sum(x*x for x in v))
def stats(xs):
    if not xs:return None
    xs=sorted(xs);return dict(n=len(xs),min=xs[0],median=xs[len(xs)//2],p95=xs[min(len(xs)-1,int(.95*len(xs)))],max=xs[-1])
groups={};ratios=[];previous=None;clock_pairs=0
for r in rows:
    if 'error' in r:previous=None;continue
    if previous is None:previous=r;continue
    b=previous;previous=r
    dt=r['elapsed_clock']-b['elapsed_clock'];di=r['integrator']['time']-b['integrator']['time']
    if not (0<dt<=1 and 0<di<=2 and not r['paused'] and not b['paused'] and all(x['integrator_pointer_stable'] for x in (b,r)) and b['integrator']['address']==r['integrator']['address']):continue
    ratios.append(di/dt);clock_pairs+=1
    old={(t['id'],c['address']):(t,c) for t in b['trains'] for c in t['cars']}
    same_clocks=all(x['elapsed_clock']==x['elapsed_clock_after'] and x['integrator']['time']==x['integrator_after']['time'] for x in (b,r))
    for t in r['trains']:
        for c in t['cars']:
            prior=old.get((t['id'],c['address']))
            if not prior:continue
            ot,oc=prior;speed=norm([(x+y)*.5 for x,y in zip(c['velocity'],oc['velocity'])])
            stable=all(not x['derailed'] and all(x[k] for k in ('body_pointer_stable','body_pointer_stable_after','definition_stable','links_stable','owner_stable')) for x in (oc,c))
            if not (speed>.5 and stable and r['origin_stable'] and b['origin_stable'] and r['origin_tile']==b['origin_tile'] and t['address']==ot['address'] and c['definition']==oc['definition'] and c['links']==oc['links'] and all(c['track'][k]==oc['track'][k] for k in ('node','direction'))):continue
            g=groups.setdefault(str(t['id']),dict(is_player=t['is_player'],pairs=0,same_clock_pairs=0,body_game_abs_error=[],body_physics_abs_error=[],track_game_abs_error=[],track_physics_abs_error=[],same_clock_body_game_abs_error=[],same_clock_body_physics_abs_error=[],physics_game_ratio=[],worst_physics=None))
            d=norm([x-y for x,y in zip(c['position'],oc['position'])]);s=abs(c['track']['node_distance']-oc['track']['node_distance'])
            vals=dict(body_game_abs_error=abs(d/dt-speed),body_physics_abs_error=abs(d/di-speed),track_game_abs_error=abs(s/dt-speed),track_physics_abs_error=abs(s/di-speed),physics_game_ratio=di/dt)
            for k,v in vals.items():g[k].append(v)
            g['pairs']+=1;g['same_clock_pairs']+=same_clocks
            if same_clocks:
                for k in ('body_game_abs_error','body_physics_abs_error'):g['same_clock_'+k].append(vals[k])
            if g['worst_physics'] is None or vals['body_physics_abs_error']>g['worst_physics']['error']:
                g['worst_physics']=dict(car=c['address'],time0=b['sim_time'],time1=r['sim_time'],game_dt=dt,physics_dt=di,body_game_speed=d/dt,body_physics_speed=d/di,stored_speed=speed,error=vals['body_physics_abs_error'],same_clocks=same_clocks)
for g in groups.values():
    for k,v in list(g.items()):
        if isinstance(v,list):g[k]=stats(v)
good=[r for r in rows if 'error' not in r]
out=dict(capture=a.name,sha256=hashlib.sha256(src.read_bytes()).hexdigest(),samples=len(rows),errors=len(rows)-len(good),paused_samples=sum(bool(r['paused']) for r in good),time_range=[good[0]['sim_time'],good[-1]['sim_time_after']],elapsed_range=[good[0]['elapsed_clock'],good[-1]['elapsed_clock_after']],physics_range=[good[0]['integrator']['time'],good[-1]['integrator_after']['time']],modes=sorted({r['integrator']['mode'] for r in good}),configured_steps=stats([r['integrator']['configured_step'] for r in good]),clock_pairs=clock_pairs,physics_game_ratio=stats(ratios),trains=groups,limitations='Paired unsigned movement speeds versus stored mean velocity norm;no outlier removal. Physics/game clocks and car fields are sequential non-atomic reads. Same-clock means unchanged elapsed and integrator clocks within each endpoint read,not proven atomic or common producer phase. Unchanged origin,node,direction and stable identities required. Counts are correlated car pairs. Clock ratio is a measurement of this run,not a correction factor or universal solver behavior.')
(root/(a.name+'-integrator-summary.json')).write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
