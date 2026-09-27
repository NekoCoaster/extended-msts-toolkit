"""Verify native animation block/controller labels without invoking the parser."""
import argparse
import json
from pathlib import Path
from binary_fields import PE
from read_live import Reader, K
p=argparse.ArgumentParser()
p.add_argument('--pid',type=int,required=True)
a=p.parse_args()
pe,r=PE(),Reader(a.pid)
try:
    rows=[]
    for token in (0x15,0x16,0x17,0x18,0x1b,0x1c):
        table=0x794250+(token-0x13)*8
        raw=pe.read(table,8)
        assert pe.u(table+4)==token and r.read(table,8)==raw
        pointer=pe.u(table)
        label=pe.string(pointer)
        encoded=label.encode('utf-16le')+b'\0\0'
        assert r.read(pointer,len(encoded))==encoded
        rows.append(dict(token=hex(token),label=label,table=hex(table),bytes=raw.hex(),string_address=hex(pointer)))
    report=dict(pid=a.pid,image_sha256=r.sha,labels=rows,
                format_reference=dict(url='https://raw.githubusercontent.com/openrails/openrails/master/Source/Orts.Formats.Msts/ShapeFile.cs',observed_date='2026-09-27',lines='1307-1318,1367-1446',interpretation='Open Rails names the animation integers FrameCount then FrameRate and key integer Frame; format corroboration only, not native execution proof.'),
                limitation='Selected label/table bytes only. Native arithmetic is recorded in pass243; no loaded animation descriptor or visual comparison sampled.')
    Path(__file__).with_name('animation-time-token-map.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(rows))
finally:
    K.CloseHandle(r.h)
