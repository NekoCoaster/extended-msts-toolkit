"""Read bounded type-5 animation slots and ordinary-wheel data, without calls."""
import argparse,datetime,hashlib,json,struct,math
from pathlib import Path
from read_live import K
from read_physical_registry import PhysicalRegistryReader
from read_wheel_animation import sample
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False)
r=PhysicalRegistryReader(a.pid)
try:
    data=dict(pid=a.pid,sha256=r.sha,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),vehicles=[])
    for car in sample(r)['vehicles'] or []:
        row=dict(object_id=car.get('object_id'),address=car['address'],train=car.get('train'))
        try:
            if 'error' in car or not car['identity_stable']:raise ValueError('Unstable source vehicle')
            if not car['shape']['available']:
                row.update(available=False,reason=car['shape'].get('reason'),shape=car['shape'])
                data['vehicles'].append(row);continue
            if not car['shape']['identity_stable']:raise ValueError('Unstable source shape')
            shape=car['shape']['address'];count,matrices,slots=struct.unpack('<III',r.read(shape+0x98,12))
            if not 0<count<=512 or not matrices or not slots:raise ValueError('Invalid bounded node layout')
            raw=r.read(slots,count*16);nodes=[]
            for i in range(count):
                callback,context,k1,k2=struct.unpack_from('<IIII',raw,i*16)
                node=dict(index=i,callback=hex(callback),context=context,key_words=[k1,k2])
                if callback==0x403512:
                    if r.read(callback,5)!=bytes.fromhex('e96a1e1d00'):raise ValueError('Wheel thunk changed')
                    node['native_target']='0x5d5381'
                if callback in (0x5d5381,0x403512):
                    if not context:raise ValueError('Null wheel callback data')
                    node['data_raw']=r.read(context,8).hex();b=bytes.fromhex(node['data_raw'])
                    node['flags_byte2']=b[2];node['car_pointer']=struct.unpack_from('<I',b,4)[0]
                    node['owner_matches']=node['car_pointer']==car['address']
                    m=r.read(matrices+i*48,48);values=struct.unpack('<12f',m)
                    if not all(math.isfinite(x) for x in values):raise ValueError('Nonfinite wheel transform')
                    node['transform_raw']=m.hex();node['transform']=values
                    node['data_stable']=r.read(context,8)==b
                nodes.append(node)
            row.update(shape=shape,node_count=count,matrices=matrices,slots=slots,nodes=nodes,
                       slots_stable=r.read(slots,count*16)==raw,
                       identity_stable=r.u(car['address']+0x50)==car['object_id'] and r.u(car['address']+0x10)==shape and r.u(shape+0x8c)==car['shape']['descriptor'] and struct.unpack('<III',r.read(shape+0x98,12))==(count,matrices,slots))
        except (OSError,ValueError) as e:row['error']=str(e)
        data['vehicles'].append(row)
    data['sim_time_after']=r.f(0x80acd4);data['sources']={}
    for name in ('read_live.py','read_physical_registry.py','read_wheel_animation.py','read_wheel_nodes.py'):
        b=(root/name).read_bytes();(out/name).write_bytes(b);data['sources'][name]=hashlib.sha256(b).hexdigest()
    (out/'nodes.json').write_text(json.dumps(data,indent=2,allow_nan=False))
    nodes=[n for v in data['vehicles'] for n in v.get('nodes',[])];w=[n for n in nodes if 'data_raw' in n]
    print(json.dumps(dict(clock=data['sim_time'],paused=data['paused'],vehicles=len(data['vehicles']),errors=[v for v in data['vehicles'] if 'error'in v],nodes=len(nodes),wheel_nodes=len(w),owner_mismatches=sum(not n['owner_matches'] for n in w),callbacks=sorted(set(n['callback'] for n in nodes)))))
finally:K.CloseHandle(r.h)
