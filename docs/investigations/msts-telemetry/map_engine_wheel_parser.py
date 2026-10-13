"""Check engine WheelRadius/NumWheels dispatch and selected writes, read-only."""
import argparse
import json
from pathlib import Path
from binary_fields import PE
from read_live import Reader, K
p = argparse.ArgumentParser()
p.add_argument('--pid', type=int, required=True)
a = p.parse_args()
root = Path(__file__).resolve().parent
pe, r = PE(), Reader(a.pid)
try:
    checks = []
    def check(address, size):
        raw = pe.read(address, size)
        assert r.read(address, size) == raw
        checks.append(dict(address=hex(address), bytes=raw.hex()))
        return raw
    labels = []
    for table, token, label in ((0x795470, 0x4013d, 'WheelRadius'), (0x7955a8, 0x40164, 'NumWheels')):
        check(table, 8)
        assert pe.u(table+4) == token and pe.string(pe.u(table)) == label
        check(pe.u(table), (len(label)+1)*2)
        labels.append(dict(token=hex(token), label=label))
    radius_index = check(0x61ec8f + 0x4013d - 0x4010e, 1)[0]
    radius_slot = 0x61ec57 + radius_index*4
    count_slot = 0x61ecc9 + (0x40164-0x40149)*4
    check(radius_slot, 4)
    check(count_slot, 4)
    assert pe.u(radius_slot) == 0x619c0f
    assert pe.u(count_slot) == 0x61a67f
    selected = []
    for line in (root/'pass58/0061949d.bytes.tsv').read_text().splitlines():
        address, raw = line.split('\t')
        va = int(address, 16)
        if any(lo <= va <= hi for lo, hi in ((0x6196c8,0x6196f5),(0x6196fc,0x619721),(0x619c0f,0x619c27),(0x61a67f,0x61a69a))):
            expected = bytes.fromhex(raw)
            assert pe.read(va,len(expected)) == expected and r.read(va,len(expected)) == expected
            selected.append(dict(address=address,bytes=raw))
    report = dict(pid=a.pid,image_sha256=r.sha,labels=labels,table_checks=checks,instructions=selected,
                  fields={'0x112':'engine definition WheelRadius','0x11a':'engine definition NumWheels'},
                  limitation='Selected dispatch/write bytes only; no loaded values or physical interpretation of wheel versus axle count was measured.')
    (root/'engine-wheel-parser-map.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(instructions=len(selected), bytes=sum(len(bytes.fromhex(x['bytes'])) for x in selected), fields=report['fields'])))
finally:
    K.CloseHandle(r.h)
