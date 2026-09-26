"""Read-only station-stop transitions; sequential observations, not atomic events."""
import argparse, datetime, hashlib, json, math, shutil, struct, time
from pathlib import Path
from read_services import ServiceReader
from read_live import K

def sample(r):
    row=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4))
    activity=0x809810
    row['activity']=dict(boarding_active=r.u(activity+0x370),remaining=r.f(activity+0x374),stop=r.u(activity+0x348),success=r.u(activity+0x34c))
    player=r.u(0x7c2ac0)
    row['player']=dict(address=player,speed=r.f(player+0x92)) if player else None
    row['services']=[]
    for entry in r.registry()['entries']:
        s=entry['address'];sentinel=r.u(s+0x30);node=r.u(sentinel);seen=set()
        x=dict(address=s,is_player=entry['is_player'],selected=r.u(s+0x34),previous=r.u(s+0x38),efficiency=r.f(s+0x208),progress=r.f(s+0x1d0),records=[])
        while node!=sentinel:
            if not node or node in seen or len(seen)>=256:raise ValueError('Invalid/bounded station list')
            seen.add(node);record=r.u(node+8);raw=r.read(record,0x28)
            u=lambda off:struct.unpack_from('<I',raw,off)[0]
            f=lambda off:struct.unpack_from('<f',raw,off)[0]
            x['records'].append(dict(address=record,platform=u(0),scheduled_arrival=f(4),recorded_arrival=f(8),scheduled_departure=f(12),recorded_departure=f(16),distance=f(20),skip=struct.unpack_from('<H',raw,28)[0],flags=struct.unpack_from('<H',raw,30)[0],merge_flags=u(32),efficiency=f(36),raw_hex=raw.hex(),node_stable=r.u(node+8)==record))
            node=r.u(node)
        x['selection_stable']=r.u(s+0x34)==x['selected']
        x['sentinel_stable']=r.u(s+0x30)==sentinel
        row['services'].append(x)
    row['sim_time_after']=r.f(0x80acd4)
    return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=60);p.add_argument('--interval',type=float,default=.1);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not math.isfinite(a.seconds) or not math.isfinite(a.interval) or a.seconds<0 or a.interval<=0:p.error('Invalid name/timing')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=a.interval,access='QUERY_LIMITED_INFORMATION | VM_READ',limitations='Sequential reads; stable list pointers do not prove atomicity or exclude reuse. Recorded arrival may be synthesized. Flags are raw branch-local bits. AI writer semantics unvalidated.',sources={})
        for n in ('read_station_series.py','read_services.py','read_live.py'):
            shutil.copy2(root/n,out/n);meta['sources'][n]=hashlib.sha256((root/n).read_bytes()).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
        start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
            while True:
                try:row=sample(r);row['elapsed']=time.perf_counter()-start;line=json.dumps(row,allow_nan=False)
                except (OSError,ValueError) as e:line=json.dumps(dict(error=str(e),elapsed=time.perf_counter()-start));errors+=1
                f.write(line+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(a.interval)
        print(json.dumps(dict(output=str(out),samples=count,errors=errors)))
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
