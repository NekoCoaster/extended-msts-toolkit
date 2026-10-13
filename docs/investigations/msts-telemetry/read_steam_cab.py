"""Exact-image steam-only raw cab sources; no native calls or game writes."""
import argparse,json,shutil
from pathlib import Path
from read_live import Reader,K
ROOT=Path(__file__).resolve().parent

def capture(r):
    start=r.f(0x80acd4);kind=r.u(0x7b6438)
    header=dict(sim_time=start,player_control_type=kind,paused=r.u(0x7be0f4))
    if kind!=1:return dict(**header,available=False,reason='Player control type is not steam; no steam controller/lead offsets read')
    train=r.u(0x7c2ac0);wrapper=r.u(train+0x72);controller=r.u(wrapper+8);lead=r.u(train+0x6a)
    if not controller or not lead:raise ValueError('Steam player context missing')
    engine_definition=r.u(lead+0x29a);bases=dict(controller=controller,lead=lead);values={}
    for field in json.loads((ROOT/'steam-cab-fields.json').read_text(encoding='utf-8')):
        address=bases[field['base']]+field['offset'];values[field['channel']]=dict(raw=r.f(address) if field['type']=='float' else r.u(address),address=address,display=field['display'])
    firebox=dict(input_2c2=r.f(lead+0x2c2),input_2ca=r.f(lead+0x2ca),definition_242=r.f(engine_definition+0x242),definition_222=r.f(engine_definition+0x222))
    stable=r.u(0x7b6438)==kind and r.u(0x7c2ac0)==train and r.u(train+0x6a)==lead and r.u(wrapper+8)==controller
    return dict(**header,available=True,train=train,controller=controller,lead=lead,engine_definition=engine_definition,train_speed=r.f(train+0x92),values=values,firebox_inputs=firebox,context_stable=stable,sim_time_after=r.f(0x80acd4),limitations='Native cab sources; source-specific runtime validation recorded separately; not independent AI controls')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Name must be one component')
    out=ROOT/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        d=dict(image_sha256=r.sha,snapshot=capture(r));(out/'steam.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
        for n in ('read_steam_cab.py','steam-cab-fields.json','read_live.py'):shutil.copy2(ROOT/n,out/n)
        print(json.dumps(d))
    finally:K.CloseHandle(r.h)
