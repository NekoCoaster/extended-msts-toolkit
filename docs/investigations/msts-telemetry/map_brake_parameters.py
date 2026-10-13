"""Match native brake token labels, parser destinations and live loaded definitions."""
import argparse,json,re,struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args();root=Path(__file__).resolve().parent;pe=PE();r=Reader(a.pid)
try:
    asm=(root/'pass58/00614c8e.asm').read_text();entries=[]
    for i in range(23):
        label_addr=0x795790+i*8;string=pe.u(label_addr);token=pe.u(label_addr+4);expected=0x401a1+i
        assert token==expected
        branch=pe.u(0x61715c+i*4);tail=asm[asm.index(f'{branch:08x}  '):];match=re.search(r'ADD EDX,0x([0-9a-f]+)',tail[:280]);assert match
        offset=int(match.group(1),16);assert 0x940<=offset<=0x99c
        assert r.read(label_addr,8)==pe.read(label_addr,8) and r.u(0x61715c+i*4)==branch
        checked=0
        for line in (root/'pass58/00614c8e.bytes.tsv').read_text().splitlines():
            va,raw=line.split('\t');va=int(va,16)
            if branch<=va<branch+29:
                data=bytes.fromhex(raw);assert pe.read(va,len(data))==data and r.read(va,len(data))==data;checked+=len(data)
        assert checked>=20
        entries.append(dict(parser_destination_bytes_verified=checked,token=hex(token),label=pe.string(string),table_entry=hex(label_addr),parser_target=hex(branch),definition_offset=hex(offset)))
    trains=[]
    for t in r.trains():
        cars=[]
        for c in t['cars']:
            addr=c['address'];d=c['definition'];cars.append(dict(address=addr,definition=d,powered=c['powered'],parameters={e['label']:r.f(d+int(e['definition_offset'],16)) for e in entries},raw_pressures={hex(o):r.f(addr+o) for o in (0x224,0x228,0x230,0x234,0x238)},owner_stable=r.u(addr+0x98)==t['address']))
        trains.append(dict(address=t['address'],is_player=t['is_player'],cars=cars))
    result=dict(image_sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),entries=entries,trains=trains,limitations='Labels and selected parser data match disk/live. Units follow named pressure/rate semantics; unit conversion helper not revalidated. Configuration may be defaulted. No AI in this snapshot; no universal brake-type applicability.')
    (root/'brake-parameter-map.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(dict(entries=entries,first_car=trains[0]['cars'][0])))
finally:K.CloseHandle(r.h)
