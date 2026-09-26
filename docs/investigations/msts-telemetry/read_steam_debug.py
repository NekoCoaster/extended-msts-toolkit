"""Read mapped steam debug fields, gated on the current steam player context."""
import argparse,json,shutil
from pathlib import Path
from read_live import Reader,K
from read_steam_cab import capture
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid capture name')
out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
    start=capture(r)
    if not start['available']:raise ValueError('Not a steam player context')
    values={}
    for field in json.loads((root/'steam-debug-fields.json').read_text(encoding='utf-8')):
        address=start[field['base']]+field['offset']
        raw=r.u(address) if field['mask'] is not None else r.f(address)
        values[field['name']]=dict(address=address,raw=raw,value=bool(raw & field['mask']) if field['mask'] is not None else raw)
    values['train_update_accumulator']=dict(raw=r.f(start['train']+0x8a))
    values['train_update_interval']=dict(raw=r.f(start['train']+0x8e))
    values['injector1_working_raw']=dict(raw=r.u(start['lead']+0x2ee))
    values['injector2_working_raw']=dict(raw=r.u(start['lead']+0x2f2))
    end=capture(r)
    result=dict(image_sha256=r.sha,start=start,end=end,values=values,context_stable=all(start[k]==end[k] for k in ('train','lead','controller','engine_definition','player_control_type')),limitations='Non-atomic external read; labels identify consumers, not update laws or all units.')
    (out/'steam-debug.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    for name in ('read_steam_debug.py','read_steam_cab.py','read_live.py','steam-debug-fields.json','steam-cab-fields.json'):shutil.copy2(root/name,out/name)
    print(json.dumps(dict(time=start['sim_time'],paused=start['paused'],stable=result['context_stable'],values=values)))
finally:K.CloseHandle(r.h)
