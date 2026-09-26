"""External read-only current environment observation; no render calls or hooks."""
import argparse,json,datetime
from pathlib import Path
from read_live import Reader,K

class EnvironmentReader(Reader):
    def environment(self):
        e=self.u(0x7b6d60);p=self.u(e+0x34);w=self.u(e+0x38)
        result=dict(environment=e,precipitation_pointer=p,wind_pointer=w)
        if p:
            s=self.u(p+0x170)
            result['precipitation']=dict(flags=self.u(p),frame_count=self.u(p+4),system=s,density=self.u(p+0x174),radius=self.f(p+0x178),relative_height=self.f(p+0x17c),speed_parameter=self.f(p+0x180),animation_factor=self.f(p+0x184),reset=self.u(p+0x188))
            if s:
                n=self.u(s+0x8c);base=self.u(s+0x30)
                if n>16384:raise ValueError('Particle bound exceeded')
                histogram={}
                for i in range(n):
                    flags=self.unpack(base+i*0x30,'H')[0];histogram[str(flags)]=histogram.get(str(flags),0)+1
                result['particles']=dict(capacity=self.u(s+0x24),count=self.u(s+0x38),allocated_count=n,near_bias=self.f(s+0x54),flag_histogram=histogram,samples=[])
                for i in range(min(n,4)):
                    q=base+i*0x30;flags,frame=self.unpack(q,'HH')
                    result['particles']['samples'].append(dict(index=i,flags=flags,frame=frame,position=list(self.unpack(q+4,'fff')),size=self.f(q+0x10),argb=self.u(q+0x14),screen_timer=self.f(q+0x24)))
        if w:
            n=self.u(w);layers=self.u(w+4)
            if n>32:raise ValueError('Wind layer bound exceeded')
            result['wind']=dict(layer_count=n,active_vortices=self.u(w+8),layers=[list(self.unpack(layers+i*40,'10f')) for i in range(n)],vortices=[list(self.unpack(w+12+i*36,'9f')) for i in range(4)])
        fog=self.u(0x83d780);light=self.u(0x828798)
        result['lighting']=dict(ambient_rgb=list(self.unpack(0x828620,'fff')),ambient_packed=self.u(0x828794),directional_rgb=list(self.unpack(0x8287a0,'fff')),directional_light=light,direction=list(self.unpack(light+0x2c,'fff')) if light else None)
        if fog:result['fog']=dict(pointer=fog,start=self.f(fog+0x20),end=self.f(fog+0x24),scale=self.f(fog+0x30))
        result['environment_pointer_stable']=e==self.u(0x7b6d60)
        return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args();root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=EnvironmentReader(a.pid)
    try:
        data=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),environment=r.environment());data['sim_time_after']=r.f(0x80acd4)
        for name in ['read_environment.py','read_live.py']:(out/name).write_bytes((root/name).read_bytes())
        (out/'environment.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
    finally:K.CloseHandle(r.h)
