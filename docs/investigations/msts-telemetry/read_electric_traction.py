"""Read-only electric producer inputs and stored outputs; no native calls.

traction_gate is only sampled lead296 bit2. Live evidence shows it can be set
with stale cached throttle; do not use it as a freshness or supply guarantee.
"""
import argparse,json,shutil
from pathlib import Path
from read_live import Reader,K

def capture(r):
    time=r.f(0x80acd4);train=r.u(0x7c2ac0)
    if r.u(0x7b6438)!=3:raise ValueError('Electric player required')
    wrapper=r.u(train+0x72)
    if r.u(wrapper)!=3:raise ValueError('Electric controller required')
    controller=r.u(wrapper+8);lead=r.u(train+0x6a);definition=r.u(lead+0x29a)
    engine_type=r.read(definition+0x88,1)[0]
    if engine_type!=2:raise ValueError('Electric engine definition required')
    fields={}
    for base,ptr,offsets in [('lead',lead,[0x1bc,0x230,0x29e,0x2a2,0x2c2,0x492,0x496]),('controller',controller,[0x8c,0xc8]),('definition',definition,[0xfe,0x102,0x106,0x13e,0x1da,0x63c,0x640])]:
        for off in offsets:fields[f'{base}_{off:x}']=r.f(ptr+off)
    flags=r.u(lead+0x296)
    return dict(time=time,time_after=r.f(0x80acd4),paused=r.u(0x7be0f4),train=train,lead=lead,controller=controller,definition=definition,engine_type=engine_type,flags296=flags,traction_gate=bool(flags&2),modifier_enabled=r.u(controller+0x394),fields=fields,stable=r.u(0x7c2ac0)==train and r.u(train+0x6a)==lead and r.u(train+0x72)==wrapper and r.u(wrapper+8)==controller and r.u(lead+0x29a)==definition and r.u(0x7b6438)==3,limitations='Non-atomic source reads. Stored lead492/496 can be stale when gate is false. No force/power units or delivered wheel force inferred by this probe.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Invalid capture name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        d=dict(image_sha256=r.sha,snapshot=capture(r));(out/'traction.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
        for name in ('read_electric_traction.py','read_live.py'):shutil.copy2(root/name,out/name)
        print(json.dumps(d))
    finally:K.CloseHandle(r.h)
