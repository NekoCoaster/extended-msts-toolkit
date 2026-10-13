"""Short bounded body accumulator series; external reads only, no solver-rate claim."""
import argparse,datetime,hashlib,json,math,struct,time
from pathlib import Path
from read_live import K
from read_physical_registry import PhysicalRegistryReader
from read_wheel_animation import sample as population

def sample(r):
    out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),clock=r.f(0x80acd4),paused=r.u(0x7be0f4),automatic_gate=r.u(0x809e1c),vehicles=[])
    base=population(r);out['population_available']=base['available'];out['manager_stable']=base.get('manager_stable',False)
    for v in base.get('vehicles') or []:
        row=dict(object_id=v['object_id'],car=v['address'],train=v.get('train'));out['vehicles'].append(row)
        try:
            if 'error' in v or not v['identity_stable']:raise ValueError('Unstable population input')
            car=v['address'];owner=r.u(car+0x98);body=r.u(car+0x5c)
            if not body or r.read(body+0xf0,1)!=b'\x01' or r.u(body+0x11d)!=car:raise ValueError('Body identity mismatch')
            raw=r.read(body+0x88,48);values=struct.unpack('<12f',raw)
            if not all(math.isfinite(x) for x in values):raise ValueError('Nonfinite body state')
            row.update(body=body,owner=owner,velocity=values[:3],angular_velocity=values[3:6],force=values[6:9],torque=values[9:12],raw=raw.hex(),state_stable=r.read(body+0x88,48)==raw,identity_stable=r.u(car+0x50)==v['object_id'] and r.u(car+0x98)==owner and r.u(car+0x5c)==body and r.u(body+0x11d)==car)
        except (ValueError,OSError) as e:row['error']=str(e)
    out['clock_after']=r.f(0x80acd4)
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=20);p.add_argument('--interval',type=float,default=.1);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not math.isfinite(a.seconds) or not 0<=a.seconds<=120 or not math.isfinite(a.interval) or a.interval<=0:p.error('Invalid name/timing')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=PhysicalRegistryReader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=a.interval,sources={},limitations='Sequential sampled accumulator values;no decomposition or solver cadence. Reject changed identity,state,manager,unavailable population and clock-crossing samples in comparisons. Equal guards cannot exclude ABA or stale producer data.')
        for name in ['read_body_accumulator_series.py','read_live.py','read_physical_registry.py','read_wheel_animation.py']:
            raw=(root/name).read_bytes();(out/name).write_bytes(raw);meta['sources'][name]=hashlib.sha256(raw).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2));start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w') as f:
            while True:
                try:row=sample(r);row['elapsed']=time.perf_counter()-start;line=json.dumps(row,allow_nan=False)
                except (OSError,ValueError) as e:line=json.dumps(dict(error=str(e),elapsed=time.perf_counter()-start));errors+=1
                f.write(line+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds or (out/'stop.request').exists():break
                time.sleep(a.interval)
        print(json.dumps(dict(samples=count,outer_errors=errors,output=str(out))))
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
