"""Read the bounded 12-name cab extension table; never invokes its enums."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from binary_fields import PE
from read_live import Reader, K

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--pid', type=int, required=True)
    p.add_argument('--name', required=True)
    a = p.parse_args()
    if Path(a.name).name != a.name or a.name in ('.', '..'):
        p.error('Invalid capture name')
    root = Path(__file__).resolve().parent
    out = root / 'captures' / a.name
    out.mkdir(exist_ok=False)
    pe = PE()
    r = Reader(a.pid)
    try:
        table = pe.read(0x780160, 48)
        live_table = r.read(0x780160, 48)
        entries = []
        for i in range(12):
            address = pe.u(0x780160 + i * 4)
            name = pe.string(address, limit=128)
            expected = (name + '\0').encode('utf-16le')
            actual = r.read(address, len(expected))
            entries.append(dict(enum=0x100+i, enum_hex=hex(0x100+i), name=name,
                                pointer=hex(address), disk_hex=expected.hex(),
                                live_hex=actual.hex(), matches=expected == actual))
        sources = {}
        for name in ('read_extended_cab_names.py', 'binary_fields.py', 'read_live.py'):
            shutil.copy2(root / name, out / name)
            sources[name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
        report = dict(pid=a.pid, executable_sha256=r.sha, table='0x780160',
                      disk_table_hex=table.hex(), live_table_hex=live_table.hex(),
                      table_matches=table == live_table, entries=entries, sources=sources,
                      limits='Parser table evidence only; no native invocation, channel activation or semantic validation.')
        (out / 'names.json').write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps(dict(table_matches=report['table_matches'], entries=entries)))
    finally:
        K.CloseHandle(r.h)
