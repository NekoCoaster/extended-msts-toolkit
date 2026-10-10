"""Read fixed globals across normal UI unload/reload; no heap dereference or readiness claim."""
import argparse,datetime,hashlib,json,math,shutil,time
from pathlib import Path
from read_live import Reader,K

def sample(r):
    clock=r.unpack(0x80acb8,'6i2f')
    return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        calendar=dict(zip(('day','month','year','second','minute','hour'),clock[:6])),
        elapsed=clock[6],day_seconds=clock[7],paused=r.u(0x7be0f4),
        player=r.u(0x7c2ac0),controller=r.u(0x7b6440),control_type=r.u(0x7b6438),
        station_sentinel=r.u(0x809810+0xb0),selected=r.u(0x809810+0xb4),previous=r.u(0x809810+0xb8),
        event_sentinel=r.u(0x809b34),stop=r.u(0x809810+0x348),success=r.u(0x809810+0x34c),
        boarding_active=r.u(0x809810+0x370),remaining=r.f(0x809810+0x374),
        day_seconds_after=r.f(0x80acd4))

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=600);p.add_argument('--interval',type=float,default=.05);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not math.isfinite(a.seconds) or not math.isfinite(a.interval) or a.seconds<0 or a.interval<=0:p.error('Invalid capture name/timing')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        sources={}
        for name in ('read_session_reset.py','read_live.py'):
            shutil.copy2(root/name,out/name);sources[name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
        (out/'metadata.json').write_text(json.dumps(dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=a.interval,access='QUERY_LIMITED_INFORMATION | VM_READ',sources=sources,limitations='Fixed globals sampled sequentially. Nonzero pointers can be stale during unload/loading;not dereferenced and not load-readiness evidence. Clock block read is not guaranteed atomic.'),indent=2)+'\n')
        start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
            while True:
                try:row=sample(r);row['wall_elapsed']=time.perf_counter()-start;line=json.dumps(row,allow_nan=False)
                except (OSError,ValueError) as e:line=json.dumps(dict(error=str(e),wall_elapsed=time.perf_counter()-start));errors+=1
                f.write(line+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds or (out/'stop.request').exists():break
                time.sleep(a.interval)
        print(json.dumps(dict(output=str(out),samples=count,errors=errors)))
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
