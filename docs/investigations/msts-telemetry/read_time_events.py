"""Read-only time-event subtype fields; never invoke native predicates."""
import argparse,datetime,hashlib,json,shutil
from pathlib import Path
from read_live import Reader,K
from read_activity import capture

def sample(r):
    start=r.f(0x80acd4)
    activity=capture(r)
    events=[]
    for e in activity['events']:
        if e['category']==0 and e['type']==0:
            threshold=r.f(e['address']+0x6e)
            clock=r.f(0x80acd0)
            events.append(dict(event=e,threshold=threshold,event_clock=clock,predicate=threshold<clock))
    return dict(sim_time=start,sim_time_after=r.f(0x80acd4),paused=r.u(0x7be0f4),events=events,
        sentinel_stable=activity['event_sentinel']==r.u(0x809b34))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Name must be one component')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        d=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,snapshot=sample(r),
            limitations='Sequential read;threshold compared in Python,not native invocation. Category/type0/0 only;no reset or reversal proof.')
        for n in ('read_time_events.py','read_activity.py','read_live.py'):shutil.copy2(root/n,out/n)
        (out/'time-events.json').write_text(json.dumps(d,indent=2))
        print(json.dumps({'events':[(x['event']['id'],x['threshold'],x['event']['state_10']) for x in d['snapshot']['events']],'sim_time':d['snapshot']['sim_time']}))
    finally:K.CloseHandle(r.h)
