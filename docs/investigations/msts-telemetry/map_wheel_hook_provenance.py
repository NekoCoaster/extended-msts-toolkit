"""Retain read-only entry bytes and source provenance; not live DLL attribution."""
import json,hashlib,struct,argparse
from pathlib import Path
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args()
root=Path(__file__).resolve().parent;out=root/'captures'/'wheel-hook-provenance-01';out.mkdir(exist_ok=False)
r=Reader(a.pid)
try:
    data=dict(pid=a.pid,sha256=r.sha,entries=[],sources=[],limitations='Relative jump destination only; no target execution, DLL attribution or proof of installed source/binary equivalence.')
    for address in (0x405694,0x5d5381):
        raw=r.read(address,6);data['entries'].append(dict(address=hex(address),bytes=raw.hex(),reread_stable=r.read(address,6)==raw,jump_target=hex(address+5+struct.unpack('<i',raw[1:5])[0]) if raw[0]==0xe9 else None))
    for name in ('crawl.c','prologues.h'):
        path=Path('C:/codex/repo/NEMT/runtime')/name;raw=path.read_bytes();(out/name).write_bytes(raw);data['sources'].append(dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest()))
    for name in ('map_wheel_hook_provenance.py','read_live.py'):(out/name).write_bytes((root/name).read_bytes())
    (out/'provenance.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
finally:K.CloseHandle(r.h)
