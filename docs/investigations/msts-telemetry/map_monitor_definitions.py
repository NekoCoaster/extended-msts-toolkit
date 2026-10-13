"""Verify safety-monitor parser labels/dispatch and destination writes."""
import argparse,json
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args();root=Path(__file__).resolve().parent;pe=PE();r=Reader(a.pid)
try:
    checks=[];labels=[]
    def check(address,size):
        raw=pe.read(address,size);assert r.read(address,size)==raw;checks.append(dict(address=hex(address),bytes=raw.hex()));return raw
    for token,label,target,offset in [(0x40475,'AWSMonitor',0x61e204,0xb0c),(0x40476,'VigilanceMonitor',0x61e23c,0xb78),(0x40477,'EmergencyStopMonitor',0x61e273,0xbe4),(0x40478,'OverspeedMonitor',0x61e2ab,0xcbc)]:
        table=0x796e30+(token-0x40475)*8;check(table,8);assert pe.u(table+4)==token and pe.string(pe.u(table))==label
        check(pe.u(table),(len(label)+1)*2);index=check(0x61f0ae+token-0x40475,1)[0];slot=0x61f096+index*4;check(slot,4);assert pe.u(slot)==target
        labels.append(dict(token=hex(token),label=label,target=hex(target),definition_offset=hex(offset)))
    for line in (root/'pass58/0061949d.bytes.tsv').read_text().splitlines():
        address,h=line.split('\t');va=int(address,16)
        if 0x61982b<=va<=0x619857 or 0x61e204<=va<=0x61e2de:
            b=bytes.fromhex(h);assert pe.read(va,len(b))==b;check(va,len(b))
    out=dict(pid=a.pid,sha256=r.sha,labels=labels,checks=checks,limitations='Selected parser dispatch/destination proof;monitor behavior and runtime state require separate consumers.')
    (root/'monitor-definition-map.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(labels=labels,checks=len(checks))))
finally:K.CloseHandle(r.h)
