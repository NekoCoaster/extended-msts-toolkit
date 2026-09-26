"""Guarded electric player raw cab sources, without native calls or writes."""
import json,argparse,shutil
from pathlib import Path
from read_live import Reader,K
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid capture name')
out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
    kind=r.u(0x7b6438);d=dict(image_sha256=r.sha,kind=kind,time=r.f(0x80acd4),paused=r.u(0x7be0f4),available=kind==3)
    if kind==3:
        train=r.u(0x7c2ac0);wrapper=r.u(train+0x72);controller=r.u(wrapper+8);lead=r.u(train+0x6a)
        if not controller or not lead:raise ValueError('Missing electric context')
        bases=dict(controller=controller,lead=lead);values={}
        for f in json.loads((root/'electric-cab-fields.json').read_text(encoding='utf-8')):
            address=bases[f['base']]+f['offset'];values[f['channel']]=dict(address=address,raw=r.f(address) if f['type']=='float' else r.u(address))
        d.update(train=train,lead=lead,controller=controller,train_speed=r.f(train+0x92),route_voltage_raw=r.f(r.u(0x7b8d3c)+0x58),voltage_gate_enabled=r.u(controller+0x258),values=values,stable=r.u(0x7b6438)==kind and r.u(0x7c2ac0)==train and r.u(train+0x6a)==lead and r.u(wrapper+8)==controller)
    else:d['reason']='Non-electric player; no electric-specific offsets read'
    (out/'electric.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
    for n in ('read_electric_cab.py','read_live.py','electric-cab-fields.json'):shutil.copy2(root/n,out/n)
    print(json.dumps(d))
finally:K.CloseHandle(r.h)
