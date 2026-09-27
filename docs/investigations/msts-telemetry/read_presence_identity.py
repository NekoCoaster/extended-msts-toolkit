"""Bounded identity join between presence records and enumerated physical cars."""
import argparse,datetime,hashlib,json,struct
from pathlib import Path
from read_infrastructure import InfrastructureReader
from read_live import K

def snapshot(r):
    result=dict(sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4))
    trains=r.trains();cars={c['address']:(t,c) for t in trains for c in t['cars']}
    infra=r.infrastructure();rows=[]
    for node in infra['vector_presence']:
        for entry in node['entries']:
            p=entry['address'];raw=r.read(p,0x1c);words=struct.unpack('<7I',raw)
            row=dict(entry,raw_hex=raw.hex(),physical_car_candidate=words[4],car_id_candidate=words[5],direction_raw=raw[24])
            if words[4] in cars:
                train,car=cars[words[4]];cp=car['address'];track=r.read(cp+0x128,0x18)
                tn,section,sp,direction,distance,sd=struct.unpack('<4I2f',track)
                row.update(train_id=train['id'],is_player=train['is_player'],train_service=train['service_object'],service_matches=train['service_object']==entry['service'],car_backlink=r.u(cp+0x258),backlink_matches=r.u(cp+0x258)==p,track_node=tn,track_distance=distance,track_direction=direction,same_node=tn==words[0],presence_minus_physical=struct.unpack_from('<f',raw,4)[0]-distance)
            row['record_stable']=raw==r.read(p,0x1c)
            rows.append(row)
    lists=[]
    for addr in (0x8099bc,0x809b04):
        head=r.u(addr);values=r.list_values(head,4096)
        lists.append(dict(root_address=addr,sentinel=head,records=values,pointer_stable=head==r.u(addr)))
    result.update(rows=rows,physical_refresh_lists=lists,physical_cars=len(cars),services=infra['topology']['services'],sim_time_after=r.f(0x80acd4),paused_after=r.u(0x7be0f4))
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=InfrastructureReader(a.pid)
    try:
        result=snapshot(r);result.update(sha256=r.sha,pid=a.pid,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sources={},limitations='Sequential read-only snapshot. Registry membership guards candidate pointer dereferences;pointer/backlink equality does not prove lifetime identity or atomic state. Raw record bytes retained;node_distance from initial enumeration may be older than raw record.')
        for name in ('read_presence_identity.py','read_infrastructure.py','read_topology.py','read_services.py','read_live.py'):
            b=(root/name).read_bytes();(out/name).write_bytes(b);result['sources'][name]=hashlib.sha256(b).hexdigest()
        (out/'identity.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
        print(json.dumps(dict(output=str(out),clock=result['sim_time'],same_clock=result['sim_time']==result['sim_time_after'],paused=result['paused'],records=len(result['rows']),joined=sum('train_id' in x for x in result['rows']),list_counts=[len(x['records']) for x in result['physical_refresh_lists']])) )
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
