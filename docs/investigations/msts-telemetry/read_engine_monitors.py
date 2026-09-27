"""Read monitored engine subobjects without triggering safety actions."""
import argparse,datetime,hashlib,json,struct
from pathlib import Path
from read_live import K
from read_physical_registry import PhysicalRegistryReader
from read_wheel_animation import sample
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=PhysicalRegistryReader(a.pid)
mapping=[('AWSMonitor',0x4ba,0xb0c),('VigilanceMonitor',0x4fa,0xb78),('EmergencyStopMonitor',0x53a,0xbe4),('unnamed_slot3',0x57a,0xc50),('OverspeedMonitor',0x5ba,0xcbc)]
try:
    result=dict(pid=a.pid,sha256=r.sha,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),clock=r.f(0x80acd4),paused=r.u(0x7be0f4),engines=[])
    for car in sample(r)['vehicles'] or []:
        if not car.get('driver'):continue
        row=dict(object_id=car['object_id'],address=car['address'],train=car.get('train'),monitors=[])
        try:
            if not car['identity_stable'] or not car['driver']['definition_stable']:raise ValueError('Unstable engine source')
            ed=car['driver']['definition']
            for name,offset,definition_offset in mapping:
                addr=car['address']+offset;raw=r.read(addr,64);words=struct.unpack('<16I',raw);definition=words[15]
                m=dict(name=name,address=addr,definition=definition,raw=raw.hex(),words=list(words),available=False)
                if definition:
                    if definition!=ed+definition_offset:raise ValueError('Unexpected monitor definition link')
                    config=r.read(definition,0x6c)
                    m.update(available=True,definition_raw=config.hex(),enable_raw=words[0],active_action_raw=words[1],state8_raw=words[2],statec_raw=words[3],raw_scalar_bits={hex(o):raw[o:o+4].hex() for o in (0x10,0x14,0x18,0x1c)},definition_stable=r.read(definition,0x6c)==config)
                else:m['reason']='definition_null'
                m['state_stable']=r.read(addr,64)==raw;row['monitors'].append(m)
            row['identity_stable']=r.u(car['address']+0x50)==car['object_id'] and r.u(car['address']+0x29a)==ed
        except (OSError,ValueError) as e:row['error']=str(e)
        result['engines'].append(row)
    result['clock_after']=r.f(0x80acd4);result['sources']={}
    for name in ('read_live.py','read_physical_registry.py','read_wheel_animation.py','read_engine_monitors.py'):
        b=(root/name).read_bytes();(out/name).write_bytes(b);result['sources'][name]=hashlib.sha256(b).hexdigest()
    (out/'monitors.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(clock=result['clock'],paused=result['paused'],engines=[dict(id=e['object_id'],error=e.get('error'),monitors=[dict(name=m['name'],available=m['available'],enable=m.get('enable_raw'),action=m.get('active_action_raw')) for m in e['monitors']]) for e in result['engines']])))
finally:K.CloseHandle(r.h)
