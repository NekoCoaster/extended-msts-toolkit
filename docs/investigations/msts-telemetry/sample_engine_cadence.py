"""Bounded engine cadence observation; no UI automation or process writes."""
import json,time,shutil,argparse
from pathlib import Path
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
root=Path(__file__).resolve().parent
if Path(a.name).name!=a.name:raise ValueError('Invalid name')
out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
 for n in ('sample_engine_cadence.py','read_live.py'):shutil.copy2(root/n,out/n)
 (out/'metadata.json').write_text(json.dumps(dict(image_sha256=r.sha,duration=40,interval=.02)),encoding='utf-8')
 end=time.monotonic()+40;n=errors=0
 with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
  while time.monotonic()<end:
   t=time.monotonic()
   try:
    if r.u(0x7b6438)!=1:raise ValueError('Not steam')
    train=r.u(0x7c2ac0);lead=r.u(train+0x6a);obj=r.u(0x80aa1c)
    d=dict(wall=t,clock=r.f(0x80acd0),day=r.f(0x80acd4),paused=r.u(0x7be0f4),train=train,lead=lead,accumulator=r.f(train+0x8a),interval=r.f(train+0x8e),physics_time=r.f(obj+0x54),physics_step=r.f(obj+0x10),fire_mass=r.f(lead+0x2ca),burn=r.f(lead+0x32e),water=r.f(lead+0x2ce),usage=r.f(lead+0x312),generation=r.f(lead+0x316),speed=r.f(train+0x92),clock_after=r.f(0x80acd0),stable=r.u(0x7c2ac0)==train and r.u(train+0x6a)==lead)
   except Exception as e:d=dict(error=str(e),wall=t);errors+=1
   f.write(json.dumps(d)+'\n');n+=1;time.sleep(max(0,.02-(time.monotonic()-t)))
 print(json.dumps(dict(samples=n,errors=errors)))
finally:K.CloseHandle(r.h)
