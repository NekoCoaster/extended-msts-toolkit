"""Read-only bounded player monitor sequence; gameplay controlled separately via UI."""
import argparse,datetime,hashlib,json,struct,time
from pathlib import Path
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=90);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..') or not 0<a.seconds<=180:p.error('Invalid bounds')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
 meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=.05,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sources={})
 for name in ('sample_monitor_cadence.py','read_live.py'):
  b=(root/name).read_bytes();(out/name).write_bytes(b);meta['sources'][name]=hashlib.sha256(b).hexdigest()
 (out/'metadata.json').write_text(json.dumps(meta,indent=2));start=time.perf_counter();count=errors=0
 with (out/'samples.jsonl').open('w') as f:
  while time.perf_counter()-start<a.seconds:
   t=time.perf_counter();d=dict(elapsed=t-start)
   try:
    train=r.u(0x7c2ac0)
    if not train:raise ValueError('No player train')
    lead=r.u(train+0x6a);ed=r.u(lead+0x29a);obj=r.u(0x80aa1c);ident=r.u(lead+0x50)
    if not lead or not ed or not obj:raise ValueError('Missing context')
    d.update(vigilance_global=r.u(0x790d88),aws_global=r.u(0x790d8c),day=r.f(0x80acd4),clock=r.f(0x80acd0),paused=r.u(0x7be0f4),train=train,lead=lead,object_id=ident,definition=ed,interval=r.f(train+0x8e),accumulator=r.f(train+0x8a),physics_time=r.f(obj+0x54),speed=r.f(lead+0x1bc),brake_cylinder=r.f(lead+0x230),brake_pipe=r.f(lead+0x238),equalizing_reservoir=r.f(lead+0x40a),brake_flags=r.u(lead+0x3f2),engine_flags=r.u(lead+0x296),monitors={})
    for name,off,def_off in [('aws',0x4ba,0xb0c),('vigilance',0x4fa,0xb78),('emergency',0x53a,0xbe4),('unnamed',0x57a,0xc50),('overspeed',0x5ba,0xcbc)]:
     raw=r.read(lead+off,64)
     if struct.unpack_from('<I',raw,60)[0]!=ed+def_off:raise ValueError('Unexpected monitor link')
     d['monitors'][name]=dict(raw=raw.hex(),stable=r.read(lead+off,64)==raw)
    d.update(clock_after=r.f(0x80acd0),context_stable=r.u(0x7c2ac0)==train and r.u(train+0x6a)==lead and r.u(lead+0x50)==ident and r.u(lead+0x29a)==ed)
   except (OSError,ValueError) as e:d['error']=str(e);errors+=1
   f.write(json.dumps(d,allow_nan=False)+'\n');f.flush();count+=1;time.sleep(max(0,.05-(time.perf_counter()-t)))
 print(json.dumps(dict(samples=count,errors=errors,output=str(out))))
finally:K.CloseHandle(r.h)
