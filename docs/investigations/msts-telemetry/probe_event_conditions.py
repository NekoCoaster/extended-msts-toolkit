"""Read-only reconstruction of location-event conditions for finite normal inputs."""
import argparse,json,math,struct,shutil
from pathlib import Path
from read_live import Reader,K
from read_activity import capture

def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def inspect(r):
    start=r.f(0x80acd4);origin=list(r.unpack(0x79d118,'ii'))
    train=r.u(0x7c2ac0);car=r.u(train+0x62);pos=list(r.unpack(car+0x170,'3f'));speed=r.f(train+0x92)
    scale=r.f(0x76e48c);threshold=r.unpack(0x7706d8,'d')[0]
    if not all(math.isfinite(v) for v in pos+[speed,scale,threshold]):raise ValueError('Nonfinite inputs unsupported')
    activity=capture(r);results=[]
    for event in activity['events']:
        if event['category']!=2 or event['type']!=1:continue
        loc=event['location'];tile=loc['tile'];offset=loc['offset'];radius=loc['radius']
        if not all(math.isfinite(v) for v in offset+[radius]):raise ValueError('Nonfinite event inputs unsupported')
        target=[f32(f32(tile[i]-origin[i])*scale+offset[i]) for i in range(2)]
        delta=[f32(pos[j]-target[i]) for i,j in enumerate((0,2))]
        distance_sq=f32(sum(v*v for v in delta));inside=distance_sq<radius*radius
        stopped=abs(speed)<threshold
        results.append(dict(id=event['id'],target_local_xz=target,delta_xz=delta,distance_squared_native_candidate=distance_sq,horizontal_distance=math.sqrt(distance_sq),inside_radius=inside,stop_condition=stopped,predicate=inside and (not loc['trigger_on_stop'] or stopped),latched_raw=event['state_10'],activation_level=event['activation_level']))
    return dict(sim_time=start,event_clock=r.f(0x80acd0),origin=origin,player_train=train,first_car=car,first_car_position=pos,speed=speed,tile_scale=scale,stop_threshold=threshold,events=results,sim_time_after=r.f(0x80acd4),origin_stable=origin==list(r.unpack(0x79d118,'ii')),player_stable=train==r.u(0x7c2ac0) and car==r.u(train+0x62),paused=r.u(0x7be0f4))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pid',required=True,type=int);parser.add_argument('--name',required=True);a=parser.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Name must be one component')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        data={'image_sha256':r.sha,'snapshot':inspect(r),'limitations':'Reconstructed predicate, not native invocation or firing proof. Finite ordinary inputs only; not an exhaustive x87 rounding emulator. Reads are asynchronous.'}
        (out/'conditions.json').write_text(json.dumps(data,indent=2),encoding='utf-8')
        for name in ('probe_event_conditions.py','read_activity.py','read_live.py'):shutil.copy2(root/name,out/name)
        print(json.dumps(data))
    finally:K.CloseHandle(r.h)
