"""Bounded read-only pause/resume sampler; UI controls remain external."""
import argparse,json,time,datetime,hashlib
from pathlib import Path
from read_speed_caps import capture,ServiceReader,K
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=50);a=p.parse_args()
    if not 0<a.seconds<=120:p.error('Seconds must be in (0,120]')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
    try:
        hashes={}
        for name in ['capture_update_cadence.py','read_speed_caps.py','read_services.py','read_live.py']:
            b=(root/name).read_bytes();(out/name).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest()
        (out/'metadata.json').write_text(json.dumps(dict(pid=a.pid,sha256=r.sha,sources=hashes),indent=2))
        begin=time.perf_counter();count=0
        with (out/'samples.jsonl').open('w') as f:
            while time.perf_counter()-begin<a.seconds:
                row=dict(wall_elapsed=time.perf_counter()-begin)
                try:
                    row.update(capture(r));t=r.u(0x7c2ac0);s=r.u(t+0xea);n=r.u(0x7c2e88)
                    if n>4096:raise ValueError('Sound count bound')
                    table=r.u(s+12);row['train']=dict(address=t,speed=r.f(t+0x92),mass=r.f(t+0x9a),length=r.f(t+0xaa),elapsed_candidate=r.f(t+0xd6),distance_candidate=r.f(t+0xda),audio=[r.f(s),r.f(s+4),r.u(s+8)],audio_records=[list(r.unpack(table+i*12,'III')) for i in range(n)] if table else [])
                    row['end_sim_time']=r.f(0x80acd4)
                except (ValueError,OSError) as e:row['error']=str(e)
                f.write(json.dumps(row,allow_nan=False)+'\n');f.flush();count+=1;time.sleep(.1)
        print(json.dumps(dict(capture=str(out),samples=count)))
    finally:K.CloseHandle(r.h)
