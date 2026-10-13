"""Bounded read-only wheel-matrix sequence for one representative of each shape/train class."""
import argparse,datetime,hashlib,json,math,struct,time
from pathlib import Path
from read_live import K
from read_physical_registry import PhysicalRegistryReader
from read_wheel_animation import sample
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=70);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..') or not 0<a.seconds<=180:p.error('Invalid bounds')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=PhysicalRegistryReader(a.pid)
def matrix(ptr):
 b=r.read(ptr,48)
 if not all(math.isfinite(v) for v in struct.unpack('<12f',b)):raise ValueError('Nonfinite matrix')
 return dict(pointer=ptr,raw=b.hex(),stable=r.read(ptr,48)==b)
try:
 meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=.25,sources={})
 for n in ('sample_wheel_matrices.py','read_live.py','read_physical_registry.py','read_wheel_animation.py'):
  b=(root/n).read_bytes();(out/n).write_bytes(b);meta['sources'][n]=hashlib.sha256(b).hexdigest()
 (out/'metadata.json').write_text(json.dumps(meta,indent=2));start=time.perf_counter();count=0
 with (out/'samples.jsonl').open('w') as f:
  while time.perf_counter()-start<a.seconds:
   t=time.perf_counter();d=dict(elapsed=t-start,vehicles=[])
   try:
    d.update(day=r.f(0x80acd4),paused=r.u(0x7be0f4));seen=set()
    for v in sample(r)['vehicles'] or []:
     if 'error' in v or not v['identity_stable']:continue
     car=v['address'];shape=r.u(car+0x10);kind=r.unpack(shape+8,'H')[0];key=(bool(v.get('train',{}).get('is_player')),kind)
     if key in seen or kind not in (4,5):continue
     seen.add(key);row=dict(object_id=v['object_id'],car=car,shape=shape,kind=kind,train=v.get('train'),rate=r.f(car+0x1b0),matrices=[]);d['vehicles'].append(row)
     try:
      table=r.u(shape)
      if kind==4:
       if table!=8555304:raise ValueError('Unsupported type4 table')
       for g in range(2):
        context=car+0xb0+g*0x3c;raw=r.read(context,0x3c)
        if struct.unpack_from('<I',raw,4)[0]!=car:raise ValueError('Owner mismatch')
        for j in range(3):
         ptr=struct.unpack_from('<I',raw,0x18+j*4)[0]
         if ptr:row['matrices'].append(dict(index=g*3+j,**matrix(ptr)))
        if r.read(context,0x3c)!=raw:row['context_changed']=True
      else:
       if not v['shape']['available'] or not v['shape']['identity_stable']:raise ValueError('Unsupported type5')
       num,mat,slots=struct.unpack('<III',r.read(shape+0x98,12))
       if not 0<num<=512 or not mat or not slots:raise ValueError('Invalid layout')
       raw=r.read(slots,num*16)
       for i in range(num):
        cb,ctx,_,_=struct.unpack_from('<IIII',raw,i*16)
        if cb==0x403512:
         if r.read(cb,5)!=bytes.fromhex('e96a1e1d00') or r.u(ctx+4)!=car:raise ValueError('Wheel callback mismatch')
         row['matrices'].append(dict(index=i,**matrix(mat+i*48)))
       row['layout_stable']=r.read(slots,num*16)==raw and struct.unpack('<III',r.read(shape+0x98,12))==(num,mat,slots)
      row['identity_stable']=r.u(car+0x50)==v['object_id'] and r.u(car+0x10)==shape and r.u(shape)==table
     except (ValueError,OSError) as e:row['error']=str(e)
    d['day_after']=r.f(0x80acd4)
   except (ValueError,OSError) as e:d['error']=str(e)
   f.write(json.dumps(d,allow_nan=False)+'\n');f.flush();count+=1;time.sleep(max(0,.25-(time.perf_counter()-t)))
 print(json.dumps(dict(samples=count,output=str(out))))
finally:K.CloseHandle(r.h)
