"""Compare a paused presence snapshot with physical-car track distances; multiset only."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
paths=[root/'captures/infrastructure-transition-final-paused-01/samples.jsonl',root/'captures/infrastructure-transition-track-check-01/tracks.json']
a=json.loads(paths[0].read_text(encoding='utf-8').splitlines()[0]);b=json.loads(paths[1].read_text(encoding='utf-8'))
assert a['paused'] and a['paused_after'] and b['paused']
assert a['sim_time']==a['sim_time_after']==b['sim_time']==b['sim_time_after']
trains=[]
for t in b['tracks']['trains']:
    presence=sorted((n['node'],e['node_distance']) for n in a['presence'] for e in n['entries'] if e['service']==t['service'])
    physical=sorted((c['track']['node'],c['track']['node_distance']) for c in t['cars'])
    assert len(presence)==len(physical)
    same_nodes=all(x[0]==y[0] for x,y in zip(presence,physical))
    delta=[x[1]-y[1] for x,y in zip(presence,physical)]
    row=dict(train=t['train'],service=t['service'],count=len(physical),same_nodes=same_nodes,max_distance_difference=max(abs(x) for x in delta),presence_minus_physical_min=min(delta),presence_minus_physical_max=max(delta))
    service=next(s for s in a['services']['entries'] if s['address']==t['service'])
    if not service['is_player']:
        age=a['sim_time']-service['update_candidate_floats']['0x150']
        if not 0<=age<=1:raise ValueError('Scoped check requires same-day AI update age0..1s')
        speed=abs(service['speed']);acc=service['acceleration'];target=service['target_speed']
        if acc==0:distance=age*speed;terminal=speed;branch='constant speed'
        else:
            reach=abs((target-speed)/acc)
            if reach<=age:terminal=target;distance=(age-reach)*target+(speed+target)*reach*.5;branch='target reached'
            else:terminal=speed+age*acc;distance=(speed+terminal)*age*.5;branch='accelerating toward target'
        row['ai_extrapolation']=dict(age=age,speed=speed,acceleration=acc,target=target,branch=branch,predicted_distance=distance,predicted_speed=terminal,max_absolute_gap_residual=max(abs(abs(x)-distance) for x in delta))
    trains.append(row)
out=dict(sim_time=a['sim_time'],sources=[dict(path=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths],trains=trains,limitations='Paused sorted multiset comparison,not one-to-one configuration-reference/car identity proof;no cross-node/detached-vehicle/lifecycle guarantee or atomic snapshot claim. Extrapolation is a single same-day sample reconstructed with Python double arithmetic,not instruction-exact x87/float execution. Numerical agreement does not prove the presence writer or justify a universal offset correction.')
(root/'presence-track-snapshot-check.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
