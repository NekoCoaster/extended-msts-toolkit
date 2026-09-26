"""Combined read-only body/definition/track/timing inputs for motion experiments."""
import argparse,datetime,hashlib,json,math,shutil,time
from pathlib import Path
from read_track import TrackReader
from read_live import K

def sample(r):
    out=dict(monotonic=time.perf_counter(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=r.f(0x80acd4),elapsed_clock=r.f(0x80acd0),frame_dt=r.f(0x828fb4),time_scale=r.f(0x80acd8),paused=r.u(0x7be0f4),origin_tile=list(r.unpack(0x79d118,'ii')),trains=r.trains())
    for t in out['trains']:
        a=t['address'];s=t['service_object']
        t['elapsed_accumulator']=r.f(a+0xd6);t['distance_accumulator']=r.f(a+0xda)
        t['service_speed']=r.f(s+0x138);t['service_track']=r.track(s+0x4c)
        for c in t['cars']:
            p=c['address'];d=c['definition']
            c['length']=r.f(d+0x400);c['vertical_parameter']=r.f(d+0x414)
            c['coupling_type']=r.read(d+0x1d4,1)[0];c['spring_raw_hex']=r.read(d+0x1e4,0x2c).hex()
            c['connection_force_magnitude']=r.f(p+0x1a0);c['car_flags84']=r.u(p+0x84)
            c['stored_velocity']=r.f(p+0x1bc);c['stored_acceleration']=r.f(p+0x1c0)
            c['track']=r.track(p+0x128)
            c['body_pointer_stable_after']=r.u(p+0x5c)==c['body']
            c['definition_stable']=r.u(p+0x94)==d
            c['links_stable']=list(r.unpack(p+0xa0,'III'))[::2]==c['links']
            c['owner_stable']=r.u(p+0x98)==a
        t['service_stable']=r.u(a+0xe6)==s
    out['origin_stable']=list(r.unpack(0x79d118,'ii'))==out['origin_tile']
    out['sim_time_after']=r.f(0x80acd4);out['elapsed_clock_after']=r.f(0x80acd0)
    out['monotonic_after']=time.perf_counter()
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=60);p.add_argument('--interval',type=float,default=.1);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not all(math.isfinite(v) for v in (a.seconds,a.interval)) or not 0<=a.seconds<=600 or not .02<=a.interval<=10:p.error('Invalid name/timing bounds')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=TrackReader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=a.interval,access='QUERY_LIMITED_INFORMATION | VM_READ',sources={},limitations='Sequential external reads,not atomic or phase-aligned. Valid pointers do not exclude reuse. Samples carry beginning/end clocks and read duration. Origin and track fields need their existing semantic qualifications. No writes or remote function calls.')
        for n in ('capture_motion_context.py','read_track.py','read_live.py'):
            shutil.copy2(root/n,out/n);meta['sources'][n]=hashlib.sha256((root/n).read_bytes()).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
            while True:
                begin=time.perf_counter()
                try:row=sample(r);line=json.dumps(row,allow_nan=False)
                except (OSError,ValueError) as e:line=json.dumps(dict(error=str(e),monotonic=begin));errors+=1
                f.write(line+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(max(0,a.interval-(time.perf_counter()-begin)))
        print(json.dumps(dict(output=str(out),samples=count,errors=errors)))
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
