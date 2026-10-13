"""Bounded read-only body accumulator observation; no contact-event inference."""
import argparse,datetime,hashlib,json,struct,time,math
from pathlib import Path
from read_live import Reader,K

def sample(r):
    before=r.f(0x80acd4);trains=r.trains();rows=[]
    for t in trains:
        for c in t['cars']:
            a,b=c['address'],c['body']
            if not b or r.read(b+0xf0,1)!=b'\x01' or r.u(b+0x11d)!=a:raise ValueError('Body identity mismatch')
            raw=r.read(b+0xf2,7)
            flags,count,aggregate44,aggregate40,aggregate42=struct.unpack('<BBBHH',raw)
            rows.append(dict(train=t['address'],player=t['is_player'],car=a,body=b,flags_f2=flags,record_count_f3=count,sum_record44_f4=aggregate44,sum_record40_f5=aggregate40,sum_record42_f7=aggregate42,stable=raw==r.read(b+0xf2,7) and r.u(a+0x5c)==b and r.u(b+0x11d)==a and r.u(a+0x98)==t['address']))
    return dict(day=before,day_after=r.f(0x80acd4),paused=r.u(0x7be0f4),rows=rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=10);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not math.isfinite(a.seconds) or not 0<=a.seconds<=120:p.error('Invalid name or duration')
    out=Path(__file__).resolve().parent/'captures'/a.name;out.mkdir(exist_ok=False)
    for source in (Path(__file__),Path(__file__).with_name('read_live.py')):(out/source.name).write_bytes(source.read_bytes())
    r=Reader(a.pid);count=errors=0;start=time.perf_counter()
    try:
        (out/'metadata.json').write_text(json.dumps(dict(pid=a.pid,sha256=r.sha,access='QUERY_LIMITED_INFORMATION | VM_READ',limits='Sequential non-atomic reads. Byte/word accumulators reset each preparation pass and can wrap. Not lifetime collision counts or confirmed contact events.'),indent=2),encoding='utf-8')
        with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
            while True:
                try:x=sample(r)
                except (OSError,ValueError) as e:x=dict(error=str(e));errors+=1
                f.write(json.dumps(x)+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(.1)
        print(json.dumps(dict(samples=count,errors=errors,output=str(out))))
    finally:K.CloseHandle(r.h)
