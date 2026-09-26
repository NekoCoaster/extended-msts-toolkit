import argparse,json,time,shutil
from pathlib import Path
from read_electric_voltage import capture
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
 for name in ('sample_electric_voltage.py','read_electric_voltage.py','read_live.py'):shutil.copy2(root/name,out/name)
 (out/'metadata.json').write_text(json.dumps(dict(image_sha256=r.sha,seconds=40,interval=.05)),encoding='utf-8')
 end=time.monotonic()+40;n=errors=0
 with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
  while time.monotonic()<end:
   t=time.monotonic()
   try:d=dict(wall=t,snapshot=capture(r))
   except Exception as e:d=dict(wall=t,error=str(e));errors+=1
   f.write(json.dumps(d)+'\n');f.flush();n+=1;time.sleep(max(0,.05-(time.monotonic()-t)))
 print(json.dumps(dict(samples=n,errors=errors)))
finally:K.CloseHandle(r.h)
