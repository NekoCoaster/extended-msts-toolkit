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
 population=sample(r)
 report['population_available']=population['available'];report['manager_stable']=population.get('manager_stable',False)
 for v in population['vehicles'] or []:
  row=dict(object_id=v['object_id'],car=v['address'],train=v.get('train'));report['vehicles'].append(row)
  try:
   if 'error'in v or not v['identity_stable']:raise ValueError('Unstable source')
   car=v['address'];body=r.u(car+0x5c);definition=r.u(car+0x94);owner=r.u(car+0x98)
   if not body or r.read(body+0xf0,1)!=b'\x01' or r.u(body+0x11d)!=car:raise ValueError('Body identity mismatch')
   raw=r.read(body+0xa0,24);velocity=r.read(body+0x88,12);coeff=r.read(definition+0x478,40);declaration=r.u(definition+0x8c)
   values=struct.unpack('<6f',raw);vel=struct.unpack('<3f',velocity);cf=struct.unpack('<10f',coeff)
   if not all(math.isfinite(x) for x in values+vel+cf):raise ValueError('Nonfinite field')
   row.update(body=body,definition=definition,force=values[:3],torque=values[3:],velocity=vel,coefficients=cf[:5],friction_coefficients=cf,friction_raw=coeff.hex(),declaration_flags=declaration,owner=owner,raw=raw.hex(),state_stable=r.read(body+0xa0,24)==raw and r.read(body+0x88,12)==velocity,definition_stable=r.read(definition+0x478,40)==coeff and r.u(definition+0x8c)==declaration,identity_stable=r.u(car+0x50)==v['object_id'] and r.u(car+0x5c)==body and r.u(car+0x94)==definition and r.u(car+0x98)==owner and r.u(body+0x11d)==car)
  except (ValueError,OSError) as e:row['error']=str(e)
 report['day_after']=r.f(0x80acd4)
 report['comparison_guards_pass']=bool(report['population_available'] and report['manager_stable'] and report['day']==report['day_after'] and all('error' not in v and v['identity_stable'] and v['state_stable'] and v['definition_stable'] for v in report['vehicles']))
 report['limitations']='Ten loaded Friction scalars, not ten known physical quantities. Retained five-element coefficients key is the first half. Rereads and same-clock guards do not make sequential observations atomic; no force reconstruction or parser execution claim.'
 for n in ('read_body_accumulators.py','read_live.py','read_physical_registry.py','read_wheel_animation.py'):
  b=(root/n).read_bytes();(out/n).write_bytes(b);report['sources'][n]=hashlib.sha256(b).hexdigest()
 (out/'accumulators.json').write_text(json.dumps(report,indent=2,allow_nan=False))
 print(json.dumps(dict(day=report['day'],paused=report['paused'],vehicles=len(report['vehicles']),errors=[x for x in report['vehicles'] if 'error'in x])))
finally:K.CloseHandle(r.h)
