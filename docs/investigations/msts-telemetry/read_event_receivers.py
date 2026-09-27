"""Bounded native receiver-list observation and physical-car handle associations."""
import argparse,datetime,json,shutil
from pathlib import Path
from read_live import Reader,K

def capture(r):
    time=r.f(0x80acd4);manager=r.u(0x7c32f0);root=r.u(manager+0x14a);first=r.u(root)
    node=first;seen=set();rows=[];links=[];table=r.u(0x828108)
    listener=list(r.unpack(manager+0x14e,'3f'))
    while node!=root:
        if not node or node in seen or len(seen)>=4096:raise ValueError('Invalid receiver list/cycle/bound')
        seen.add(node);nxt,prev,obj=r.unpack(node,'III');definition=r.u(obj+0x10)
        if not definition:raise ValueError('Missing receiver definition')
        handle=r.u(obj+4)
        if not 0<handle<1000000 or r.u(table+handle*8)!=obj:raise ValueError('Receiver registry mismatch')
        streams=r.u(definition+0x10);slots=r.u(definition+0xc)
        if streams>4096 or slots>65536:raise ValueError('Definition count exceeds research bound')
        rows.append(dict(node=node,object=obj,handle=handle,class_handle=r.u(obj),definition=definition,stream_count=streams,trigger_state_slot_count=slots,stream_state=r.u(obj+0x14),trigger_state=r.u(obj+0x18),flags=r.u(obj+0x1c),event_masks=[r.u(obj+0x20),r.u(obj+0x24)],scalars=[r.f(obj+x) for x in [0x28,0x2c,0x30]],previous_scalars=[r.f(obj+x) for x in [0x3c,0x40,0x44]],last_processing_tick_ms=r.u(obj+0x50)))
        rows[-1].update(position=list(r.unpack(obj+0x58,'3f')),stored_squared_distance=r.f(obj+0x38),activation_flags=r.u(definition+0x18),activation_distance_threshold=r.f(definition+0x1c),deactivation_flags=r.u(definition+0x24),deactivation_distance_threshold=r.f(definition+0x28))
        # Same indirect string source used by debug formatter0053af56.
        try:
            name_object=r.u(definition+4);name_pointer=r.u(name_object+4);raw=bytearray()
            for i in range(512):
                unit=r.read(name_pointer+i*2,2)
                if unit==b'\0\0':break
                raw.extend(unit)
            else:raise ValueError('Label exceeds512 UTF16 units')
            rows[-1]['definition_label']=raw.decode('utf-16le')
        except (OSError,ValueError) as error:rows[-1]['label_unavailable']=str(error)
        links.append((node,nxt,obj));node=nxt
    associations=[]
    for train in r.trains():
        for car in train['cars']:
            for off in ([0x25c,0x4b6] if car['powered'] else [0x25c]):
                associations.append(dict(train=train['address'],train_id=train['id'],is_player=train['is_player'],car=car['address'],source_offset=hex(off),handle=r.u(car['address']+off)))
    known={x['handle'] for x in rows}
    for row in rows:row['car_associations']=[a for a in associations if a['handle']==row['handle']]
    stable=r.u(0x7c32f0)==manager and r.u(manager+0x14a)==root and r.u(root)==first and r.u(0x828108)==table and all(r.u(n)==nxt and r.u(n+8)==obj for n,nxt,obj in links)
    return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),time=time,time_after=r.f(0x80acd4),paused=r.u(0x7be0f4),manager=manager,sentinel=root,listener_position=listener,stable_list=stable,receivers=rows,car_handles_absent_from_list=[a for a in associations if a['handle'] and a['handle'] not in known],limitations='Non-atomic enumeration. List stability checks cannot exclude remove/reinsert ABA. Unassociated receiver does not prove environmental or AI ownership. Probe bounds are not native capacities. Stream count is allocation metadata, not active playback count.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Invalid capture name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        d=dict(image_sha256=r.sha,snapshot=capture(r));(out/'receivers.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
        for name in ['read_event_receivers.py','read_live.py']:shutil.copy2(root/name,out/name)
        s=d['snapshot'];print(json.dumps(dict(time=s['time'],paused=s['paused'],stable=s['stable_list'],count=len(s['receivers']),associated=sum(bool(x['car_associations']) for x in s['receivers']),streams=sum(x['stream_count'] for x in s['receivers']),unlisted_handles=s['car_handles_absent_from_list'])))
    finally:K.CloseHandle(r.h)
