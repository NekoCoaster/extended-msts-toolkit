"""Bounded external snapshot of dispatcher inputs, not an event/crossing detector."""
import argparse, hashlib, json, math, struct
from pathlib import Path
from read_live import Reader, K

def nodes(r, sentinel, limit):
    node = r.u(sentinel)
    seen = set()
    while node != sentinel:
        if not node or node in seen or len(seen) >= limit:
            raise ValueError('List cycle/null/bound')
        seen.add(node)
        nxt, prev, value = r.unpack(node, 'III')
        yield node, nxt, prev, value
        node = nxt

def sample(r):
    out = dict(clock=r.f(0x80acd4), paused=r.u(0x7be0f4), records=[])
    sentinel = r.u(0x80a01c)
    if not sentinel:
        raise ValueError('No interaction root')
    head = r.u(sentinel)
    stable = True
    for node, nxt, prev, group in nodes(r, sentinel, 10000):
        item, services = r.unpack(group, 'II')
        kind = r.u(item)
        service_head = r.u(services)
        for sn, snext, sprev, record in nodes(r, services, 4096):
            if len(out['records']) >= 50000:
                raise ValueError('Total record bound')
            raw = r.read(record, 20)
            service, old_a, a, old_b, b = struct.unpack('<I4f', raw)
            threshold = r.f(service+0x128)
            if not all(math.isfinite(v) for v in (old_a,a,old_b,b,threshold)):
                raise ValueError('Nonfinite dispatcher input')
            state = 1 if a < threshold and b < threshold else 0 if old_a == -1 or old_b == -1 or a == old_a else 2 if a < old_a else 3
            good = (r.read(record,20)==raw and r.f(service+0x128)==threshold and r.unpack(sn,'III')==(snext,sprev,record))
            stable &= good
            out['records'].append(dict(item=item,kind=kind,record=record,service=service,previous=[old_a,old_b],current=[a,b],threshold=threshold,conditional_state=state,stable=good))
        stable &= r.unpack(group,'II')==(item,services) and r.u(services)==service_head and r.u(item)==kind and r.unpack(node,'III')==(nxt,prev,group)
    out['clock_after'] = r.f(0x80acd4)
    out['guards_pass'] = bool(stable and r.u(0x80a01c)==sentinel and r.u(sentinel)==head and out['clock']==out['clock_after'])
    if not out['guards_pass']:
        for row in out['records']:
            row['conditional_state'] = None
    return out

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid capture name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False)
    r=Reader(a.pid)
    try:
        result=sample(r);result['pid']=a.pid;result['image_sha256']=r.sha;result['sources']={}
        for name in ('read_track_interaction_records.py','read_live.py'):
            raw=(root/name).read_bytes();(out/name).write_bytes(raw);result['sources'][name]=hashlib.sha256(raw).hexdigest()
        result['limitations']='Sequential inputs, not atomic or guaranteed dispatch-time values. Conditional finite-value state only; no invocation or crossing proof. Pointer reuse and in-place changes may evade rereads.'
        (out/'records.json').write_text(json.dumps(result,indent=2,allow_nan=False))
        print(json.dumps(dict(records=len(result['records']),guards_pass=result['guards_pass'],clock=result['clock'],clock_after=result['clock_after'])))
    finally:K.CloseHandle(r.h)
