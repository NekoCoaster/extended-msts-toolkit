"""Bounded external manual-boarding inputs. No writes or native function calls.
Model is conditional on native geometry gates; sequential snapshots are not onset proof.
"""
import argparse,datetime,hashlib,json,math,shutil,struct,time
from pathlib import Path
from read_live import Reader,K

def sample(r):
    activity=0x809810; service=activity+0x80
    out=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),clock=r.f(0x80acd4),paused=r.u(0x7be0f4),automatic_gate=r.u(0x809e1c),request=r.u(activity+0x36c),active=r.u(activity+0x370),remaining=r.f(activity+0x374),stored_fraction=r.f(activity+0x364),speed=r.f(service+0x138),vehicles=[])
    selected=r.u(service+0x34);train=r.u(service+0x158)
    out.update(selected=selected,train=train)
    if not selected or not train:
        out['available']=False;return out
    sentinel=r.u(0x80a10c);node=r.u(sentinel)
    if not node or node==sentinel:raise ValueError('No first route database')
    db=r.u(node+8);collection=r.u(db+0x20);array=r.u(collection);size=r.u(collection+8)
    if size>100000:raise ValueError('Item table bound')
    platform_id=r.u(selected)
    def endpoint(index):
        if index>=size:raise ValueError('Platform index outside table')
        p=r.u(array+4*index)
        if not p or r.u(p)!=3:raise ValueError('Selected item is not platform')
        return dict(index=index,address=p,distance=r.f(p+12),pair=r.u(p+0x34),waiting=r.u(p+0x3c),minimum_wait=r.f(p+0x38))
    first=endpoint(platform_id);second=endpoint(first['pair']);out['endpoints']=[first,second]
    car=r.u(train+0x62);head=car;seen=set()
    while car:
        if car in seen or len(seen)>=512:raise ValueError('Vehicle list cycle/bound')
        seen.add(car);definition=r.u(car+0x94);track=r.u(car+0x128);nxt=r.u(car+0xa8)
        kind=r.unpack(definition+0x88,'B')[0];capacity=r.f(definition+0xc08);position=r.f(car+0x138)
        items=r.u(track+0x20);count=r.u(track+0x24)
        if count>10000:raise ValueError('Vehicle item array bound')
        pointers=list(r.unpack(items,'I'*count)) if count else []
        eligible=kind==3 or capacity>0
        membership=first['address'] in pointers or second['address'] in pointers
        inside=min(first['distance'],second['distance'])<position<max(first['distance'],second['distance'])
        stable=(r.u(car+0x94)==definition and r.u(car+0x128)==track and r.u(car+0xa8)==nxt and r.u(track+0x20)==items and r.u(track+0x24)==count)
        out['vehicles'].append(dict(address=car,definition=definition,kind=kind,capacity_field=capacity,position=position,item_pointers=pointers,eligible=eligible,membership=membership,inside=inside,contributes=eligible and membership and inside,pointers_stable=stable))
        car=nxt
    eligible=sum(x['eligible'] for x in out['vehicles']);contributing=sum(x['contributes'] for x in out['vehicles'])
    out.update(available=True,eligible_count=eligible,contributing_count=contributing,conditional_fraction=contributing/eligible if eligible else None,conditional_duration=struct.unpack('<f',struct.pack('<f',10*second['waiting']/contributing))[0] if contributing else None)
    out['guards']=dict(selection=r.u(service+0x34)==selected,train=r.u(service+0x158)==train,head=r.u(train+0x62)==head,database_root=r.u(0x80a10c)==sentinel,database_node=r.u(sentinel)==node,database=r.u(node+8)==db,collection=r.u(db+0x20)==collection,array=r.u(collection)==array,size=r.u(collection+8)==size,platform=r.u(selected)==platform_id,endpoints=all(r.u(array+4*x['index'])==x['address'] for x in [first,second]))
    out['clock_after']=r.f(0x80acd4)
    out['comparison_guards_pass']=all(out['guards'].values()) and all(v['pointers_stable'] for v in out['vehicles']) and out['clock']==out['clock_after']
    if not out['comparison_guards_pass']:
        for field in ['eligible_count','contributing_count','conditional_fraction','conditional_duration']:
            out[field]=None
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=0);p.add_argument('--interval',type=float,default=.1);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not math.isfinite(a.seconds) or a.seconds<0 or not math.isfinite(a.interval) or a.interval<=0:p.error('Invalid output/timing')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        sources={}
        for name in ['read_manual_loading_inputs.py','read_live.py']:
            shutil.copyfile(root/name,out/name);sources[name]=hashlib.sha256((root/name).read_bytes()).hexdigest()
        (out/'metadata.json').write_text(json.dumps(dict(pid=a.pid,sha256=r.sha,sources=sources,limitations='First database/index join from inspected build. Conditional model uses paired endpoint waiting count per0058782c caller mapping; earlier geometry gates remain unvalidated; no atomicity, door geometry or onset execution proof. Pointer rereads cannot exclude reuse or contents changing in place.'),indent=2))
        start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w') as f:
            while True:
                try:line=json.dumps(sample(r),allow_nan=False)
                except (ValueError,OSError) as e:line=json.dumps(dict(error=str(e)));errors+=1
                f.write(line+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds or (out/'stop.request').exists():break
                time.sleep(a.interval)
        print(json.dumps(dict(samples=count,errors=errors,output=str(out))))
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
