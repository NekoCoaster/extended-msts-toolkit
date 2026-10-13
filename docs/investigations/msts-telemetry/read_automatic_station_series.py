"""Read-only automatic-player and station context; stop.request ends capture cleanly."""
import argparse,json,math,shutil,hashlib,time
from pathlib import Path
from read_live import K
from read_services import ServiceReader
from read_station_series import sample as station_sample

def sample(r):
    gate=r.u(0x809e1c);player=r.u(0x7c2ac0)
    if not player:
        return dict(available=False,reason='no player train',driver_gate=gate,paused=r.u(0x7be0f4),sim_time=r.f(0x80acd4))
    player_service=r.u(player+0xe6)
    row=station_sample(r)
    row['automatic_driver']=dict(gate=gate,train=player,service=player_service,path=r.u(player_service+0x130),control_type=r.u(0x7b6438))
    for service in row['services']:
        addr=service['address']
        service['ai_wait']={hex(off):r.f(addr+off) for off in (0x1ec,0x1f0,0x210)}
        service['selected_after_wait']=r.u(addr+0x34)
        service['wait_selection_stable']=service['selected_after_wait']==service['selected']
    row['automatic_driver'].update(train_stable=r.u(0x7c2ac0)==player,service_stable=r.u(player+0xe6)==player_service,gate_stable=r.u(0x809e1c)==gate)
    row['sim_time_after']=r.f(0x80acd4)
    return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=60);p.add_argument('--interval',type=float,default=.1);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not math.isfinite(a.seconds) or not math.isfinite(a.interval) or a.seconds<0 or a.interval<=0:p.error('Invalid name/timing')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=a.interval,access='QUERY_LIMITED_INFORMATION | VM_READ',limitations='Sequential reads; stable list pointers do not prove atomicity or exclude reuse. Recorded arrival may be synthesized. Flags are raw branch-local bits. AI writer semantics unvalidated.',sources={})
        for n in ('read_automatic_station_series.py','read_station_series.py','read_services.py','read_live.py'):
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
