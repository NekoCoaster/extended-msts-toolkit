"""Read-only corroboration of service class bits against physical car definitions."""
import argparse, collections, hashlib, json
from pathlib import Path
from read_services import ServiceReader, K
from binary_fields import PE

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
    try:
        pe=PE();start=r.f(0x80acd4);trains=[]
        for train in r.trains():
            cars=[dict(address=c['address'],definition=c['definition'],type=r.read(c['definition']+0x88,1)[0]) for c in train['cars']]
            bits=r.u(train['service_object'])&6
            expected=4 if any(c['type']==2 for c in cars) else 2
            trains.append(dict(address=train['address'],service=train['service_object'],cars=cars,class_bits=bits,expected_from_current_cars=expected,matches=bits==expected))
        tokens=[]
        for address in [0x795448,0x795450]:
            pointer=pe.u(address);token=pe.u(address+4);raw=pe.read(address,8)
            tokens.append(dict(address=address,string_pointer=pointer,name=pe.string(pointer),token=token,disk_hex=raw.hex(),live_matches=r.read(address,8)==raw and r.read(pointer,len(pe.string(pointer).encode('utf-16le'))+2)==pe.read(pointer,len(pe.string(pointer).encode('utf-16le'))+2)))
        result=dict(pid=a.pid,sha256=r.sha,sim_time=start,sim_time_after=r.f(0x80acd4),paused=r.u(0x7be0f4),trains=trains,tokens=tokens,limitation='Physical consists only; class selection is traced at initialization, not proved to refresh after coupling changes.')
        (out/'snapshot.json').write_text(json.dumps(result,indent=2))
        hashes={}
        for name in ['probe_service_class.py','read_services.py','read_live.py','binary_fields.py']:
            data=(root/name).read_bytes();(out/name).write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
        (out/'sources.json').write_text(json.dumps(hashes,indent=2))
        print(json.dumps(dict(trains=[dict(class_bits=t['class_bits'],counts=dict(collections.Counter(c['type'] for c in t['cars'])),matches=t['matches']) for t in trains],tokens=tokens,same_sim_time=result['sim_time']==result['sim_time_after'],paused=result['paused'])))
    finally:K.CloseHandle(r.h)
