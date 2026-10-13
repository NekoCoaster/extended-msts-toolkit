"""Bounded read-only observations of one session-local AI path iterator."""
import argparse
import datetime
import hashlib
import json
import shutil
import time
from pathlib import Path
from read_live import Reader, K

def sample(r, address, identity):
    if r.u(address+0x40) != identity:
        raise ValueError('Service identity changed')
    iterator = r.u(address+0x1d4)
    path = r.u(iterator)
    base, count = r.unpack(path+0x10, '2I')
    if count > 4096 or not base:
        raise ValueError('Invalid path bounds')
    cursor, event = r.u(iterator+0x2c), r.u(iterator+0x24)
    def index(pointer):
        if not pointer:
            return None
        offset = pointer-base
        if offset < 0 or offset % 0x24 or offset//0x24 >= count:
            raise ValueError('Node outside loaded array')
        return offset//0x24
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  time=r.f(0x80acd4), step=r.f(0x828fb4), paused=r.u(0x7be0f4),
                  service=address, identity=identity, iterator=iterator, path=path,
                  cursor_index=index(cursor), event_index=index(event),
                  iterator_type=r.u(iterator+0xc), speed=r.f(address+0x138),
                  target=r.f(address+0x13c), progress=r.f(address+0x1d0),
                  flags={hex(o):r.u(address+o) for o in (0x1dc,0x1e4,0x1e8,0x214)},
                  timers={hex(o):r.f(address+o) for o in (0x1ec,0x1f0,0x210)})
    result['roots_stable'] = (r.u(address+0x40)==identity and r.u(address+0x1d4)==iterator and r.u(iterator)==path)
    result['cursor_stable'] = cursor==r.u(iterator+0x2c) and event==r.u(iterator+0x24)
    # 005a7e9c selects the inline movement endpoint from the speed sign bit.
    endpoint = address + (0xb4 if r.u(address+0x138) & 0x80000000 else 0x4c)
    result['movement_endpoint'] = dict(address=endpoint,track=r.u(endpoint),
                                       direction=r.u(endpoint+0xc),position=r.f(endpoint+0x10))
    result['retained_segment'] = dict(track=r.u(iterator+0x10),direction=r.u(iterator+0x14),
                                     start=r.f(iterator+0x18),end=r.f(iterator+0x1c))
    return result

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--pid',type=int,required=True)
    parser.add_argument('--service',type=lambda x:int(x,0),required=True)
    parser.add_argument('--identity',type=int,required=True)
    parser.add_argument('--name',required=True)
    parser.add_argument('--seconds',type=float,default=180)
    args=parser.parse_args()
    if Path(args.name).name!=args.name or args.name in ('.','..') or not 0<args.seconds<=600:
        parser.error('Invalid name/duration')
    root=Path(__file__).resolve().parent;out=root/'captures'/args.name;out.mkdir(exist_ok=False)
    r=Reader(args.pid)
    try:
        sources={}
        for name in ('read_path_wait_series.py','read_live.py'):
            shutil.copy2(root/name,out/name);sources[name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
        (out/'metadata.json').write_text(json.dumps(dict(arguments=vars(args),sources=sources,sha256=r.sha,limits='Sequential external reads;brief transitions can be missed;session-local service identity may be reused.'),indent=2),encoding='utf-8')
        start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
            while True:
                try:row=sample(r,args.service,args.identity)
                except (OSError,ValueError) as exc:row=dict(error=str(exc));errors+=1
                row['wall_elapsed']=time.perf_counter()-start
                f.write(json.dumps(row,allow_nan=False)+'\n');f.flush();count+=1
                if row['wall_elapsed']>=args.seconds or (out/'stop.request').exists():break
                time.sleep(.02)
        report=dict(samples=count,errors=errors,wall_elapsed=time.perf_counter()-start)
        (out/'completion.json').write_text(json.dumps(report),encoding='utf-8');print(json.dumps(report))
    finally:K.CloseHandle(r.h)
