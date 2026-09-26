"""Bounded electric traction trace; exact image and electric-kind guards inherited."""
import argparse,json,time,shutil
from pathlib import Path
from read_live import Reader,K
from read_electric_traction import capture
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=60);a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid);n=errors=0
try:
 for f in ('read_electric_series.py','read_electric_traction.py','read_live.py'):shutil.copy2(root/f,out/f)
 (out/'metadata.json').write_text(json.dumps(dict(sha256=r.sha,requested_seconds=a.seconds,interval=.05)),encoding='utf-8')
 start=time.perf_counter()
 with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
  while time.perf_counter()-start<a.seconds:
   try:
    s=capture(r);s['elapsed']=time.perf_counter()-start;s['train_speed']=r.f(s['train']+0x92);s['brake_mode']=r.u(s['lead']+0x3f2);s['pantograph']=r.u(s['controller']+0x264)
    s['powered_cars']=[]
    for train in r.trains():
     if not train['is_player']:continue
     for car in train['cars']:
      if not car['powered']:continue
      c=car['address'];d=car['engine_definition']
      s['powered_cars'].append(dict(address=c,is_lead=c==s['lead'],type_word=r.u(c),flags80=r.read(c+0x80,1)[0],flags296=r.u(c+0x296),force=r.f(c+0x29e),power=r.f(c+0x2a2),current_union=r.f(c+0x2c2),max_force=r.f(d+0x102),max_power=r.f(d+0xfe),car102_raw=r.f(c+0x102),owner_stable=r.u(c+0x98)==train['address']))
   except Exception as e:s=dict(error=str(e));errors+=1
   f.write(json.dumps(s)+'\n');f.flush();n+=1;time.sleep(.05)
 print(json.dumps(dict(output=str(out),samples=n,errors=errors)))
finally:K.CloseHandle(r.h)
