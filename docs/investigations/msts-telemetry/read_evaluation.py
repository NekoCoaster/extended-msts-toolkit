"""Bounded external reads of player evaluation episode lists; no game calls."""
import argparse,json,shutil
from pathlib import Path
from read_live import Reader,K

def records(r,address,fmt,names,bound=128):
    root=r.u(address)
    if not root:return None
    n=r.u(root);seen=set();result=[]
    while n!=root:
        if not n or n in seen or len(seen)>=bound:raise ValueError('Evaluation list bound/cycle')
        seen.add(n);p=r.u(n+8);result.append(dict(address=p,**dict(zip(names,r.unpack(p,fmt)))));n=r.u(n)
    return result

def capture(r):
    a=0x809810;b=0x809790;start=r.f(0x80acd4)
    speed=records(r,b+0x28,'fffffI',['start','location_raw','limit','duration','peak_adjusted_speed','subtype'])
    errors=records(r,b+0x24,'ffI',['time','location_raw','code'])
    conditions=dict(freight_count=r.u(b+0x3c),passenger_count=r.u(b+0x40),freight_records=records(r,b+0x2c,'ff',['time','location_raw']),passenger_records=records(r,b+0x30,'ff',['time','location_raw']),last_record_time=r.f(a+0x384),sample_interval=r.f(0x753d78),initial_time_sentinel=r.f(0x758b84),report_presence_flags=r.u(b+8))
    return dict(vehicle_conditions=conditions,sim_time=start,speed_episode_count=r.u(b+0x38),speed_episode_duration=r.f(b+0x44),active=r.u(a+0x398),active_start=r.f(a+0x388),active_location_raw=r.f(a+0x38c),active_peak_adjusted_speed=r.f(a+0x390),active_limit=r.f(a+0x394),active_subtype=r.u(a+0x39c),speed_records=speed,operational_error_count=r.u(b+0x34),operational_errors=errors,tolerance=r.f(0x7705b0),sim_time_after=r.f(0x80acd4),paused=r.u(0x7be0f4))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Name must be one component')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        d=dict(image_sha256=r.sha,snapshot=capture(r));(out/'evaluation.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
        for name in ('read_evaluation.py','read_live.py'):shutil.copy2(root/name,out/name)
        print(json.dumps(d))
    finally:K.CloseHandle(r.h)
