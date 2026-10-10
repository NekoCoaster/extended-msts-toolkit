"""Read-only paired station/event/result observations;stop.request ends capture cleanly."""
import argparse,json,math,shutil,hashlib,time
from pathlib import Path
from read_live import K
from read_services import ServiceReader
from read_station_series import sample as station_sample
from read_activity import capture

def sample(r):
    row=station_sample(r)
    row['events']=capture(r)
    row['event_root_stable']=row['events']['event_sentinel']==r.u(0x809b34)
    row['sim_time_after']=r.f(0x80acd4)
    return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=60);p.add_argument('--interval',type=float,default=.1);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not math.isfinite(a.seconds) or not math.isfinite(a.interval) or a.seconds<0 or a.interval<=0:p.error('Invalid name/timing')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=a.interval,access='QUERY_LIMITED_INFORMATION | VM_READ',limitations='Sequential reads; stable list pointers do not prove atomicity or exclude reuse. Recorded arrival may be synthesized. Flags are raw branch-local bits. AI writer semantics unvalidated.',sources={})
        for n in ('read_outcome_series.py','read_station_series.py','read_activity.py','read_services.py','read_live.py'):
            shutil.copy2(root/n,out/n);meta['sources'][n]=hashlib.sha256((root/n).read_bytes()).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
        start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
            while True:
                try:row=sample(r);row['elapsed']=time.perf_counter()-start;line=json.dumps(row,allow_nan=False)
                except (OSError,ValueError) as e:line=json.dumps(dict(error=str(e),elapsed=time.perf_counter()-start));errors+=1
                f.write(line+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds or (out/'stop.request').exists():break
                time.sleep(a.interval)
        print(json.dumps(dict(output=str(out),samples=count,errors=errors)))
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
