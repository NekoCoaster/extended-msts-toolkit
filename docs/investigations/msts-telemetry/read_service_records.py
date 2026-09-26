"""Bounded service record list; raw fields avoid unverified timetable labels."""
import argparse,json,shutil
from pathlib import Path
from read_services import ServiceReader
from read_live import K
p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
try:
    result=dict(sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),services=[])
    for s in r.registry()['entries']:
        addr=s['address'];sentinel=r.u(addr+0x30);n=r.u(sentinel);seen=set();records=[]
        while n!=sentinel:
            if not n or n in seen or len(seen)>=256:raise ValueError('Invalid/bounded service record list')
            seen.add(n);record=r.u(n+8)
            records.append(dict(node=n,address=record,track_item_id=r.u(record),distance_candidate=r.f(record+0x14),efficiency_override=r.f(record+0x24),raw_words=[r.u(record+i) for i in range(0,0x28,4)]));n=r.u(n)
        result['services'].append(dict(address=addr,id=s.get('service_id'),sentinel=sentinel,selected=r.u(addr+0x34),previous=r.u(addr+0x38),progress_candidate=r.f(addr+0x1d0),length_candidate=r.f(addr+0x124),records=records,sentinel_stable=r.u(addr+0x30)==sentinel))
    result['sim_time_after']=r.f(0x80acd4)
    result['limitations']='Sequential structural read only. Empty lists do not validate populated records or selector arithmetic. Raw words and provisional offsets are not confirmed schedule timestamps.'
    for f in ('read_service_records.py','read_services.py','read_live.py'):shutil.copy2(root/f,out/f)
    (out/'records.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
finally:K.CloseHandle(r.h)
