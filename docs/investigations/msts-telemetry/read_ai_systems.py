"""Paired service/physical vehicle observations; read-only and non-atomic."""
import argparse, datetime, hashlib, json, math, shutil, time
from pathlib import Path
from read_services import ServiceReader
from read_live import K

def sample(r):
    row=dict(sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),trains=[])
    row['service_registry']=r.registry()
    for t in r.trains():
        a=t['address'];s=t['service_object']
        x={k:t[k] for k in ('address','id','is_player','kind_byte','speed_raw','lead','service_object')}
        x['service']=dict(speed=r.f(s+0x138),target=r.f(s+0x13c),acceleration=r.f(s+0x140),physicalized=r.u(s+0x134),train=r.u(s+0x158))
        x['cars']=[]
        for c in t['cars']:
            p=c['address'];d=c['definition'];b=c['body']
            v={k:c[k] for k in ('address','powered','definition','body','derailed','links')}
            v['flags84']=r.u(p+0x84)
            v['fields']={hex(o):r.f(p+o) for o in (0x1bc,0x1c0,0x198,0x19c,0x224,0x228,0x22c,0x230,0x234,0x238,0x268)}
            v['brake_definition']={hex(o):r.f(d+o) for o in (0x918,0x954)}
            if c['powered']:
                v['engine_kind']=r.read(c['engine_definition']+0x88,1)[0]
                v['powered_fields']={hex(o):r.f(p+o) for o in (0x29e,0x2a2,0x2c2)}
            v['stable']=r.u(p+0x98)==a and r.u(p+0x5c)==b and r.u(p+0x94)==d and r.u(b+0x11d)==p
            x['cars'].append(v)
        x['service_stable']=r.u(a+0xe6)==s and r.u(s+0x158)==a
        x['chain_stable']=r.u(a+0x62)==t['cars'][0]['address'] and all(list(r.unpack(c['address']+0xa0,'III'))[::2]==c['links'] for c in t['cars']) if t['cars'] else r.u(a+0x62)==0
        row['trains'].append(x)
    row['sim_time_after']=r.f(0x80acd4)
    return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=60);p.add_argument('--interval',type=float,default=.1);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not math.isfinite(a.seconds) or not math.isfinite(a.interval) or a.seconds<0 or a.interval<=0:p.error('Invalid capture name or timing')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=a.interval,access='QUERY_LIMITED_INFORMATION | VM_READ',warning='Sequential non-atomic reads. Stable pointers do not exclude reuse. Powered+2c2 is type-dependent, not universally current.',sources={})
        for name in ('read_ai_systems.py','read_services.py','read_live.py'):
            shutil.copy2(root/name,out/name);meta['sources'][name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
        start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
            while True:
                try:
                    row=sample(r);row['elapsed']=time.perf_counter()-start
                    line=json.dumps(row,allow_nan=False)
                except (OSError,ValueError) as e:
                    line=json.dumps(dict(error=str(e),elapsed=time.perf_counter()-start));errors+=1
                f.write(line+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(a.interval)
        print(json.dumps(dict(output=str(out),samples=count,errors=errors)))
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
