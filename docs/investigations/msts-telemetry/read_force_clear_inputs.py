"""Read-only inputs for inspected force-clear branches; never invokes native code."""
import argparse,json,hashlib,struct,datetime
from pathlib import Path
from read_live import K
from read_physical_registry import PhysicalRegistryReader
from read_wheel_animation import sample
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=PhysicalRegistryReader(a.pid)
try:
 report=dict(pid=a.pid,sha256=r.sha,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),clock=r.f(0x80acd4),paused=r.u(0x7be0f4),zero_vector_raw=r.read(0x83db48,12).hex(),vehicles=[],sources={})
 base=sample(r);report['population_available']=base['available'];report['manager_stable']=base.get('manager_stable',False)
 for v in base.get('vehicles') or []:
  row=dict(car=v['address'],object_id=v['object_id'],train=v.get('train'));report['vehicles'].append(row)
  try:
   if 'error' in v or not v['identity_stable']:raise ValueError('Unstable population input')
   car=v['address'];body=r.u(car+0x5c);owner=r.u(car+0x98);flags=r.u(car+0x84)
   if not body or r.read(body+0xf0,1)!=b'\x01' or r.u(body+0x11d)!=car:raise ValueError('Body guard')
   bf=r.u(body+4);state=r.unpack(body+0xf2,'B')[0]
   owner_mode=r.unpack(owner+0x5a,'B')[0] if owner else None;service=r.u(car+0x1f8)
   row.update(owner_mode=owner_mode,service=service)
   row.update(body=body,owner=owner,car_flags=flags,body_flags=bf,state_flags=state,entry_gate=(flags&2)==0 or (bf&2)!=0,clear_condition=bool(state&8) and (bool(flags&8) or owner==0),force_raw=r.read(body+0xa0,12).hex(),torque_raw=r.read(body+0xac,12).hex(),velocity_raw=r.read(body+0x88,12).hex())
   row['guards_pass']=r.u(car+0x50)==v['object_id'] and r.u(car+0x5c)==body and r.u(car+0x98)==owner and r.u(car+0x84)==flags and r.u(body+0x11d)==car and r.u(body+4)==bf and r.unpack(body+0xf2,'B')[0]==state and r.u(car+0x1f8)==service and (not owner or r.unpack(owner+0x5a,'B')[0]==owner_mode)
  except (OSError,ValueError) as e:row['error']=str(e)
 report['clock_after']=r.f(0x80acd4)
 report['limitation']='Branch predicates only,not invocation or causal zero proof. Sequential inputs can cross solver phases;values do not have state rereads. Historical captures cannot inherit these flags.'
 for name in ['read_force_clear_inputs.py','read_live.py','read_physical_registry.py','read_wheel_animation.py']:
  raw=(root/name).read_bytes();(out/name).write_bytes(raw);report['sources'][name]=hashlib.sha256(raw).hexdigest()
 (out/'inputs.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(clock=report['clock'],clock_after=report['clock_after'],zero_vector=report['zero_vector_raw'],vehicles=len(report['vehicles']),errors=sum('error'in x for x in report['vehicles']),guard_failures=sum(not x.get('guards_pass',False) for x in report['vehicles']),eligible=sum(x.get('entry_gate',False) and x.get('clear_condition',False) for x in report['vehicles']))))
finally:K.CloseHandle(r.h)
