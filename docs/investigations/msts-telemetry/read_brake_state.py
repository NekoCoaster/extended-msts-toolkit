"""Read-only, offset-labelled brake state; no UI or memory writes."""
import argparse, datetime, json, struct
from pathlib import Path
from read_live import Reader, K
from binary_fields import PE

def sample(r):
    trains=[]
    for t in r.trains():
        cars=[]
        for c in t['cars']:
            a=c['address']; d=c['definition']
            cars.append(dict(address=a,powered=c['powered'],floats={hex(o):r.f(a+o) for o in (0x198,0x19c,0x22c,0x230,0x234,0x238,0x268)},integers={hex(o):r.u(a+o) for o in (0x26c,0x270)},definition_integers={hex(o):r.u(d+o) for o in (0x910,0x914)},definition_floats={hex(o):r.f(d+o) for o in (0x918,0x91c,0x954)},owner_stable=r.u(a+0x98)==t['address']))
        trains.append(dict(address=t['address'],lead=t['lead'],is_player=t['is_player'],cars=cars))
    return trains

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        pe=PE(r.path);result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),trains=sample(r),shared_timers={hex(o):r.f(o) for o in (0x80a1ec,0x80a1f0)},constants={hex(o):dict(disk=struct.unpack('<f',pe.read(o,4))[0],live=r.f(o)) for o in (0x753c38,0x758b84,0x752d0c)})
        result['sim_time_after']=r.f(0x80acd4)
        for f in ('read_brake_state.py','read_live.py','binary_fields.py'):(out/f).write_bytes((root/f).read_bytes())
        (out/'brakes.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
    finally:K.CloseHandle(r.h)
