"""Bounded external clock capture; stops15simulation seconds after observed midnight wrap."""
import argparse,datetime,hashlib,json,math,shutil,time
from pathlib import Path
from read_live import Reader,K

def sample(r):
    raw=r.read(0x80acb8,32)
    import struct
    day,month,year,second,minute,hour,elapsed,day_seconds=struct.unpack('<6I2f',raw)
    row=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),day=day,month=month,year=year,second=second,minute=minute,hour=hour,
        elapsed=elapsed,day_seconds=day_seconds,raw_hex=raw.hex(),paused=r.u(0x7be0f4),player=r.u(0x7c2ac0),step=r.f(0x828fb4),activity_start=r.f(0x80988c))
    after=r.read(0x80acb8,32);row['clock_block_stable']=after==raw;row['clock_after_hex']=after.hex()
    return row

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=4000);p.add_argument('--interval',type=float,default=.1);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not math.isfinite(a.seconds) or not math.isfinite(a.interval) or a.seconds<0 or a.interval<=0:p.error('Invalid name/timing')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        sources={}
        for name in ('read_clock_series.py','read_live.py'):
            shutil.copy2(root/name,out/name);sources[name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
        (out/'metadata.json').write_text(json.dumps(dict(pid=a.pid,sha256=r.sha,access='QUERY_LIMITED_INFORMATION | VM_READ',seconds=a.seconds,interval=a.interval,sources=sources,limits='Sequential external snapshots;matching32byte rereads do not prove atomicity. Wrap detector is >86000to<1000 with nonnull player and monotonic elapsed;not a general session detector.'),indent=2)+'\n')
        start=time.perf_counter();previous=None;wrap_elapsed=None;count=errors=0;reason='time_limit'
        with (out/'samples.jsonl').open('w') as f:
            while True:
                try:
                    row=sample(r);row['wall_elapsed']=time.perf_counter()-start
                    if previous and previous['day_seconds']>86000 and row['day_seconds']<1000 and row['player'] and row['elapsed']>=previous['elapsed']:wrap_elapsed=row['elapsed']
                    line=json.dumps(row,allow_nan=False);previous=row
                except (OSError,ValueError) as e:line=json.dumps(dict(error=str(e),wall_elapsed=time.perf_counter()-start));errors+=1
                f.write(line+'\n');f.flush();count+=1
                if wrap_elapsed is not None and previous['elapsed']>=wrap_elapsed+15:reason='15_simulation_seconds_after_wrap';break
                if (out/'stop.request').exists():reason='stop_request';break
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(a.interval)
        result=dict(samples=count,errors=errors,reason=reason,wrap_elapsed=wrap_elapsed,wall_elapsed=time.perf_counter()-start)
        (out/'completion.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
    finally:K.CloseHandle(r.h)
