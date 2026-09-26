"""Resolve electric event receiver handles without calling any receiver."""
import argparse,json,shutil
from pathlib import Path
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid capture name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
    if r.u(0x7b6438)!=3:raise ValueError('Electric player required')
    time=r.f(0x80acd4);train=r.u(0x7c2ac0);lead=r.u(train+0x6a);table=r.u(0x828108);rows=[]
    for off in [0x4b6,0x25c]:
        handle=r.u(lead+off);row=dict(source_offset=hex(off),handle=handle);rows.append(row)
        if not 0<handle<1000000:row['unavailable']='Handle outside research bound';continue
        obj=r.u(table+handle*8);row['object']=obj
        if not obj:continue
        class_id=r.u(obj);row['class_handle']=class_id
        row['event_masks']=[r.u(obj+0x20),r.u(obj+0x24)]
        row['scalar_values']=[r.f(obj+0x28),r.f(obj+0x2c),r.f(obj+0x30)]
        if not 0<class_id<1000000:row['unavailable']='Class handle outside research bound';continue
        cls=r.u(table+class_id*8);row['class_object']=cls
        if not cls:continue
        row['methods']=[]
        for slot in [0x82,0x83,0x85]:
            index=r.u(cls+0x64+slot*4)
            method=dict(slot=slot,index=index);row['methods'].append(method)
            if index>=4096:method['unavailable']='Method index outside research bound';continue
            method['address']=r.u(cls+0x1064+index*4)
    d=dict(image_sha256=r.sha,time=time,time_after=r.f(0x80acd4),paused=r.u(0x7be0f4),train=train,lead=lead,registry=table,receivers=rows,stable=r.u(0x7c2ac0)==train and r.u(train+0x6a)==lead and r.u(0x828108)==table,limitations='Read-only routing snapshot, not an event log. Registry bounds are conservative probe bounds, not native capacities. No receiver executed.')
    (out/'event-routes.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
    for n in ['read_electric_event_routes.py','read_live.py']:shutil.copy2(root/n,out/n)
    print(json.dumps(d))
finally:K.CloseHandle(r.h)
