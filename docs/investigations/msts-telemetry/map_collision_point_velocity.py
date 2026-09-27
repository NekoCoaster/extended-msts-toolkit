"""Verify collision point-velocity thunk and comparison constant; read only."""
import argparse,json,struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args();pe=PE();r=Reader(a.pid)
try:
 addr=0x401aa0;b=pe.read(addr,5);live=r.read(addr,5);assert b==live and b[0]==0xe9;target=addr+5+struct.unpack('<i',b[1:])[0];assert target==0x5e17a0
 c=pe.read(0x77138c,4);assert c==r.read(0x77138c,4)
 report=dict(pid=a.pid,sha256=r.sha,thunk=dict(address=hex(addr),bytes=b.hex(),target=hex(target)),comparison=dict(address='0x77138c',bytes=c.hex(),float32=struct.unpack('<f',c)[0]),branch_immediate_floats={hex(x):struct.unpack('<f',struct.pack('<I',x))[0] for x in [0x3ca3d70a,0x3c23d70a,0x3f4ccccd]},limitation='Only thunk and scalar bytes verified;units follow existing body-field mapping,not independent contact measurement or exact host-float emulation.')
 Path(__file__).with_name('collision-point-velocity-map.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
finally:K.CloseHandle(r.h)
