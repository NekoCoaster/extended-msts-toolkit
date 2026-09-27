"""Read-only comparison of native consist aggregates with connected car definitions."""
import argparse,json,hashlib,struct
from pathlib import Path
from read_services import ServiceReader,K
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
    try:
        start=r.f(0x80acd4);rows=[]
        for t in r.trains():
            mass=length=0.;cars=[]
            for c in t['cars']:
                definition=c['definition'];m=r.f(definition+0x444);l=r.f(definition+0x400)
                mass=f32(mass+m);length=f32(length+l)
                cars.append(dict(address=c['address'],definition=definition,type=r.read(definition+0x88,1)[0],definition_mass_candidate=m,definition_length_candidate=l,physics_mass=c['mass']))
            train=t['address'];stored_mass=r.f(train+0x9a);stored_length=r.f(train+0xaa)
            rows.append(dict(train=train,service=t['service_object'],cars=cars,stored_mass=stored_mass,stored_length=stored_length,reproduced_mass=mass,reproduced_length=length,mass_matches=mass==stored_mass,length_matches=length==stored_length,physics_mass_sum=sum(c['physics_mass'] for c in cars if c['physics_mass'] is not None),class_bits=r.u(t['service_object'])&6,last_car=r.u(train+0x66),last_car_matches=r.u(train+0x66)==cars[-1]['address']))
        result=dict(pid=a.pid,sha256=r.sha,sim_time=start,sim_time_after=r.f(0x80acd4),paused=r.u(0x7be0f4),trains=rows)
        (out/'snapshot.json').write_text(json.dumps(result,indent=2,allow_nan=False));hashes={}
        for name in ['probe_consist_totals.py','read_services.py','read_live.py']:
            data=(root/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
        (out/'sources.json').write_text(json.dumps(hashes,indent=2))
        print(json.dumps(dict(same_sim_time=start==result['sim_time_after'],trains=[{k:v for k,v in t.items() if k!='cars'} for t in rows])))
    finally:K.CloseHandle(r.h)
