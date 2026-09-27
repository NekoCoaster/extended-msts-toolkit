"""Read-only bounded topology traversal; never operate or write a switch."""
import argparse,json,datetime,hashlib
from collections import deque,Counter
from pathlib import Path
from read_services import ServiceReader
from read_live import K

class TopologyReader(ServiceReader):
    def topology(self,additional_seeds=()):
        services=self.registry();seeds={s['service_id']:self.u(s['address']+0x4c) for s in services['entries']}
        todo=deque(x for x in seeds.values() if x);nodes={}
        todo.extend(x for x in additional_seeds if x)
        while todo:
            p=todo.popleft()
            if p in nodes:continue
            if len(nodes)>=10000:raise ValueError('Topology exceeded node bound')
            kind=self.u(p);row=dict(address=p,kind=kind,links=[]);nodes[p]=row
            if kind==1:
                row.update(raw_header=self.read(p,0x18).hex(),length=self.f(p+0x28),section_count=self.u(p+0x1c))
                section=self.u(p+0x18)
                if row['section_count'] and section:
                    row['first_section_signature']=dict(definition=self.unpack(section,'H')[0],tile=list(self.unpack(section+0x18,'ii')),offset=list(self.unpack(section+0x20,'fff')))
                for off in [8,16]:row['links'].append(dict(node=self.u(p+off),direction=self.unpack(p+off+4,'B')[0]))
            elif kind in [2,3]:
                a=self.u(p+12);b=self.u(p+16);pins=self.u(p+20)
                if a+b>64:raise ValueError('Endpoint pin count exceeded bound')
                row.update(input_count=a,output_count=b,pins=pins,raw_header=self.read(p,0x18).hex())
                for i in range(a+b):row['links'].append(dict(node=self.u(pins+8*i),direction=self.unpack(pins+8*i+4,'B')[0]))
                if kind==2:
                    selected=self.u(p+0x50);index=a+selected
                    row.update(selected_branch=selected,selected_pin_index=index,selection_in_bounds=index<a+b,selected_node=row['links'][index]['node'] if index<a+b else None)
            else:raise ValueError(f'Unknown node type {kind} at {p:#x}')
            todo.extend(v['node'] for v in row['links'] if v['node'])
        missing=[]
        for p,row in nodes.items():
            for link in row['links']:
                q=link['node']
                if q and p not in [v['node'] for v in nodes[q]['links']]:missing.append([p,q])
        return dict(services=services,seeds=seeds,nodes=list(nodes.values()),counts=dict(Counter(str(n['kind']) for n in nodes.values())),nonreciprocal_links=missing)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=TopologyReader(a.pid)
    try:
        result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pid=a.pid,sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),topology=r.topology())
        result['sim_time_after']=r.f(0x80acd4)
        for name in ['read_topology.py','read_services.py','read_live.py']:(out/name).write_bytes((root/name).read_bytes())
        (out/'topology.json').write_text(json.dumps(result,indent=2))
        print(json.dumps(dict(output=str(out),counts=result['topology']['counts'],nonreciprocal_links=len(result['topology']['nonreciprocal_links']),same_sim_time=result['sim_time']==result['sim_time_after'])))
    finally:K.CloseHandle(r.h)
