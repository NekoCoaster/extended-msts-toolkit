"""Bounded read-only hypothesis probe from native 0x60cd5c."""
from read_live import Reader, K
import argparse, json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
r=Reader(a.pid)
def wide(addr):
    data=r.read(addr,256);return data.decode('utf-16le',errors='replace').split('\0')[0]
try:
    manager=r.u(0x7bdecc);root=r.u(manager+0x20);table=r.u(0x828108)
    result=dict(manager=manager,root=root,table=table,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),trains=[])
    n=r.u(root);seen=set()
    while n and n!=root:
        if n in seen or len(seen)>=256:raise ValueError('Invalid registry')
        seen.add(n);nxt,prev,index=r.unpack(n,'III')
        if index>=100000:raise ValueError('Invalid table index')
        t=r.u(table+index*8);row=dict(node=n,index=index,address=t)
        try:
            row.update(id=r.u(t+0x10),kind_byte=r.read(t+0x5a,1)[0],first=r.u(t+0x62),last=r.u(t+0x66),lead=r.u(t+0x6a),
                       controller_wrapper=r.u(t+0x72),speed_raw=r.f(t+0x92),service_object=r.u(t+0xe6),is_player=t==r.u(0x7c2ac0))
            cars=[];car=row['first'];visited=set()
            while car:
                if car in visited or len(visited)>=256:raise ValueError('Invalid car chain')
                visited.add(car)
                c=dict(address=car,owner=r.u(car+0x98),definition=r.u(car+0x94),body=r.u(car+0x5c),next=r.u(car+0xa8))
                c['asset_directory']=wide(c['definition']+0xad0)
                try:c['physics']=r.car(car)
                except Exception as e:c['physics_error']=str(e)
                cars.append(c);car=c['next']
            row['cars']=cars
        except Exception as e:row['error']=str(e)
        result['trains'].append(row);n=nxt
    result['monitor_type_labels']=[wide(r.u(0x79f898+i*4)) for i in range(15)]
    out=Path(__file__).resolve().parent/'captures'/a.name;out.mkdir(exist_ok=False)
    (out/'registry.json').write_text(json.dumps(result,indent=2))
    (out/'probe.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({**{k:v for k,v in result.items() if k!='trains'},'trains':[{k:v for k,v in t.items() if k!='cars'}|{'car_count':len(t.get('cars',[])),'physics_errors':sum('physics_error' in c for c in t.get('cars',[]))} for t in result['trains']]}))
finally:K.CloseHandle(r.h)
