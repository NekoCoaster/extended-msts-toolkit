"""Bounded external read of loaded sky arrays; raw records are not decoded claims."""
import argparse,datetime,hashlib,json
from pathlib import Path
from read_live import Reader,K

p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid capture name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
    result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4))
    environment=r.u(0x7b6d60);sky=r.u(environment)
    if not sky:raise ValueError('No loaded sky')
    layers,split,layer_array=r.unpack(sky,'IiI');satellites,satellite_array=r.unpack(sky+0x180,'II')
    if layers>32 or satellites>32:raise ValueError('Conservative sky array bound exceeded')
    result.update(environment=environment,sky=sky,layer_count=layers,layer_split=split,layer_array=layer_array,
                  satellite_count=satellites,satellite_array=satellite_array,
                  layers=[dict(index=i,address=layer_array+i*0x1ac,raw_hex=r.read(layer_array+i*0x1ac,0x1ac).hex()) for i in range(layers)],
                  satellites=[dict(index=i,address=satellite_array+i*0x1cd,raw_hex=r.read(satellite_array+i*0x1cd,0x1cd).hex()) for i in range(satellites)])
    result['structure_stable']=(environment==r.u(0x7b6d60) and sky==r.u(environment) and
        (layers,split,layer_array)==r.unpack(sky,'IiI') and (satellites,satellite_array)==r.unpack(sky+0x180,'II'))
    result.update(sim_time_after=r.f(0x80acd4),paused_after=r.u(0x7be0f4),sources={})
    for name in ('read_sky_structure.py','read_live.py'):
        b=(root/name).read_bytes();(out/name).write_bytes(b);result['sources'][name]=hashlib.sha256(b).hexdigest()
    (out/'sky.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('layers','satellites')},indent=2))
finally:K.CloseHandle(r.h)
