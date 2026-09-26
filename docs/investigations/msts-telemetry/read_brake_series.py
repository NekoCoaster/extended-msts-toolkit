"""Bounded read-only time series for all physical-car brake candidates."""
import argparse,datetime,json,time,shutil
from pathlib import Path
from read_live import Reader,K
from read_brake_state import sample
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=90);a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid);count=0;errors=0
try:
    for f in ('read_brake_series.py','read_brake_state.py','read_live.py','binary_fields.py'):shutil.copy2(root/f,out/f)
    (out/'metadata.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,requested_seconds=a.seconds,requested_interval=.05)),encoding='utf-8')
    start=time.perf_counter()
    with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
        while time.perf_counter()-start<a.seconds:
            try:
                t=r.u(0x7c2ac0);ctl=r.u(r.u(t+0x72)+8)
                row=dict(elapsed=time.perf_counter()-start,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),trains=sample(r),timers=[r.f(0x80a1f0),r.f(0x80a1ec)],control_type=r.u(0x7b6438),train_brake=r.f(ctl+0x128),speed=r.f(t+0x92))
                lead=r.u(t+0x6a)
                row['selected_mode']=r.u(lead+0x3f2);row['selected_fraction']=r.f(lead+0x3f6);row['pipe_command']=r.f(lead+0x40a)
                row['sim_time_after']=r.f(0x80acd4)
            except Exception as e:row=dict(error=str(e));errors+=1
            f.write(json.dumps(row)+'\n');f.flush();count+=1;time.sleep(.05)
    print(json.dumps(dict(output=str(out),samples=count,errors=errors)))
finally:K.CloseHandle(r.h)
