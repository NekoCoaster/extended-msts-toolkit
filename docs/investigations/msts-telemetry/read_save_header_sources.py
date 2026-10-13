"""Read selected live session strings/scalars referenced by save-header writer."""
import argparse,datetime,hashlib,json,shutil
from pathlib import Path
from read_services import ServiceReader
from read_live import K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
try:
    route=r.u(0x7b8d3c);activity=r.u(0x7b8d40);strings=[]
    for kind,obj,offsets in [('route',route,[4,0x14]),('activity',activity,[4,8,0xc,0x1c])]:
        if not obj:continue
        for off in offsets:
            pointer=r.u(obj+off)
            value=r.wide(pointer,4096) if pointer else None
            strings.append(dict(kind=kind,offset=hex(off),pointer=pointer,value=value,stable_pointer=r.u(obj+off)==pointer))
    result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),image_sha256=r.sha,route=route,activity=activity,
        strings=strings,activity_word0=r.u(activity) if activity else None,activity_mode28=r.u(activity+0x28) if activity else None,
        origin=list(r.unpack(0x79d118,'2i')),dayclock=r.f(0x80acd4),paused=r.u(0x7be0f4),
        stable_roots=r.u(0x7b8d3c)==route and r.u(0x7b8d40)==activity,
        limitations='Runtime root branch sampled,not editor fallback809814 or a newly saved file. Strings bounded;pointer rereads not atomic contents. Loaded labels do not verify asset files.')
    (out/'sources.json').write_text(json.dumps(result,indent=2));hashes={}
    for name in ['read_save_header_sources.py','read_services.py','read_live.py']:
        shutil.copy2(root/name,out/name);hashes[name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
    (out/'probe-hashes.json').write_text(json.dumps(hashes,indent=2));print(json.dumps(result,indent=2))
finally:K.CloseHandle(r.h)
