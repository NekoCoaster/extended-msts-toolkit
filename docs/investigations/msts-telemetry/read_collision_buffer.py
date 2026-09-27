"""Read bounded collision work-buffer entries; no persistent contact/event claim."""
import argparse,hashlib,json,struct
from pathlib import Path
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
 header=r.read(0x80a76c,12);base,count,capacity=struct.unpack('<3I',header)
 if count>capacity or capacity>100000:raise ValueError('Invalid count/capacity')
 if count and not base:raise ValueError('Null populated buffer')
 limit=min(count,128);raw=r.read(base,limit*0x62) if limit else b'';rows=[]
 for i in range(limit):
  b=raw[i*0x62:(i+1)*0x62];rows.append(dict(index=i,objects=struct.unpack_from('<2I',b,4),bodies=struct.unpack_from('<2I',b,12),callbacks=struct.unpack_from('<2I',b,20),point_raw=struct.unpack_from('<3f',b,32),raw=b.hex()))
 report=dict(pid=a.pid,sha256=r.sha,day=r.f(0x80acd4),paused=r.u(0x7be0f4),base=base,count=count,capacity=capacity,read_count=limit,truncated=count>limit,header_stable=r.read(0x80a76c,12)==header,records_stable=(r.read(base,len(raw))==raw if raw else True),records=rows,sources={},limitation='Scratch buffer rebuilds per native pass;count is not contact/event history. Pointers not dereferenced or registry-qualified;partial record fields only. Sequential checks not atomic.')
 for n in ['read_collision_buffer.py','read_live.py']:
  b=(root/n).read_bytes();(out/n).write_bytes(b);report['sources'][n]=hashlib.sha256(b).hexdigest()
 (out/'buffer.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['records','sources']}))
finally:K.CloseHandle(r.h)
