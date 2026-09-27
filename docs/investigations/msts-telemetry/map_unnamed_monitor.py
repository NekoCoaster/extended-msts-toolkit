"""Check the unnamed monitor disable thunk and diesel current multiplier."""
import argparse,json,struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);a=p.parse_args();r=Reader(a.pid);pe=PE()
try:
 thunk=pe.read(0x4033e6,5);assert r.read(0x4033e6,5)==thunk and thunk[0]==0xe9
 target=0x4033e6+5+struct.unpack('<i',thunk[1:])[0];assert target==0x60f839
 raw=pe.read(0x771430,4);assert r.read(0x771430,4)==raw
 report=dict(pid=a.pid,sha256=r.sha,disable_thunk=dict(address='0x4033e6',bytes=thunk.hex(),target=hex(target)),current_multiplier=dict(address='0x771430',bytes=raw.hex(),float32=struct.unpack('<f',raw)[0]),limitation='Selected thunk and constant only; does not establish a native subsystem name or live trip.')
 Path(__file__).with_name('unnamed-monitor-map.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
finally:K.CloseHandle(r.h)
