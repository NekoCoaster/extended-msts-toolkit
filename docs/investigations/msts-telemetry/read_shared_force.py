"""Read shared-force branch predicates, preserving raw tested-build offsets."""
import argparse,json,struct,shutil
from pathlib import Path
from read_live import Reader,K
from binary_fields import PE
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args();root=Path(__file__).resolve().parent
if Path(a.name).name!=a.name:raise ValueError('Invalid capture name')
out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
 pe=PE(r.path);rows=[]
 for t in r.trains():
  cars=[]
  for c in t['cars']:
   if not c['powered']:continue
   base=c['address'];d=c['engine_definition'];flags=r.u(d+0x94);raw=r.f(base+0x102)
   cars.append(dict(address=base,engine_definition=d,engine_type=r.read(d+0x88,1)[0],definition_flags94=flags,definition_flags8c=r.u(d+0x8c),car102_raw_bits=hex(r.u(base+0x102)),car102_as_float=raw,ramp_predicate=bool(flags&0x200) and raw>0,definition_floats={hex(o):r.f(d+o) for o in (0xfe,0x102,0x10a,0x10e)},force=r.f(base+0x29e),power=r.f(base+0x2a2),flags296=r.u(base+0x296)))
  rows.append(dict(address=t['address'],is_player=t['is_player'],lead=t['lead'],speed=t['speed_raw'],cars=cars))
 constants={hex(o):dict(disk=struct.unpack('<f',pe.read(o,4))[0],live=r.f(o)) for o in (0x406031,0x753fb0,0x753d4c)}
 result=dict(sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),trains=rows,constants=constants,limitations='Predicate reconstructed for ordinary finite inputs, not x87 NaN behavior. car102 is the actual helper read, not engine-definition102; its semantic identity unresolved. Paused zero-output sample cannot validate nonzero ramp behavior.')
 (out/'shared-force.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 for f in ('read_shared_force.py','read_live.py','binary_fields.py'):shutil.copy2(root/f,out/f)
 print(json.dumps(result))
finally:K.CloseHandle(r.h)
