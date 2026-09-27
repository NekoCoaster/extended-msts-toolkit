"""Capture bounded read-only wheel snapshots while normal UI controls gameplay."""
import argparse
import datetime
import hashlib
import json
import time
from pathlib import Path
from read_wheel_animation import sample
from read_physical_registry import PhysicalRegistryReader
from read_live import K
p=argparse.ArgumentParser()
p.add_argument('--pid',type=int,required=True)
p.add_argument('--name',required=True)
p.add_argument('--seconds',type=float,default=40)
p.add_argument('--interval',type=float,default=0.5)
a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
if not 0<a.seconds<=180 or not .1<=a.interval<=10:p.error('Capture bounds')
root=Path(__file__).resolve().parent
out=root/'captures'/a.name
out.mkdir(exist_ok=False)
r=PhysicalRegistryReader(a.pid)
try:
    metadata=dict(pid=a.pid,sha256=r.sha,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seconds=a.seconds,interval=a.interval,sources={})
    for name in ('read_live.py','read_physical_registry.py','read_wheel_animation.py','capture_wheel_sequence.py'):
        raw=(root/name).read_bytes();(out/name).write_bytes(raw)
        metadata['sources'][name]=hashlib.sha256(raw).hexdigest()
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2))
    start=time.perf_counter();count=0;errors=0
    with (out/'samples.jsonl').open('w') as stream:
        while time.perf_counter()-start<a.seconds:
            before=time.perf_counter()
            row=dict(elapsed=before-start)
            try:
                row.update(sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),sample=sample(r),sim_time_after=r.f(0x80acd4))
            except (OSError,ValueError) as error:
                row['error']=str(error);errors+=1
            row['read_seconds']=time.perf_counter()-before
            stream.write(json.dumps(row,allow_nan=False)+'\n');stream.flush();count+=1
            time.sleep(max(0,a.interval-(time.perf_counter()-before)))
    print(json.dumps(dict(output=str(out),samples=count,outer_errors=errors)))
finally:
    K.CloseHandle(r.h)
