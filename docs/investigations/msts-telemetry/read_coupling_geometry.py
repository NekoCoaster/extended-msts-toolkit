"""Read-only endpoint geometry; derived distances are not signed slack/force."""
import argparse,datetime,json,math,shutil
from pathlib import Path
from read_live import Reader,K

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        data=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),trains=[],direction_epsilon=r.f(0x753e38),access='QUERY_LIMITED_INFORMATION | VM_READ')
        for t in r.trains():
            cars={}
            for c in t['cars']:
                addr=c['address'];d=c['definition'];length=r.f(d+0x400);vertical=r.f(d+0x414)
                x=dict(address=addr,body=c['body'],definition=d,links=c['links'],position=c['position'],right=c['right'],up=c['up'],forward=c['forward'],length=length,vertical_parameter=vertical,type_byte=r.read(d+0x1d4,1)[0],spring_raw_hex=r.read(d+0x1e4,0x2c).hex(),stored_force_magnitude=r.f(addr+0x1a0),break_threshold=r.f(d+0x210),endpoints=[])
                x['linear_velocity']=c['velocity'];x['angular_velocity']=c['angular_velocity']
                for sign in (-.5,.5):
                    local=[0,1-vertical,sign*length]
                    world=[c['position'][i]+sum(local[j]*c[k][i] for j,k in enumerate(('right','up','forward'))) for i in range(3)]
                    offset=[world[i]-c['position'][i] for i in range(3)];omega=c['angular_velocity']
                    cross=[omega[1]*offset[2]-omega[2]*offset[1],omega[2]*offset[0]-omega[0]*offset[2],omega[0]*offset[1]-omega[1]*offset[0]]
                    velocity=[c['velocity'][i]+cross[i] for i in range(3)]
                    x['endpoints'].append(dict(local=local,world=world,velocity=velocity))
                x['stable']=r.u(addr+0x5c)==c['body'] and r.u(addr+0x94)==d and r.u(addr+0x98)==t['address'] and list(r.unpack(addr+0xa0,'III'))[::2]==c['links']
                cars[addr]=x
            pairs=[]
            for c in cars.values():
                following=c['links'][1]
                if not following:continue
                if following not in cars:raise ValueError('Connected vehicle missing from train chain')
                other=cars[following];delta=[other['endpoints'][1]['world'][i]-c['endpoints'][0]['world'][i] for i in range(3)]
                distance=math.sqrt(sum(v*v for v in delta));direction=[v/distance for v in delta] if distance>data['direction_epsilon'] else [0,0,0]
                relative=[other['endpoints'][1]['velocity'][i]-c['endpoints'][0]['velocity'][i] for i in range(3)]
                pairs.append(dict(car=c['address'],next_car=following,reciprocal=other['links'][0]==c['address'],endpoint_delta=delta,endpoint_distance=distance,relative_endpoint_velocity=relative,separation_rate=sum(relative[i]*direction[i] for i in range(3)),stable=c['stable'] and other['stable']))
            data['trains'].append(dict(id=t['id'],is_player=t['is_player'],speed=t['speed_raw'],cars=list(cars.values()),pairs=pairs))
        data['sim_time_after']=r.f(0x80acd4)
        data['limitations']='Sequential reads; no solver-phase or atomicity claim. Double-precision reconstruction of native float/x87 path, not bit-exact. Endpoint distance is nonnegative and not signed slack. Stored force is not reconstructed or proven actual wheel/rail force. AI physical population and changed geometry need separate validation.'
        for n in ('read_coupling_geometry.py','read_live.py'):shutil.copy2(root/n,out/n)
        (out/'couplings.json').write_text(json.dumps(data,indent=2,allow_nan=False),encoding='utf-8')
        print(json.dumps(dict(output=str(out),sim_time=data['sim_time'],sim_time_after=data['sim_time_after'],paused=data['paused'],trains=[dict(id=t['id'],cars=len(t['cars']),pairs=len(t['pairs']),distance_range=[min((x['endpoint_distance'] for x in t['pairs']),default=None),max((x['endpoint_distance'] for x in t['pairs']),default=None)],unstable=sum(not x['stable'] for x in t['pairs'])) for t in data['trains']])))
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
