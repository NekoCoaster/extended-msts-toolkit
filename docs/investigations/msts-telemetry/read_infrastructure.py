"""Bounded read-only route registries, signal association and vector presence lists."""
import argparse,json,datetime
from pathlib import Path
from collections import Counter
from read_topology import TopologyReader
from read_live import K

class InfrastructureReader(TopologyReader):
    def list_values(self,root,limit):
        if not root:return []
        n=self.u(root);seen=set();values=[]
        while n!=root:
            if not n or n in seen or len(seen)>=limit:raise ValueError('List bound/cycle')
            seen.add(n);values.append(self.u(n+8));n=self.u(n)
        return values
    def infrastructure(self):
        databases=[];allnodes=[]
        for db in self.list_values(self.u(0x80a10c),32):
            table=self.u(db);last=self.u(db+12)
            if last>=10000:raise ValueError('Node table bound')
            nodes=[dict(index=i,route_id_candidate=i+1,address=self.u(table+4*i)) for i in range(last+1)]
            allnodes.extend(n['address'] for n in nodes if n['address'])
            collection=self.u(db+0x20);items=[]
            if collection:
                array=self.u(collection);count=self.u(collection+8)
                if count>100000:raise ValueError('Track-item bound')
                for i in range(count):
                    p=self.u(array+i*4)
                    if not p:continue
                    row=dict(index=i,address=p,kind=self.u(p))
                    if row['kind']==0:
                        row.update(flags=self.u(p+0x1c),direction=self.unpack(p+0x20,'B')[0],aspect=self.unpack(p+0x21,'B')[0],associated_service=self.u(p+0x24),definition=self.u(p+0x14))
                    items.append(row)
            databases.append(dict(address=db,nodes=nodes,items=items,item_kind_counts=dict(Counter(str(i['kind']) for i in items))))
        topology=self.topology(allnodes);presence=[]
        for n in topology['nodes']:
            if n['kind']!=1:continue
            entries=[]
            for p in self.list_values(self.u(n['address']+0x2c),4096):
                entries.append(dict(address=p,track_node=self.u(p),node_distance=self.f(p+4),configuration_reference=self.u(p+8),service=self.u(p+12)))
            if entries:presence.append(dict(node=n['address'],entries=entries))
        return dict(databases=databases,topology=topology,vector_presence=presence)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=InfrastructureReader(a.pid)
    try:
        result=dict(pid=a.pid,sha256=r.sha,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),infrastructure=r.infrastructure())
        result['sim_time_after']=r.f(0x80acd4)
        for name in ['read_infrastructure.py','read_topology.py','read_services.py','read_live.py']:(out/name).write_bytes((root/name).read_bytes())
        (out/'infrastructure.json').write_text(json.dumps(result,indent=2));i=result['infrastructure']
        print(json.dumps(dict(output=str(out),counts=i['topology']['counts'],item_kinds=[d['item_kind_counts'] for d in i['databases']],presence_nodes=len(i['vector_presence']),presence_entries=sum(len(v['entries']) for v in i['vector_presence']))))
    finally:K.CloseHandle(r.h)
