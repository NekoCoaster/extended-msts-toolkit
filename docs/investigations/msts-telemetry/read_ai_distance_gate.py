"""Read-only inputs to native AI physicalization distance gate005a58af."""
import argparse,datetime,hashlib,json,math
from pathlib import Path
from read_services import ServiceReader
from read_live import K
from binary_fields import PE
p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
try:
    begin=r.f(0x80acd4);paused=r.u(0x7be0f4);view=r.u(0x7c2a88)
    if not view:raise ValueError('Null player view')
    v=list(r.unpack(view+0x38,'fff'));threshold=r.f(0x770718);rows=[]
    for s in r.registry()['entries']:
        if s['is_player']:continue
        endpoints=[list(r.unpack(s['address']+off,'fff')) for off in (0x94,0xfc)]
        sq=[sum((x-y)**2 for x,y in zip(point,v)) for point in endpoints]
        rows.append(dict(service=s['address'],service_id=s['service_id'],physicalized=s['physicalized_raw'],train=s['train'],endpoint_positions=endpoints,squared_distances=sq,distances=[math.sqrt(x) for x in sq],would_enter_distance_branch=any(x<threshold for x in sq),would_leave_distance_branch=all(x>threshold for x in sq),update_gate=s['update_candidate_words']['0x144']))
    result=dict(pid=a.pid,sha256=r.sha,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=begin,paused=paused,view=view,view_position38=v,threshold_squared=threshold,threshold_radius=math.sqrt(threshold),constant_disk_matches=PE().read(0x770718,4)==r.read(0x770718,4),services=rows,sim_time_after=r.f(0x80acd4),paused_after=r.u(0x7be0f4),view_pointer_stable=view==r.u(0x7c2a88),sources={},limitations='Read-only reconstruction,not native execution. Shared local coordinate frame and float rounding need care. Finite values only;NaN branch behavior unmodeled. Inactive/uninitialized service endpoints can be stale. Distance branch alone does not guarantee allocation or cleanup success. No threshold-crossing capture or origin-shift proof.')
    for n in ('read_ai_distance_gate.py','read_services.py','read_live.py','binary_fields.py'):
        data=(root/n).read_bytes();(out/n).write_bytes(data);result['sources'][n]=hashlib.sha256(data).hexdigest()
    (out/'gate.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8');print(json.dumps(result))
finally:K.CloseHandle(r.h)
