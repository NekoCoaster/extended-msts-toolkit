"""Read guarded body force/torque accumulators and resistance inputs; no reconstruction claim."""
import argparse,hashlib,json,math,struct
from pathlib import Path
from read_live import K
from read_physical_registry import PhysicalRegistryReader
from read_wheel_animation import sample
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=PhysicalRegistryReader(a.pid)
try:
 report=dict(pid=a.pid,sha256=r.sha,day=r.f(0x80acd4),paused=r.u(0x7be0f4),vehicles=[],sources={})
 for v in sample(r)['vehicles'] or []:
  row=dict(object_id=v['object_id'],car=v['address'],train=v.get('train'));report['vehicles'].append(row)
  try:
   if 'error'in v or not v['identity_stable']:raise ValueError('Unstable source')
   car=v['address'];body=r.u(car+0x5c);definition=r.u(car+0x94)
   if not body or r.read(body+0xf0,1)!=b'\x01' or r.u(body+0x11d)!=car:raise ValueError('Body identity mismatch')
   raw=r.read(body+0xa0,24);velocity=r.read(body+0x88,12);coeff=r.read(definition+0x478,20)
   values=struct.unpack('<6f',raw);vel=struct.unpack('<3f',velocity);cf=struct.unpack('<5f',coeff)
   if not all(math.isfinite(x) for x in values+vel+cf):raise ValueError('Nonfinite field')
   row.update(body=body,definition=definition,force=values[:3],torque=values[3:],velocity=vel,coefficients=cf,raw=raw.hex(),state_stable=r.read(body+0xa0,24)==raw and r.read(body+0x88,12)==velocity,definition_stable=r.read(definition+0x478,20)==coeff,identity_stable=r.u(car+0x50)==v['object_id'] and r.u(car+0x5c)==body and r.u(car+0x94)==definition and r.u(body+0x11d)==car)
  except (ValueError,OSError) as e:row['error']=str(e)
 report['day_after']=r.f(0x80acd4)
 for n in ('read_body_accumulators.py','read_live.py','read_physical_registry.py','read_wheel_animation.py'):
  b=(root/n).read_bytes();(out/n).write_bytes(b);report['sources'][n]=hashlib.sha256(b).hexdigest()
 (out/'accumulators.json').write_text(json.dumps(report,indent=2,allow_nan=False))
 print(json.dumps(dict(day=report['day'],paused=report['paused'],vehicles=len(report['vehicles']),errors=[x for x in report['vehicles'] if 'error'in x])))
finally:K.CloseHandle(r.h)
