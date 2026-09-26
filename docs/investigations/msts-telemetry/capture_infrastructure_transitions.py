"""Bounded query/read-only infrastructure transition series; no native calls/writes."""
import argparse,datetime,hashlib,json,math,time
from pathlib import Path
from read_infrastructure import InfrastructureReader
from read_live import K
def sample(r):
    row=dict(monotonic=time.perf_counter(),sim_time=r.f(0x80acd4),elapsed=r.f(0x80acd0),paused=r.u(0x7be0f4))
    infra=r.infrastructure();ids={n['address']:n['route_id_candidate'] for d in infra['databases'] for n in d['nodes']}
    row['node_map']=ids;row['services']=infra['topology']['services'];row['presence']=infra['vector_presence']
    row['signals']=[i for d in infra['databases'] for i in d['items'] if i['kind']==0]
    row['junctions']=[];row['vectors']=[]
    for n in infra['topology']['nodes']:
        p=n['address']
        if n['kind']==2:
            owner=r.u(p+0x58)
            row['junctions'].append(dict(address=p,route_id=ids[p],branch=n['selected_branch'],owner=owner,flags=r.unpack(p+0x4e,'H')[0],owner_stable=owner==r.u(p+0x58)))
        elif n['kind']==1:
            head=r.u(p+0x38);values=r.list_values(head,4096)
            row['vectors'].append(dict(address=p,route_id=ids[p],constraint=r.read(p+0x34,1)[0],state=r.read(p+0x35,1)[0],services=values,list_stable=head==r.u(p+0x38)))
    row['trains']=[dict(id=t['id'],address=t['address'],is_player=t['is_player'],speed=t['speed_raw'],service=t['service_object'],cars=len(t['cars']),derailed=sum(bool(c['derailed']) for c in t['cars'])) for t in r.trains()]
    row.update(sim_time_after=r.f(0x80acd4),elapsed_after=r.f(0x80acd0),paused_after=r.u(0x7be0f4),monotonic_after=time.perf_counter())
    return row
def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=120);p.add_argument('--interval',type=float,default=.5);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not all(math.isfinite(x) for x in (a.seconds,a.interval)) or not 0<=a.seconds<=600 or not .1<=a.interval<=10:p.error('Invalid capture bounds')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=InfrastructureReader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=a.interval,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sources={},access='QUERY_LIMITED_INFORMATION | VM_READ',limitations='Full registry traversed each sample;non-atomic reads. Null/lists may race;errors preserved. Pointer rereads do not prove field/list coherence. Route IDs must retain build provenance.')
        for n in ('capture_infrastructure_transitions.py','read_infrastructure.py','read_topology.py','read_services.py','read_live.py'):
            b=(root/n).read_bytes();(out/n).write_bytes(b);meta['sources'][n]=hashlib.sha256(b).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
            while True:
                begin=time.perf_counter()
                try:line=json.dumps(sample(r),allow_nan=False)
                except (OSError,ValueError) as e:line=json.dumps(dict(error=str(e),monotonic=begin));errors+=1
                f.write(line+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(max(0,a.interval-(time.perf_counter()-begin)))
        print(json.dumps(dict(output=str(out),samples=count,errors=errors)))
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
