"""Verify native monitoring parameter labels and retain parser target mapping."""
import argparse,json,struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args();root=Path(__file__).resolve().parent;pe=PE();r=Reader(a.pid)
entries=[(0x4045b,0,0x611005),(0x4045c,4,0x611078),(0x4045d,12,0x6110b2),(0x40464,8,0x61103c),(0x40460,0x18,0x611160),(0x40461,0x1c,0x61119d),(0x40462,0x20,0x6111da),(0x40463,0x24,0x611219),(0x4046f,0x50,0x6114ce),(0x40470,0x54,0x61158b),(0x40471,0x58,0x6115ca),(0x40472,0x5c,0x611606),(0x40473,0x60,0x61150d),(0x40474,0x64,0x61154c)]
try:
    labels=[];checks=[]
    for token,offset,instruction in entries:
        table=0x796e30+(token-0x40475)*8;raw=pe.read(table,8);assert r.read(table,8)==raw and pe.u(table+4)==token
        pointer=pe.u(table);name=pe.string(pointer);b=(name+'\0').encode('utf-16le');assert pe.read(pointer,len(b))==b and r.read(pointer,len(b))==b
        labels.append(dict(token=hex(token),name=name,definition_offset=hex(offset),destination_instruction=hex(instruction),table=hex(table),table_bytes=raw.hex()))
    # The entire parser was already checked in pass261; retain selected label bytes
    # and constants here without claiming a fresh complete dispatch analysis.
    for address in (0x758b84,0x753c38,0x753e48):
        b=pe.read(address,4);assert r.read(address,4)==b;checks.append(dict(address=hex(address),bytes=b.hex(),float32=struct.unpack('<f',b)[0]))
    report=dict(pid=a.pid,sha256=r.sha,parameters=labels,constants=checks,limitation='Labels and constants checked now;destination mapping follows pass261 assembly. Timer units/runtime producers and unusual trigger formulas need independent interpretation.')
    (root/'monitor-parameter-map.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
finally:K.CloseHandle(r.h)
