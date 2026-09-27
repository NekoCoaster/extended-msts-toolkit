"""Verify alerter registration label and preserve installed binding provenance."""
import argparse,json,hashlib
from pathlib import Path
from read_live import Reader,K
from binary_fields import PE
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args();r=Reader(a.pid);pe=PE()
try:
 b='alerter\0'.encode('utf-16le');assert pe.read(0x76d5b4,len(b))==b and r.read(0x76d5b4,len(b))==b
 path=Path('C:/MSTS/GLOBAL/common.txt');raw=path.read_bytes();s=raw.decode('utf-16') if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else raw.decode('utf-8-sig');lines=[dict(line=i+1,text=x) for i,x in enumerate(s.splitlines()) if '"alerter"' in x]
 report=dict(pid=a.pid,sha256=r.sha,label_address='0x76d5b4',label_bytes=b.hex(),binding_file=str(path),binding_sha256=hashlib.sha256(raw).hexdigest(),bindings=lines,limitation='Installed declaration and native registration evidence;not proof current input bindings dispatch this shortcut.')
 Path(__file__).with_name('alerter-command-map.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
finally:K.CloseHandle(r.h)
