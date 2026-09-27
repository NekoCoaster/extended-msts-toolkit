"""Short read-only series of native keyboard bits and transient buffer headers."""
import argparse,datetime,hashlib,json,shutil,struct,time
from pathlib import Path
from read_live import Reader,K
from read_input_bindings import capture
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=30);a=p.parse_args()
if Path(a.name).name!=a.name or not 0<a.seconds<=60:raise ValueError('Invalid bounds')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
    context=capture(r);keyboards=[d for d in context['devices'] if d.get('kind')==1]
    if len(keyboards)!=1:raise ValueError('Expected exactly one keyboard')
    k=keyboards[0];obj=k['input_object'];count=k['count'];bits_address=k['bits_address']
    (out/'context.json').write_text(json.dumps(context,indent=2));hashes={}
    for name in ['capture_keyboard_transition.py','read_input_bindings.py','read_live.py']:
        shutil.copy2(root/name,out/name);hashes[name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
    (out/'metadata.json').write_text(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),image_sha256=r.sha,seconds=a.seconds,requested_sleep_s=.005,probe_hashes=hashes),indent=2))
    start=time.perf_counter();samples=errors=0
    with (out/'samples.jsonl').open('w') as f:
        while time.perf_counter()-start<a.seconds:
            begin=time.perf_counter();row=dict(t=begin-start)
            try:
                if r.u(k['address']+4)!=obj or r.u(obj+0x24)!=bits_address:raise ValueError('Keyboard identity changed')
                head=r.read(obj+0xc,16);buffer,capacity,cursor,used=struct.unpack('<4I',head)
                if not 0<=cursor<=used<=capacity<=4096:raise ValueError('Invalid header/bounds')
                bits=r.read(bits_address,(count+7)//8)
                row.update(bits=bits.hex(),held=[i for i in range(count) if bits[i//8]&(1<<(i%8))],capacity=capacity,cursor=cursor,count=used,
                           records=[list(r.unpack(buffer+i*16,'4I')) for i in range(used)],stable_header=r.read(obj+0xc,16)==head,
                           stable_bits=r.read(bits_address,len(bits))==bits,paused=r.u(0x7be0f4),dayclock=r.f(0x80acd4))
            except (OSError,ValueError) as error:row['error']=str(error);errors+=1
            row['read_s']=time.perf_counter()-begin;f.write(json.dumps(row)+'\n');samples+=1;time.sleep(.005)
    print(json.dumps(dict(samples=samples,errors=errors,elapsed=time.perf_counter()-start)))
finally:K.CloseHandle(r.h)
