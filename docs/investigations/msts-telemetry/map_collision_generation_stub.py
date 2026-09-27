"""Verify the exact collision generation jump stub independently of stored references."""
import argparse,json,struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args();r=Reader(a.pid);pe=PE()
try:
 addr=0x4038c3;b=pe.read(addr,5);assert b==r.read(addr,5) and b[0]==0xe9;target=addr+5+struct.unpack('<i',b[1:])[0];assert target==0x629dbc
 slot=pe.read(0x773298,4);assert slot==r.read(0x773298,4) and struct.unpack('<I',slot)[0]==addr
 report=dict(pid=a.pid,sha256=r.sha,stub=hex(addr),bytes=b.hex(),opcode='JMP rel32',target=hex(target),pointer_slot='0x773298',slot_bytes=slot.hex(),limitation='Stored Ghidra reference calls this UNCONDITIONAL_CALL but disk/live opcode is JMP. Slot reference is not invocation proof. Earlier pass283 began at a misaligned address and must not be used as instruction evidence.')
 Path(__file__).with_name('collision-generation-stub-map.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
finally:K.CloseHandle(r.h)
