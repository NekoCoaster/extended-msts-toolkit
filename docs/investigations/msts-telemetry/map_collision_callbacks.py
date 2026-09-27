"""Read-only callback table and rel32 stub mapping; names remain unassigned."""
import argparse,json,struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args();pe=PE();r=Reader(a.pid)
try:
 table=r.read(0x7a09b0,8);disk=pe.read(0x7a09b0,8);targets=list(struct.unpack('<2I',table))+[0x402bc6,0x401dbb];rows=[]
 for addr in targets:
  b=r.read(addr,5);d=pe.read(addr,5)
  rows.append(dict(address=hex(addr),live=b.hex(),disk=d.hex(),equal=b==d,stable=r.read(addr,5)==b,rel32_target=hex(addr+5+struct.unpack('<i',b[1:])[0]) if b[0]==0xe9 else None))
 report=dict(pid=a.pid,sha256=r.sha,table_address='0x7a09b0',table_live=table.hex(),table_disk=disk.hex(),table_equal=table==disk,table_stable=r.read(0x7a09b0,8)==table,callbacks=rows,limitation='Registration/save encoding and thunk targets only;not callback invocation or physical meaning.')
 Path(__file__).with_name('collision-callback-map.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
finally:K.CloseHandle(r.h)
