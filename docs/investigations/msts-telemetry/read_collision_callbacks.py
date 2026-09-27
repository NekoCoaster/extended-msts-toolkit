"""Guarded read-only physical vehicle callback/state snapshot."""
import argparse,json,hashlib,struct
from pathlib import Path
from read_live import K
from read_physical_registry import PhysicalRegistryReader
from read_wheel_animation import sample
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args();root=Path(__file__).resolve().parent;out=root/'captures'/'collision-callback-paused-01';out.mkdir(exist_ok=False);r=PhysicalRegistryReader(a.pid)
try:
 rows=[]
 for v in sample(r)['vehicles']:
  car=v['address'];row=dict(car=car,object_id=v['object_id'],train=v.get('train'));rows.append(row)
  try:
   if 'error'in v or not v['identity_stable']:raise ValueError('Unstable source')
   raw=r.read(car+0x74,8);cb,state=struct.unpack('<2I',raw);row.update(callback=hex(cb),state=state,raw=raw.hex(),stable=r.read(car+0x74,8)==raw and r.u(car+0x50)==v['object_id'])
  except (ValueError,OSError) as e:row['error']=str(e)
 result=dict(pid=a.pid,sha256=r.sha,day=r.f(0x80acd4),paused=r.u(0x7be0f4),vehicles=rows,sources={})
 for n in ['read_collision_callbacks.py','read_live.py','read_physical_registry.py','read_wheel_animation.py']:
  b=(root/n).read_bytes();(out/n).write_bytes(b);result['sources'][n]=hashlib.sha256(b).hexdigest()
 (out/'callbacks.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(vehicles=len(rows),values=sorted(set((x.get('callback'),x.get('state')) for x in rows)),errors=[x for x in rows if 'error'in x or not x.get('stable')],day=result['day'],paused=result['paused'])))
finally:K.CloseHandle(r.h)
