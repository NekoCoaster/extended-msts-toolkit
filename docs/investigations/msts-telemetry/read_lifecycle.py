"""Read-only combined service/track capture across scheduled traffic changes."""
import argparse,json,time,datetime,hashlib
from pathlib import Path
from read_services import ServiceReader
from read_track import TrackReader
from read_live import K
class LifecycleReader(ServiceReader,TrackReader):
    def sample(self):
        out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=self.f(0x80acd4),paused=self.u(0x7be0f4))
        out['services']=self.registry()
        for row in out['services']['entries']:
            try:row['track']=self.track(row['address']+0x4c)
            except (OSError,ValueError) as e:row['track_error']=str(e)
        out['tracks']=self.tracks();out['sim_time_after']=self.f(0x80acd4);out['same_sim_time']=out['sim_time']==out['sim_time_after']
        return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=540);p.add_argument('--interval',type=float,default=1);a=p.parse_args()
    if a.seconds<0 or a.interval<=0:p.error('Invalid timing')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=LifecycleReader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=a.interval,sources={},access='QUERY_LIMITED_INFORMATION | VM_READ')
        for name in ['read_lifecycle.py','read_services.py','read_track.py','read_live.py']:
            b=(root/name).read_bytes();(out/name).write_bytes(b);meta['sources'][name]=hashlib.sha256(b).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2));start=time.perf_counter();count=errors=0
        with (out/'lifecycle.jsonl').open('w') as f:
            while True:
                try:s=r.sample()
                except (OSError,ValueError) as e:s=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),error=str(e));errors+=1
                f.write(json.dumps(s,allow_nan=False)+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(a.interval)
        print(json.dumps(dict(output=str(out),samples=count,errors=errors,final_sim_time=s.get('sim_time'))))
    finally:K.CloseHandle(r.h)
