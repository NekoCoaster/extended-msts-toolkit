"""Compare derived connection-state rate with observed endpoint-gap changes."""
import argparse,hashlib,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid name')
root=Path(__file__).resolve().parent;path=root/'captures'/a.name/'samples.jsonl'
norm=lambda x:math.sqrt(sum(v*v for v in x))
sub=lambda a,b:[x-y for x,y in zip(a,b)]
def endpoint(c,sign):
    local=[0,1-c['vertical_parameter'],sign*.5*c['length']]
    offset=[sum(local[j]*c[k][i] for j,k in enumerate(('right','up','forward'))) for i in range(3)]
    world=[c['position'][i]+offset[i] for i in range(3)];w=c['angular_velocity']
    rot=[w[1]*offset[2]-w[2]*offset[1],w[2]*offset[0]-w[0]*offset[2],w[0]*offset[1]-w[1]*offset[0]]
    return world,[c['velocity'][i]+rot[i] for i in range(3)]
def pairs(t):
    cars={c['address']:c for c in t['cars']};out={}
    for c in cars.values():
        n=cars.get(c['links'][1])
        if n is None:continue
        p,v=endpoint(c,-1);q,u=endpoint(n,1);delta=sub(q,p);gap=norm(delta)
        rate=sum(x*y for x,y in zip(sub(u,v),delta))/gap if gap>1e-7 else 0
        valid=n['links'][0]==c['address'] and all(not x['derailed'] and all(x[k] for k in ('body_pointer_stable','body_pointer_stable_after','definition_stable','links_stable','owner_stable')) for x in (c,n))
        out[(c['address'],n['address'])]=dict(gap=gap,rate=rate,valid=valid,definitions=[c['definition'],n['definition']])
    return out
def stats(xs):
    if not xs:return None
    xs=sorted(xs);return dict(min=xs[0],median=xs[len(xs)//2],p95=xs[min(len(xs)-1,int(.95*len(xs)))],max=xs[-1])
groups={};previous=None
for line in path.read_text(encoding='utf-8').splitlines():
    r=json.loads(line)
    if 'error' in r:previous=None;continue
    current={t['id']:(t,pairs(t)) for t in r['trains']}
    if previous is not None:
        before,old=previous;dt=r['elapsed_clock']-before['elapsed_clock']
        if 0<dt<=1 and not r['paused'] and not before['paused'] and r['origin_stable'] and before['origin_stable'] and r['origin_tile']==before['origin_tile']:
            for key,(t,ps) in current.items():
                if key not in old:continue
                ot,ops=old[key]
                if ot['address']!=t['address'] or max(abs(t['speed_raw']),abs(ot['speed_raw']))<=.5:continue
                g=groups.setdefault(str(key),dict(is_player=t['is_player'],eligible_pairs=0,cross_clock_pairs=0,gap=[],stored_state_rate=[],gap_difference_rate=[],absolute_rate_difference=[],same_clock_absolute_rate_difference=[],worst=None))
                for pair,s in ps.items():
                    o=ops.get(pair)
                    if o is None or not s['valid'] or not o['valid'] or s['definitions']!=o['definitions']:continue
                    fd=(s['gap']-o['gap'])/dt;rate=(s['rate']+o['rate'])*.5;error=abs(fd-rate)
                    same=all(x['sim_time']==x['sim_time_after'] for x in (r,before))
                    g['eligible_pairs']+=1;g['cross_clock_pairs']+=not same
                    for name,value in [('gap',s['gap']),('stored_state_rate',rate),('gap_difference_rate',fd),('absolute_rate_difference',error)]:g[name].append(value)
                    if same:g['same_clock_absolute_rate_difference'].append(error)
                    if g['worst'] is None or error>g['worst']['error']:g['worst']=dict(pair=pair,time0=before['sim_time'],time1=r['sim_time'],gap0=o['gap'],gap1=s['gap'],rate=rate,finite_difference=fd,error=error,same_clock=same)
    previous=(r,current)
for g in groups.values():
    for k in ('gap','stored_state_rate','gap_difference_rate','absolute_rate_difference','same_clock_absolute_rate_difference'):g[k]=stats(g[k])
out=dict(capture=a.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),trains=groups,limitations='Adjacent unpaused samples with elapsed delta0..1s,unchanged origin,stable reciprocal car pairs/definitions and train speed>0.5 at either end. Endpoint formulas reconstructed in double precision;epsilon1e-7 approximate. Non-atomic reads and asynchronous placement can create apparent gap jumps. No force/slack truth claim;no sign-agreement guarantee or tolerances inferred from these distributions.')
(root/(a.name+'-connections.json')).write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
