"""Retain disk/live constants and token labels used by wheel/adhesion tracing."""
import argparse
import json
import struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader, K

p = argparse.ArgumentParser()
p.add_argument('--pid', required=True, type=int)
a = p.parse_args()
pe, r = PE(), Reader(a.pid)
try:
    labels = []
    for address, expected in ((0x795470, 0x4013d), (0x795658, 0x4017a)):
        assert pe.u(address+4) == expected
        assert r.read(address, 8) == pe.read(address, 8)
        label = pe.string(pe.u(address))
        assert r.read(pe.u(address), len(label.encode('utf-16le'))+2) == label.encode('utf-16le')+b'\0\0'
        labels.append(dict(address=hex(address), token=hex(expected), label=label))
    constants = []
    for address in (0x753c38, 0x76e798, 0x76cbe0, 0x7732b4):
        assert r.read(address, 4) == pe.read(address, 4)
        constants.append(dict(address=hex(address), raw=pe.read(address, 4).hex(), value=r.f(address)))
    table_entry = 0x7732a0
    assert r.read(table_entry, 4) == pe.read(table_entry, 4)
    thunk = pe.u(table_entry)
    assert thunk == 0x40419c
    code = pe.read(thunk, 5)
    assert code[0] == 0xe9 and r.read(thunk, 5) == code
    target = thunk + 5 + struct.unpack('<i', code[1:])[0]
    assert target == 0x62ad6a
    callback = dict(vtable=hex(0x773280), slot=hex(0x20), table_entry=hex(table_entry),
                    thunk=hex(thunk), bytes=code.hex(), target=hex(target),
                    limitation='Static/live table and jump bytes; no loaded object or callback invocation observed.')
    result = dict(pid=a.pid, image_sha256=r.sha, labels=labels, constants=constants, callback=callback,
                  limitation='Exact selected constants/table/string bytes only; no loaded vehicle or physics behavior validation.')
    Path(__file__).with_name('adhesion-constant-map.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result))
finally:
    K.CloseHandle(r.h)
