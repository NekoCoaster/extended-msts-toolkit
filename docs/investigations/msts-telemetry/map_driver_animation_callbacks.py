"""Verify native wheel/rod callback registrations; never invokes callbacks."""
import argparse
import json
import struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader, K
p = argparse.ArgumentParser()
p.add_argument('--pid', type=int, required=True)
a = p.parse_args()
pe, r = PE(), Reader(a.pid)
try:
    rows = []
    for index, label in enumerate([f'WHEELS{i}' for i in range(1,5)] + [f'ROD{i:02}' for i in range(1,7)]):
        table = 0x7a3dec + index*12
        raw = pe.read(table,12)
        assert r.read(table,12) == raw
        name, callback, flag = (pe.u(table+i) for i in (0,4,8))
        assert pe.string(name) == label and callback == 0x6390cf and flag == 0x800
        encoded = label.encode('utf-16le') + b'\0\0'
        assert pe.read(name,len(encoded)) == encoded and r.read(name,len(encoded)) == encoded
        rows.append(dict(address=hex(table),name=label,string_address=hex(name),callback=hex(callback),flag=hex(flag),bytes=raw.hex()))
    epsilon_raw = pe.read(0x753e38,4)
    assert r.read(0x753e38,4) == epsilon_raw
    report = dict(pid=a.pid,image_sha256=r.sha,registrations=rows,
                  comparison_epsilon=dict(address='0x753e38',bytes=epsilon_raw.hex(),value=struct.unpack('<f',epsilon_raw)[0]),
                  limitation='Selected table/string byte equality; no shape instance, callback execution or visual motion observed.')
    Path(__file__).with_name('driver-animation-callback-map.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(registrations=len(rows),callback='0x6390cf',flag='0x800')))
finally:
    K.CloseHandle(r.h)
