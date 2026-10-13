"""Read electric player brake selector state and loaded ranges; no process writes."""
import argparse,datetime,hashlib,json,struct
from pathlib import Path
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid capture name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
    t=r.u(0x7c2ac0);lead=r.u(t+0x6a);d=r.u(lead+0x29a);wrapper=r.u(t+0x72)
    if r.u(0x7b6438)!=3 or r.u(wrapper)!=3 or r.read(d+0x88,1)[0]!=2:raise ValueError('Tested electric player required')
    ctl=r.u(wrapper+8);v=list(r.unpack(d+0x452,'42f'));h=r.f(lead+0x406);mode=r.u(lead+0x3f2);fraction=r.f(lead+0x3f6)
    modes=[1,2,4,8,0x10,0x20,0x40,0x80,0x100,0x200,0x4000,0x8000,0x400,0x800,0x1000,0x2000,0x10000,0x20000,0x40000,0x80000]
    ranges=[dict(mode=hex(m),start=v[1+2*i],end=v[2+2*i],enabled=v[1+2*i]!=-1,contains=v[1+2*i]!=-1 and v[1+2*i]<=h<v[2+2*i]) for i,m in enumerate(modes)]
    predicted=next((int(x['mode'],16) for x in ranges if x['contains']),0x100000 if v[41]!=-1 and h>=v[41] else 0x200000) if v[0]==-1 else 0
    asset=Path('C:/MSTS/TRAINS/TRAINSET/ACELA/acela.eng');data=asset.read_bytes();text=data.decode('utf-16') if data[:2] in (b'\xff\xfe',b'\xfe\xff') else data.decode('utf-8-sig');declarations=[x.strip() for x in text.splitlines() if 'Notch (' in x and 'TrainBrakesController' in x]
    result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),train=t,lead=lead,definition=d,controller=ctl,controller_handle=r.f(ctl+0x128),copied_handle=h,selected_mode=hex(mode),selected_fraction=fraction,train_pipe_command_pressure=r.f(lead+0x40a),table_first=v[0],ranges=ranges,terminal_emergency_start=v[41],predicted_mode=hex(predicted),mode_matches=mode==predicted,asset_path=str(asset),asset_sha256=hashlib.sha256(data).hexdigest(),declarations=declarations,identity_stable=r.u(0x7c2ac0)==t and r.u(t+0x6a)==lead and r.u(lead+0x29a)==d,limitations='Acela asset declarations corroborate observed loaded ranges, not a general filename resolver. Single paused electric read; continuous-curve mode and AI unvalidated. Native selector ordering retained; no remote calls.')
    (out/'selector.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    for f in ('read_brake_selector.py','read_live.py'):(out/f).write_bytes((root/f).read_bytes())
    print(json.dumps({k:v for k,v in result.items() if k not in ('ranges','declarations')}))
finally:K.CloseHandle(r.h)
