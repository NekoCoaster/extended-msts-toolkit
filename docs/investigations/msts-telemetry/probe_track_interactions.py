"""Read-only crossing request and sound-region candidate snapshot; no audio/barrier inference."""
import argparse,json,hashlib
from pathlib import Path
from collections import Counter
from read_infrastructure import InfrastructureReader
from read_live import K

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=InfrastructureReader(a.pid)
    try:
        start=r.f(0x80acd4);table=r.u(0x828108);rows=[];trains=[]
        for db in r.infrastructure()['databases']:
            for item in db['items']:
                if item['kind'] not in [2,4,7,10]:continue
                row=dict(item,database=db['address']);p=item['address']
                try:
                    index=r.u(p+8)
                    if index>=100000:raise ValueError('World object index bound')
                    obj=r.u(table+index*8) if index else 0
                    row.update(world_index=index,world_object=obj)
                    if item['kind']==2:
                        row.update(pickup_flags=r.u(p+0x2c),candidate_vehicle=r.u(p+0x34))
                        if obj:row.update(pickup_type=r.u(obj+0x90),minimum_speed=r.f(obj+0x88),maximum_speed=r.f(obj+0x8c))
                    elif item['kind']==4 and obj:
                        row.update(hazard_state_candidate=r.u(obj+0xac),hazard_requested_state=r.u(obj+0xb0),hazard_trigger_latch=r.read(obj+0xcc,1)[0])
                    elif item['kind']==7 and obj:
                        row.update(request_state=r.u(obj+0x90),flags_raw=r.u(obj+0x84),float_candidates={hex(off):r.f(obj+off) for off in [0x74,0x78,0x7c,0x80,0x88]})
                    elif item['kind']==10:row.update(region_index=r.u(p+0x2a),angle_candidate=r.f(p+0x2e))
                except (OSError,ValueError) as e:row['error']=str(e)
                rows.append(row)
        for t in r.trains():
            state=r.u(t['address']+0xea);row=dict(train=t['address'],state=state)
            if state:row.update(reference_distance_candidate=r.f(state),nearest_distance_candidate=r.f(state+4),selected_region=r.u(state+8),region_table=r.u(state+12))
            trains.append(row)
        result=dict(pid=a.pid,sha256=r.sha,sim_time=start,sim_time_after=r.f(0x80acd4),paused=r.u(0x7be0f4),items=rows,trains=trains)
        (out/'snapshot.json').write_text(json.dumps(result,indent=2,allow_nan=False));hashes={}
        for name in ['probe_track_interactions.py','read_infrastructure.py','read_topology.py','read_services.py','read_live.py']:
            data=(root/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
        (out/'sources.json').write_text(json.dumps(hashes,indent=2))
        print(json.dumps(dict(items=len(rows),errors=sum('error'in x for x in rows),kinds=dict(Counter(x['kind'] for x in rows)),loaded_crossing_items=sum(x['kind']==7 and bool(x.get('world_object')) for x in rows),request_states=dict(Counter(x['request_state'] for x in rows if 'request_state'in x)),trains=trains,same_sim_time=start==result['sim_time_after'])))
    finally:K.CloseHandle(r.h)
