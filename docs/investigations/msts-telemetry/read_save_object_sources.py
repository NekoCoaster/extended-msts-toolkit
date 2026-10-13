"""Read-only source snapshot for physical-object save writers; never serializes game state."""
import argparse, datetime, hashlib, json, shutil
from pathlib import Path
from read_live import Reader, K

p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid name')
root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
    trains=r.trains();rows=[]
    def raw(address,size):
        data=r.read(address,size)
        return dict(address=address,size=size,hex=data.hex(),stable=data==r.read(address,size))
    def ref(base,offset,target_offset):
        ptr=r.u(base+offset)
        return dict(offset=hex(offset),pointer=ptr,saved_word=r.u(ptr+target_offset) if ptr else 0xffffffff,
                    stable=r.u(base+offset)==ptr)
    for train in trains:
        t=train['address'];row=dict(address=t,id=train['id'],is_player=train['is_player'],
            raw=raw(t+0x10,0xe2),references=[ref(t,o,0x50) for o in [0x62,0x66,0x6a,0x6e]],
            service=ref(t,0xe6,0x40),controller_present=bool(r.u(t+0x72)),cars=[])
        for car in train['cars']:
            c=car['address'];body=car['body']
            cr=dict(address=c,id=r.u(c+0x50),wagon_raw=raw(c+0x7c,0x216),body_raw=raw(body+4,0x191),
                    references=[ref(c,0xac,0x50),ref(c,0x1f8,0x40),ref(c,0x240,0x50)],
                    static_flags=r.u(c+0x18),saved_static_flags=r.u(c+0x18)&0x3fe3c0)
            if car['powered']:
                ed=car['engine_definition'];cr['engine_raw']=raw(c+0x292,0x36c);cr['subobjects']=[]
                for off in [0x4ba,0x4fa,0x53a,0x57a]:
                    ptr=r.u(c+off+0x3c)
                    indices=[i for i in range(4) if ptr==ed+0xb0c+i*0x6c]
                    index=indices[0] if indices else 0xffffffff if not ptr else None
                    cr['subobjects'].append(dict(offset=hex(off),raw=raw(c+off+4,0x3c),definition_pointer=ptr,
                        saved_definition_index=index,writer_would_reject=index is None,stable=r.u(c+off+0x3c)==ptr))
            row['cars'].append(cr)
        rows.append(row)
    result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),image_sha256=r.sha,trains=rows,
                registry_stable=[t['address'] for t in trains]==[t['address'] for t in r.trains()],
                paused=r.u(0x7be0f4),dayclock=r.f(0x80acd4),
                limitations='Source memory only, not emitted SAV bytes. Raw spans include pointers and overlapping subobjects; no portable schema or atomicity. No object writer or loader invoked.')
    (out/'sources.json').write_text(json.dumps(result,indent=2));hashes={}
    for name in ['read_save_object_sources.py','read_live.py']:
        shutil.copy2(root/name,out/name);hashes[name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
    (out/'probe-hashes.json').write_text(json.dumps(hashes,indent=2))
    print(json.dumps(dict(trains=len(rows),cars=sum(len(t['cars']) for t in rows),paused=result['paused'],dayclock=result['dayclock'],registry_stable=result['registry_stable'],subobjects=[c['subobjects'] for t in rows for c in t['cars'] if 'subobjects' in c]),indent=2))
finally:K.CloseHandle(r.h)
