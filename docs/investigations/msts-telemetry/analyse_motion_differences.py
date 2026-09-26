"""Offline finite differences; descriptive discrepancies, not solver assertions."""
import hashlib,json,math
from pathlib import Path
root=Path(__file__).resolve().parent
def norm(v):return math.sqrt(sum(x*x for x in v))
def sub(a,b):return [x-y for x,y in zip(a,b)]
def mean(a,b):return [(x+y)*.5 for x,y in zip(a,b)]
def cross(a,b):return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def stats(xs):
    if not xs:return None
    xs=sorted(xs)
    return dict(min=xs[0],median=xs[len(xs)//2],p95=xs[min(len(xs)-1,int(.95*len(xs)))],max=xs[-1])
results={}
for name in ('vehicle-motion-running-01','vehicle-motion-ai-01','vehicle-motion-restart-01'):
    path=root/'captures'/name/'samples.jsonl';groups={};previous=None;errors=0
    for line in path.read_text(encoding='utf-8').splitlines():
        row=json.loads(line)
        if 'snapshot' not in row:errors+=1;previous=None;continue
        s=row['snapshot'];s['_capture_monotonic']=row['monotonic']
        if previous is None:previous=s;continue
        dt=s['sim_time']-previous['sim_time']
        old={(t['id'],c['address']):(t,c) for t in previous['trains'] for c in t['cars']}
        for t in s['trains']:
            g=groups.setdefault(str(t['id']),dict(is_player=t['is_player'],eligible_pairs=0,rejected_pairs=0,cross_clock_pairs=0,changed_forward_with_zero_omega=0,same_clock_changed_forward_with_zero_omega=0,linear=[],angular=[],speed=[],omega=[],same_clock_linear=[],same_clock_angular=[],wall_linear=[],sim_to_wall_ratio=[],worst_linear=None,worst_angular=None))
            for c in t['cars']:
                prior=old.get((t['id'],c['address']))
                if prior is None:continue
                ot,oc=prior
                stable=all(x['body_pointer_stable'] and x['body_pointer_stable_after'] and not x['derailed'] for x in (oc,c))
                identity=oc['definition']==c['definition'] and oc['links']==c['links'] and ot['address']==t['address']
                if not (0<dt<=1 and not s['paused'] and not previous['paused'] and stable and identity):g['rejected_pairs']+=1;continue
                g['eligible_pairs']+=1
                same=all(x['sim_time']==x['sim_time_after'] for x in (previous,s))
                g['cross_clock_pairs']+=not same
                displacement=sub(c['position'],oc['position']);fd=[x/dt for x in displacement];avg=mean(c['velocity'],oc['velocity'])
                linear=norm(sub(fd,avg));omega=mean(c['angular_velocity'],oc['angular_velocity'])
                wall_dt=s['_capture_monotonic']-previous['_capture_monotonic']
                if wall_dt>0:
                    g['sim_to_wall_ratio'].append(dt/wall_dt)
                    g['wall_linear'].append(norm(sub([x/wall_dt for x in displacement],avg)))
                forward=mean(c['forward'],oc['forward']);derivative=[x/dt for x in sub(c['forward'],oc['forward'])]
                angular=norm(sub(derivative,cross(omega,forward)))
                changed=norm(derivative)>1e-6 and norm(oc['angular_velocity'])==0 and norm(c['angular_velocity'])==0
                g['changed_forward_with_zero_omega']+=changed
                g['same_clock_changed_forward_with_zero_omega']+=changed and same
                g['linear'].append(linear);g['angular'].append(angular);g['speed'].append(norm(avg));g['omega'].append(norm(omega))
                if same:g['same_clock_linear'].append(linear);g['same_clock_angular'].append(angular)
                detail=dict(car=c['address'],time0=previous['sim_time'],time1=s['sim_time'],dt=dt,wall_dt=wall_dt,finite_difference_velocity=fd,mean_velocity=avg,mean_angular_velocity=omega,forward_derivative=derivative,same_clock=same,displacement_norm=norm(displacement))
                if g['worst_linear'] is None or linear>g['worst_linear']['error']:g['worst_linear']=dict(error=linear,**detail)
                if g['worst_angular'] is None or angular>g['worst_angular']['error']:g['worst_angular']=dict(error=angular,**detail)
        previous=s
    for g in groups.values():
        for key in ('linear','angular','speed','omega','same_clock_linear','same_clock_angular','wall_linear','sim_to_wall_ratio'):g[key]=stats(g[key])
    results[name]=dict(source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),error_rows=errors,trains=groups)
out=dict(captures=results,method='Adjacent successful rows only;0<dt<=1s;both unpaused,not derailed,stable body reads,same train address/car address/definition/links. Compare position difference/dt with mean linear velocity,and forward-vector difference/dt with mean angular velocity cross mean forward vector. Same-clock subset reported separately. No outlier clipping.',limitations='Finite samples,phase/order and origin shifts can create discrepancies. Stable pointers/clock do not prove atomicity or exclude reuse. Body pointer identity itself may swap and is not required equal across samples. This tests consistency,not causation,accuracy bounds or a native derivative guarantee. Missing definition400/414 prevents endpoint reconstruction;no coupling validation.')
(root/'motion-difference-summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({name:{key:{k:v for k,v in g.items() if not k.startswith('worst')} for key,g in r['trains'].items()} for name,r in results.items()},indent=2))
