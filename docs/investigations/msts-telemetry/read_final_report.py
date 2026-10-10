"""Bounded read-only finalized evaluation records; no native calls or string dereference."""
import argparse,datetime,json,shutil
from pathlib import Path
from read_live import Reader,K

def walk(r,slot,fmt,names):
    root=r.u(slot);rows=[];seen=set()
    if root:
        node=r.u(root)
        while node!=root:
            if not node or node in seen or len(seen)>=1024:raise ValueError('Report list bound/cycle')
            seen.add(node);p=r.u(node+8)
            rows.append(dict(address=p,**dict(zip(names,r.unpack(p,fmt))),node_stable=r.u(node+8)==p))
            node=r.u(node)
    return dict(root=root,root_stable=root==r.u(slot),records=rows)

def capture(r):
    b=0x809790
    return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),day_seconds=r.f(0x80acd4),paused=r.u(0x7be0f4),player=r.u(0x7c2ac0),
        activity_stop=r.u(0x809b58),activity_success=r.u(0x809b5c),
        report_success=r.u(b+4),presence_flags=r.u(b+8),termination_code=r.u(b+12),duration=r.f(b+16),
        late_arrival_count=r.u(b+0x48),missed_stop_count=r.u(b+0x4c),last_arrival_deviation=r.f(b+0x50),last_departure_deviation=r.f(b+0x54),
        station_count=r.u(b+0x60),action_count=r.u(b+0x64),unlatched_action_count=r.u(b+0x68),distance_unit_flag=r.u(b+0x6c),
        stations=walk(r,b+0x58,'IfffffH',('name_pointer','location_raw','scheduled_arrival','recorded_arrival','scheduled_departure','recorded_departure','flags')),
        actions=walk(r,b+0x5c,'6I',('type','type_label_pointer','extension72_text_pointer','extension76_text_pointer','event14_text_pointer','trigger_latch')),
        day_seconds_after=r.f(0x80acd4))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid capture name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        d=dict(sha256=r.sha,access='QUERY_LIMITED_INFORMATION | VM_READ',snapshot=capture(r),limits='Sequential snapshot,not atomic. Native finalization-only fields can be empty/stale during gameplay. String pointers retained raw and not dereferenced. Station location units require report flag/context.')
        (out/'report.json').write_text(json.dumps(d,indent=2)+'\n')
        for name in ('read_final_report.py','read_live.py'):shutil.copy2(root/name,out/name)
        print(json.dumps(d))
    finally:K.CloseHandle(r.h)
