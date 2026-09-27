"""Read subtype fields supported by native serializer evidence; no process writes."""
import argparse,json,datetime
from pathlib import Path
from read_infrastructure import InfrastructureReader
from read_live import K
class ItemReader(InfrastructureReader):
    def items(self):
        infra=self.infrastructure();rows=[]
        for db in infra['databases']:
            for base in db['items']:
                p=base['address'];kind=base['kind'];row=dict(base)
                if kind!=9:row.update(node_distance=self.f(p+12),common_flags=self.u(p+16))
                if kind==3:
                    row['platform']=dict(station=self.wide(self.u(p+0x28)) if self.u(p+0x28) else None,name=self.wide(self.u(p+0x2c)) if self.u(p+0x2c) else None,flags=self.u(p+0x30),paired_item=self.u(p+0x34),minimum_wait=self.f(p+0x38),waiting_passengers=self.u(p+0x3c))
                elif kind==6:
                    row['siding']=dict(name=self.wide(self.u(p+0x14)) if self.u(p+0x14) else None,flags=self.u(p+0x18),paired_item=self.u(p+0x1c))
                elif kind==8:
                    row['speedpost']=dict(flags=self.unpack(p+0x28,'H')[0],byte_value=self.unpack(p+0x2a,'B')[0],float_value=self.f(p+0x2c),angle=self.f(p+0x30))
                rows.append(row)
        return rows
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args();root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ItemReader(a.pid)
    try:
        s=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),items=r.items());s['sim_time_after']=r.f(0x80acd4)
        for name in ['read_track_items.py','read_infrastructure.py','read_topology.py','read_services.py','read_live.py']:(out/name).write_bytes((root/name).read_bytes())
        (out/'items.json').write_text(json.dumps(s,indent=2));print(json.dumps(dict(output=str(out),items=len(s['items']),same_sim_time=s['sim_time']==s['sim_time_after'])))
    finally:K.CloseHandle(r.h)
