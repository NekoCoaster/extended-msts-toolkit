"""Read baseline/selected-record efficiency sources without modifying the game."""
import argparse,json,shutil,struct
from pathlib import Path
from read_services import ServiceReader
from read_live import K
from binary_fields import PE
p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid);pe=PE()
try:
    result=dict(sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),services=[],constants=[])
    for address in (0x4069d2,0x758434,0x753c38):
        raw=pe.read(address,4);result['constants'].append(dict(address=hex(address),value=struct.unpack('<f',raw)[0],disk_live_equal=r.read(address,4)==raw))
    for s in r.registry()['entries']:
        addr=s['address'];selected=r.u(addr+0x34)
        result['services'].append(dict(address=addr,id=s.get('service_id'),baseline=r.f(addr+0x204),effective=r.f(addr+0x208),selected_record=selected,selected_value=r.f(selected+0x24) if selected else None,selected_stable=r.u(addr+0x34)==selected,start_speed_candidate=r.f(addr+0x28),configured_cap=r.f(addr+0x1f8)))
    result['sim_time_after']=r.f(0x80acd4)
    result['limitations']='Paused source consistency only; baseline parser binding and selected-record identity untraced. No changed-efficiency transition or clamp boundary experiment.'
    for f in ('read_service_efficiency.py','read_services.py','read_live.py','binary_fields.py'):shutil.copy2(root/f,out/f)
    (out/'efficiency.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
finally:K.CloseHandle(r.h)
