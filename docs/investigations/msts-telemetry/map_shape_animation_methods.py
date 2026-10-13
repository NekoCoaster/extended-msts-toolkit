"""Read initialized type-5 shape virtual table; do not invoke native methods."""
import argparse
import json
from pathlib import Path
from read_live import Reader, K
p = argparse.ArgumentParser()
p.add_argument('--pid',type=int,required=True)
a = p.parse_args()
r = Reader(a.pid)
try:
    expected = {0x28:0x6a5fc0,0x2c:0x6a5fd0,0x38:0x6a6300,0x3c:0x6a6310,0x40:0x6a6330,0x44:0x6a6340}
    rows = []
    for offset,target in expected.items():
        actual = r.u(0x828be0+offset)
        assert actual == target
        rows.append(dict(table='0x828be0',slot=hex(offset),target=hex(actual)))
    report = dict(pid=a.pid,image_sha256=r.sha,methods=rows,
                  limitation='Initialized live table values only; no disk-table equality, loaded shape instance or method invocation is claimed. Constructor and method code checked separately.')
    Path(__file__).with_name('shape-animation-method-map.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(methods=len(rows),table='0x828be0')))
finally:
    K.CloseHandle(r.h)
