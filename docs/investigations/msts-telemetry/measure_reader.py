"""Bounded external read-cost measurement; no claim of in-game frame impact."""
import argparse,json,time,statistics
from pathlib import Path
from read_lifecycle import LifecycleReader
from read_live import K
class MeasuredReader(LifecycleReader):
    def read(self,a,n):
        self.read_calls=getattr(self,'read_calls',0)+1;self.read_bytes=getattr(self,'read_bytes',0)+n
        return super().read(a,n)
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args();root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=MeasuredReader(a.pid);rows=[]
try:
    for i in range(30):
        r.read_calls=r.read_bytes=0;wall=time.perf_counter();cpu=time.process_time();s=r.sample()
        rows.append(dict(wall_ms=(time.perf_counter()-wall)*1000,cpu_ms=(time.process_time()-cpu)*1000,read_calls=r.read_calls,read_bytes=r.read_bytes,same_sim_time=s['same_sim_time'],physical_cars=sum(len(t['cars']) for t in s['tracks']['trains']),services=len(s['services']['entries'])))
    result=dict(pid=a.pid,sha256=r.sha,samples=rows,wall_ms_median=statistics.median(x['wall_ms'] for x in rows),wall_ms_max=max(x['wall_ms'] for x in rows),crossed_step=sum(not x['same_sim_time'] for x in rows),limitation='External collector cost only, one machine and entity count; no game frame-time baseline or scheduling-impact comparison.')
    for name in ['measure_reader.py','read_lifecycle.py','read_services.py','read_track.py','read_live.py']:(out/name).write_bytes((root/name).read_bytes())
    (out/'measurement.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='samples'}))
finally:K.CloseHandle(r.h)
