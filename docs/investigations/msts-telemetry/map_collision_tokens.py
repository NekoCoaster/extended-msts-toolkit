"""Verify exact collision parser labels/token pairs on disk and live."""
import argparse,json,struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args();pe=PE();r=Reader(a.pid)
try:
 rows=[]
 for label,entry,ptr,token in [('CollideFlags',0x794dd0,0x76749c,0x40069),('CollideFunction',0x794dd8,0x767474,0x4006a)]:
  expected=struct.pack('<2I',ptr,token);string=(label+'\0').encode('utf-16le');assert pe.read(entry,8)==r.read(entry,8)==expected;assert pe.read(ptr,len(string))==r.read(ptr,len(string))==string
  rows.append(dict(label=label,entry=hex(entry),pointer=hex(ptr),token=hex(token),pair=expected.hex(),string=string.hex(),disk_live_equal=True))
 report=dict(pid=a.pid,sha256=r.sha,labels=rows,limitation='Native token labels and parser linkage;not a complete flag-bit dictionary or callback invocation proof.')
 Path(__file__).with_name('collision-token-map.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
finally:K.CloseHandle(r.h)
