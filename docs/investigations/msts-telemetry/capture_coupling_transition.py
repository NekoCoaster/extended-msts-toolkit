"""Read-only compact physical-registry, ownership and player-track series."""
import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from read_physical_registry import PhysicalRegistryReader
from read_track import TrackReader
from read_signals_cab import DetailReader
from read_live import K

class Reader(PhysicalRegistryReader, TrackReader, DetailReader):
    pass

def sample(r):
    row=r.details()
    row['origin']=list(r.unpack(0x79d118,'ii'))
    reg=r.physical_registry()
    row['registry']=dict(count=reg['stored_count'], count_after=reg['stored_count_after'],
                         roots_stable=reg['roots_stable'],trains=reg['trains'],
                         outside=reg['physical_not_in_train_chains'],missing=reg['train_cars_not_in_physical_list'])
    row['cars']=[dict(address=o['address'],id=o.get('object_id'),owner=o.get('owner'),kind=o['native_kind'],
                      stable=o['stable'],reciprocal=o['reciprocal_list_links'],
                      body=o['physics']['body'],links=o['physics']['links'],position=o['physics']['position'],
                      speed=o['physics']['longitudinal_speed'],body_stable=o['physics']['body_pointer_stable'])
                 for o in reg['objects'] if 'physics' in o]
    row['player_track']=r.track(row['player']['lead']+0x128)
    row['end_time']=r.f(0x80acd4)
    row['origin_stable']=row['origin']==list(r.unpack(0x79d118,'ii'))
    return row

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--pid',type=int,required=True)
    p.add_argument('--name',required=True)
    p.add_argument('--seconds',type=float,default=180)
    p.add_argument('--interval',type=float,default=.25)
    a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not all(math.isfinite(v) for v in (a.seconds,a.interval)) or not 0<=a.seconds<=600 or not .1<=a.interval<=10:p.error('Invalid bounds')
    root=Path(__file__).resolve().parent
    out=root/'captures'/a.name
    out.mkdir(exist_ok=False)
    r=Reader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,seconds=a.seconds,interval=a.interval,access='QUERY_LIMITED_INFORMATION | VM_READ',sources={},limitations='Sequential external reads. Races and errors retained; links/owners can change during capture. No pointer persistence guarantee.')
        for name in ('capture_coupling_transition.py','read_physical_registry.py','read_track.py','read_signals_cab.py','read_live.py'):
            data=(root/name).read_bytes();(out/name).write_bytes(data);meta['sources'][name]=hashlib.sha256(data).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2))
        start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w') as f:
            while True:
                begin=time.perf_counter()
                try:line=json.dumps(sample(r),allow_nan=False)
                except (OSError,ValueError) as e:line=json.dumps(dict(error=str(e),monotonic=begin));errors+=1
                f.write(line+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(max(0,a.interval-(time.perf_counter()-begin)))
        print(json.dumps(dict(output=str(out),samples=count,errors=errors)))
    finally:K.CloseHandle(r.h)
