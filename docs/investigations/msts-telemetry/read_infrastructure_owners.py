"""Route-wide junction association and vector-list snapshot; query/read access only."""
import argparse,datetime,hashlib,json
from pathlib import Path
from read_infrastructure import InfrastructureReader
from read_live import K
p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid capture name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False)
r=InfrastructureReader(a.pid)
try:
    result=dict(pid=a.pid,sha256=r.sha,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),infrastructure=r.infrastructure())
    ids={n['address']:n['route_id_candidate'] for d in result['infrastructure']['databases'] for n in d['nodes']}
    services={s['address']:s['service_id'] for s in result['infrastructure']['topology']['services']['entries'] if 'service_id' in s}
    junctions=[];vectors=[]
    for n in result['infrastructure']['topology']['nodes']:
        b=n['address']
        if n['kind']==2:
            owner=r.u(b+0x58);flags=r.unpack(b+0x4e,'H')[0]
            junctions.append(dict(address=b,route_id=ids[b],association=owner,service_id=services.get(owner),flags4e=flags,selected_branch=n['selected_branch'],association_stable=owner==r.u(b+0x58)))
        elif n['kind']==1:
            head=r.u(b+0x38);values=r.list_values(head,4096)
            vectors.append(dict(address=b,route_id=ids[b],list38=head,values=values,service_ids=[services.get(v) for v in values],byte34=r.read(b+0x34,1)[0],byte35=r.read(b+0x35,1)[0],list_pointer_stable=head==r.u(b+0x38)))
    result.update(junctions=junctions,vectors=vectors,sim_time_after=r.f(0x80acd4),paused_after=r.u(0x7be0f4),sources={},limitations='Non-atomic snapshot; unchanged clock/pointers do not prove coherent producer phase or absence of identity reuse. Field/list names remain structural; association is not automatically occupancy or movement authority.')
    for name in ('read_infrastructure_owners.py','read_infrastructure.py','read_topology.py','read_services.py','read_live.py'):
        data=(root/name).read_bytes();(out/name).write_bytes(data);result['sources'][name]=hashlib.sha256(data).hexdigest()
    (out/'owners.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(dict(output=str(out),sim_time=result['sim_time'],same_clock=result['sim_time']==result['sim_time_after'],junctions=len(junctions),associated_junctions=[x for x in junctions if x['association']],nonempty_vectors=[x for x in vectors if x['values']],unstable=sum(not x['association_stable'] for x in junctions)+sum(not x['list_pointer_stable'] for x in vectors))))
finally:K.CloseHandle(r.h)
