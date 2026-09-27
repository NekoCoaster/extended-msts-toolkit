"""Read loaded layer geometry/timing with bounded edge-array traversal."""
import argparse,datetime,hashlib,json,struct
from pathlib import Path
from read_live import Reader,K

p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
    e=r.u(0x7b6d60);s=r.u(e);count=r.u(s);base=r.u(s+8)
    if count>32:raise ValueError('Layer bound')
    result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),environment=e,sky=s,layers=[])
    for i in range(count):
        address=base+i*0x1ac;raw=r.read(address,0x24)
        faces,radius,height,n,ptr,fi0,fi1,fo0,fo1=struct.unpack('<IffIIffff',raw)
        if n>256:raise ValueError('Edge bound')
        edges=[dict(index=j,address=ptr+j*8,height=r.f(ptr+j*8),radius=r.f(ptr+j*8+4)) for j in range(n)]
        result['layers'].append(dict(index=i,address=address,raw_header=raw.hex(),top_faces=faces,top_radius=radius,top_height=height,
            edge_count=n,edge_array=ptr,fadein_start=fi0,fadein_end=fi1,fadeout_start=fo0,fadeout_end=fo1,edges=edges,
            header_stable=raw==r.read(address,0x24)))
    result.update(structure_stable=e==r.u(0x7b6d60) and s==r.u(e) and count==r.u(s) and base==r.u(s+8),
                  sim_time_after=r.f(0x80acd4),paused_after=r.u(0x7be0f4),sources={})
    for name in ('read_sky_layers.py','read_live.py'):
        b=(root/name).read_bytes();(out/name).write_bytes(b);result['sources'][name]=hashlib.sha256(b).hexdigest()
    (out/'layers.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
finally:K.CloseHandle(r.h)
