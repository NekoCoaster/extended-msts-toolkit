"""Bounded read-only live activity-event discovery."""
import argparse,json,datetime
from pathlib import Path
from read_live import Reader,K

def capture(r):
    root=r.u(0x809b34);n=r.u(root);seen=set();events=[]
    while n!=root:
        if not n or n in seen or len(seen)>=1024:raise ValueError('Event list cycle/bound')
        seen.add(n);e=r.u(n+8)
        row=dict(address=e,category=r.u(e+4),type=r.u(e+8),id=r.u(e+12),state_10=r.u(e+0x10),state_20=r.u(e+0x20),activation_level=r.u(e+0x24),outcome_count=r.u(e+0x66),reversible_candidate=r.u(e+0x6a))
        if row['category']==2:
            tx,tz,x,z,radius,stop=r.unpack(e+0x6e,'iifffI');row['location']=dict(tile=[tx,tz],offset=[x,z],radius=radius,trigger_on_stop=stop)
        count=row['outcome_count']
        if count>5:row['outcomes_error']='Outcome count exceeds inline capacity inferred from layout'
        else:row['outcomes_raw']=[list(r.unpack(e+0x2a+i*12,'III')) for i in range(count)]
        events.append(row);n=r.u(n)
    return dict(activity_base=0x809810,event_sentinel=root,events=events)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args();root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        d=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),activity=capture(r));d['sim_time_after']=r.f(0x80acd4)
        for name in ['read_activity.py','read_live.py']:(out/name).write_bytes((root/name).read_bytes())
        (out/'activity.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
    finally:K.CloseHandle(r.h)
