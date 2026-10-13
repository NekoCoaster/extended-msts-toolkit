"""Read cached consist inputs; never call the native lazy definition resolver."""
import argparse, hashlib, json, math, struct
from pathlib import Path
from read_live import Reader,K
from read_track_interaction_records import sample,nodes

f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]

def capture(r):
    interactions=sample(r)
    result=dict(clock=r.f(0x80acd4),paused=r.u(0x7be0f4),interaction_guards=interactions['guards_pass'],services=[])
    player=r.u(0x7c2ac0)
    for service in sorted({v['service'] for v in interactions['records']}):
        root=r.u(service+0x12c);head=r.u(root);stored=r.f(service+0x128);train=r.u(service+0x158)
        row=dict(service=service,train=train,player=bool(train and train==player),stored=stored,definitions=[])
        result['services'].append(row);total=0.0;stable=True
        for node,nxt,prev,entry in nodes(r,root,512):
            cache=r.u(entry+8);definition=r.u(cache)
            if not definition:raise ValueError('Definition cache unresolved; native calls forbidden')
            flags=r.read(definition+0x1e4,2);length=r.read(definition+0x400,4);extra=r.read(definition+0x208,4)
            value=struct.unpack('<f',length)[0];addition=struct.unpack('<f',extra)[0]
            if not math.isfinite(value) or not math.isfinite(addition):raise ValueError('Nonfinite definition input')
            eligible=bool(flags[0] and flags[1]&0x10)
            total=f32(total+value)
            if eligible:total=f32(total+addition)
            good=(r.u(entry+8)==cache and r.u(cache)==definition and r.read(definition+0x1e4,2)==flags and r.read(definition+0x400,4)==length and r.read(definition+0x208,4)==extra and r.unpack(node,'III')==(nxt,prev,entry))
            stable &= good
            row['definitions'].append(dict(definition=definition,cache=cache,length=value,extra=addition,flags=list(flags),extra_selected=eligible,partial_sum=total,stable=good))
        row['guards_pass']=bool(stable and r.u(service+0x12c)==root and r.u(root)==head and r.f(service+0x128)==stored and r.u(service+0x158)==train)
        row['model']=total;row['matches']=total==stored
    result['clock_after']=r.f(0x80acd4)
    result['guards_pass']=bool(result['interaction_guards'] and result['clock']==result['clock_after'] and r.u(0x7c2ac0)==player and all(s['guards_pass'] for s in result['services']))
    if not result['guards_pass']:
        for row in result['services']:row['model']=None;row['matches']=None
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid capture name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        result=capture(r);result.update(pid=a.pid,image_sha256=r.sha,sources={})
        for name in ('read_interaction_threshold_inputs.py','read_track_interaction_records.py','read_live.py'):
            raw=(root/name).read_bytes();(out/name).write_bytes(raw);result['sources'][name]=hashlib.sha256(raw).hexdigest()
        result['limitations']='Cached definitions only; no resolver invocation or initializer execution proof. Sequential rereads are not atomic. Later writers and refreshed-consist behavior remain unvalidated.'
        (out/'inputs.json').write_text(json.dumps(result,indent=2,allow_nan=False))
        print(json.dumps(dict(guards_pass=result['guards_pass'],services=[{k:v for k,v in s.items() if k!='definitions'} for s in result['services']])))
    finally:K.CloseHandle(r.h)
