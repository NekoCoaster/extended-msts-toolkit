"""Read loaded inputs to the traced wheel animation branch; never execute it."""
import argparse,json,hashlib,datetime
from pathlib import Path
from read_physical_registry import PhysicalRegistryReader
from read_wheel_animation import sample,finite
from read_live import K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid capture name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False)
r=PhysicalRegistryReader(a.pid)
try:
    context=r.u(0x80aa1c)
    if not context:raise ValueError('No shared context')
    default=r.u(context+0x94)
    if not default:raise ValueError('No default definition')
    data=dict(pid=a.pid,sha256=r.sha,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),context=context,default_definition=default,default_wheelset=finite(r,default+0x4e8),frame_delta=finite(r,0x828fb4),vehicles=[])
    for v in sample(r)['vehicles'] or []:
        if not v.get('driver'):continue
        car=v['address'];definition=r.u(car+0x94)
        flags=r.u(definition+0x90);local=finite(r,definition+0x4e8)
        row=dict(object_id=v['object_id'],address=car,train=v['train'],definition=definition,definition_kind=r.unpack(definition+0x88,'B')[0],car_flags80=r.u(car+0x80),car_flags84=r.u(car+0x84),definition_flags8c=r.u(definition+0x8c),definition_flags90=flags,local_wheelset=local,selected_wheelset=local if flags&0x10 else data['default_wheelset'],driver=v['driver'],shape=v['shape'])
        row['identity_stable']=v['identity_stable'] and r.u(car+0x50)==v['object_id'] and r.u(car+0x94)==definition
        data['vehicles'].append(row)
    data['context_stable']=r.u(0x80aa1c)==context and r.u(context+0x94)==default
    data['sim_time_after']=r.f(0x80acd4)
    data['sources']={}
    for name in ('read_live.py','read_physical_registry.py','read_wheel_animation.py','read_wheel_gates.py'):
        raw=(root/name).read_bytes();(out/name).write_bytes(raw);data['sources'][name]=hashlib.sha256(raw).hexdigest()
    (out/'gates.json').write_text(json.dumps(data,indent=2,allow_nan=False))
    print(json.dumps(data))
finally:K.CloseHandle(r.h)
