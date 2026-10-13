"""Read-only bounded presence/car identity time series."""
import argparse,datetime,hashlib,json,math,time
from pathlib import Path
from read_presence_identity import snapshot,InfrastructureReader,K

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=60);p.add_argument('--interval',type=float,default=.25);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not all(math.isfinite(v) for v in (a.seconds,a.interval)) or not 0<=a.seconds<=600 or not .1<=a.interval<=10:p.error('Invalid bounds')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=InfrastructureReader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=a.interval,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sources={},access='QUERY_LIMITED_INFORMATION | VM_READ',limitations='Sequential full-route identity snapshots. Stable records and clocks are filters,not atomicity guarantees. Errors retained.')
        for name in ('capture_presence_identity.py','read_presence_identity.py','read_infrastructure.py','read_topology.py','read_services.py','read_live.py'):
            b=(root/name).read_bytes();(out/name).write_bytes(b);meta['sources'][name]=hashlib.sha256(b).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
            while True:
                begin=time.perf_counter()
                try:row=snapshot(r)
                except (OSError,ValueError) as e:row=dict(error=str(e));errors+=1
                row.update(monotonic=begin,monotonic_after=time.perf_counter());f.write(json.dumps(row,allow_nan=False)+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(max(0,a.interval-(time.perf_counter()-begin)))
        print(json.dumps(dict(output=str(out),samples=count,errors=errors)))
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
