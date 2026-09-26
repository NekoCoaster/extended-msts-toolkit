"""Per-vehicle brake/force candidates, externally read without process writes."""
import argparse,json,datetime
from pathlib import Path
from read_live import Reader,K

def sample(r):
    out=[]
    for t in r.trains():
        row=dict(train_id=t['id'],is_player=t['is_player'],cars=[])
        for c in t['cars']:
            a=c['address'];d=c['definition'];b=c['body']
            x=dict(address=a,powered=c['powered'],derailed=c['derailed'],definition=d,body=b,links=c['links'])
            x['candidate_floats']={hex(off):r.f(a+off) for off in [0x1a0,0x1a8,0x1bc,0x224,0x228,0x22c,0x230,0x234,0x238]}
            x['definition_candidates']={hex(off):r.f(d+off) for off in [0x210,0x918,0x954]}
            x['body_force_candidate']=list(r.unpack(b+0xa0,'fff'));x['body_torque_candidate']=list(r.unpack(b+0xac,'fff'));x['inverse_inertia_world']=list(r.unpack(b+0x64,'9f'))
            x['body_pointer_stable']=r.u(a+0x5c)==b;row['cars'].append(x)
        out.append(row)
    return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args();root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        d=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),trains=sample(r));d['sim_time_after']=r.f(0x80acd4)
        for name in ['read_vehicle_systems.py','read_live.py']:(out/name).write_bytes((root/name).read_bytes())
        (out/'vehicles.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(output=str(out),examples=[{'train':t['train_id'],'first':t['cars'][0],'last':t['cars'][-1]} for t in d['trains']])))
    finally:K.CloseHandle(r.h)
