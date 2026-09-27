"""Read the two bounded wheel-transform groups used by the native type-4 branch."""
import argparse,json,struct,math,hashlib,datetime
from pathlib import Path
from read_live import K
from read_physical_registry import PhysicalRegistryReader
from read_wheel_animation import sample
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=PhysicalRegistryReader(a.pid)
def matrix(pointer):
    if not pointer:return None
    raw=r.read(pointer,48);values=struct.unpack('<12f',raw)
    if not all(math.isfinite(x) for x in values):raise ValueError('Nonfinite matrix')
    return dict(address=pointer,raw=raw.hex(),values=values,reread_stable=r.read(pointer,48)==raw)
try:
    data=dict(pid=a.pid,sha256=r.sha,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),clock=r.f(0x80acd4),paused=r.u(0x7be0f4),vehicles=[])
    for v in sample(r)['vehicles'] or []:
        car=v['address'];row=dict(address=car,object_id=v.get('object_id'),train=v.get('train'))
        try:
            if 'error'in v or not v['identity_stable']:raise ValueError('Unstable source')
            shape=r.u(car+0x10);kind=r.unpack(shape+8,'H')[0];table=r.u(shape)
            row.update(shape=shape,kind=kind,table=table)
            if kind!=4 or table!=8555304:row.update(available=False,reason='unsupported_shape')
            else:
                groups=[]
                for i in range(2):
                    context=car+0xb0+i*0x3c;raw=r.read(context,0x3c)
                    owner=struct.unpack_from('<I',raw,4)[0]
                    groups.append(dict(index=i,context=context,raw=raw.hex(),flags_byte2=raw[2],owner=owner,owner_matches=owner==car,
                      base_transform=matrix(struct.unpack_from('<I',raw,0x14)[0]),
                      wheels=[matrix(struct.unpack_from('<I',raw,0x18+j*4)[0]) for j in range(3)],context_stable=r.read(context,0x3c)==raw))
                row.update(available=True,groups=groups,identity_stable=r.u(car+0x50)==v['object_id'] and r.u(car+0x10)==shape and r.u(shape)==table and r.unpack(shape+8,'H')[0]==kind)
        except (OSError,ValueError) as e:row['error']=str(e)
        data['vehicles'].append(row)
    data['clock_after']=r.f(0x80acd4);data['sources']={}
    for name in ('read_live.py','read_physical_registry.py','read_wheel_animation.py','read_type4_wheels.py'):
        b=(root/name).read_bytes();(out/name).write_bytes(b);data['sources'][name]=hashlib.sha256(b).hexdigest()
    (out/'wheels.json').write_text(json.dumps(data,indent=2,allow_nan=False))
    good=[v for v in data['vehicles'] if v.get('available')];groups=[g for v in good for g in v['groups']]
    print(json.dumps(dict(clock=data['clock'],paused=data['paused'],supported=len(good),errors=[v for v in data['vehicles'] if 'error'in v],groups=len(groups),wheels=sum(m is not None for g in groups for m in g['wheels']),owners_match=all(g['owner_matches'] for g in groups),identities_stable=all(v['identity_stable'] for v in good))))
finally:K.CloseHandle(r.h)
