"""Bounded read-only steam cab capture, with UI controls kept separate."""
import argparse,json,time,shutil
from pathlib import Path
from read_live import Reader,K
from read_steam_cab import capture
p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=60);a=p.parse_args()
if Path(a.name).name!=a.name or not 0<a.seconds<=600:raise ValueError('Invalid bounds')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
    for n in ('sample_steam_cab.py','read_steam_cab.py','steam-cab-fields.json','read_live.py'):shutil.copy2(root/n,out/n)
    (out/'metadata.json').write_text(json.dumps(dict(image_sha256=r.sha,seconds=a.seconds,interval=.5),indent=2),encoding='utf-8')
    end=time.monotonic()+a.seconds;n=errors=0
    with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
        while time.monotonic()<end:
            start=time.monotonic()
            try:d=dict(monotonic=start,snapshot=capture(r))
            except Exception as e:d=dict(monotonic=start,error=str(e));errors+=1
            f.write(json.dumps(d)+'\n');f.flush();n+=1;time.sleep(max(0,.5-(time.monotonic()-start)))
    print(json.dumps(dict(samples=n,errors=errors)))
finally:K.CloseHandle(r.h)
