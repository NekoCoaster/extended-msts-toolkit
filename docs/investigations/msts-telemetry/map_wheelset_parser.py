"""Verify selected Wheelset parser instructions and label without changing MSTS."""
import argparse
import hashlib
import json
from pathlib import Path
from binary_fields import PE
from read_live import Reader, K

p = argparse.ArgumentParser()
p.add_argument('--pid', type=int, required=True)
a = p.parse_args()
root = Path(__file__).resolve().parent
pe, reader = PE(), Reader(a.pid)
try:
    table = 0x795d88
    assert pe.u(table) == 0x760a4c and pe.u(table + 4) == 0x40260
    assert pe.string(pe.u(table)) == 'Wheelset'
    checks = []
    for address, size in ((table, 8), (0x760a4c, 18)):
        expected = pe.read(address, size)
        assert reader.read(address, size) == expected
        checks.append(dict(address=hex(address), bytes=expected.hex()))
    selected = []
    for line in (root / 'pass58/00614c8e.bytes.tsv').read_text().splitlines():
        address, raw = line.split('\t')
        va = int(address, 16)
        if 0x614f7a <= va <= 0x614f84 or 0x616be0 <= va <= 0x616c1e:
            expected = bytes.fromhex(raw)
            assert pe.read(va, len(expected)) == expected
            assert reader.read(va, len(expected)) == expected
            selected.append(dict(address=address, bytes=raw))
    addresses = {int(x['address'], 16) for x in selected}
    assert {0x614f7a, 0x614f84, 0x616be6, 0x616bef, 0x616c0f}.issubset(addresses)
    asset = Path('C:/MSTS/TRAINS/TRAINSET/DEFAULT/default.wag')
    report = dict(pid=a.pid, image_sha256=reader.sha, label='Wheelset', token='0x40260',
                  definition_offset='0x4e8', declaration_flag_offset='0x8c', declaration_flag='0x10',
                  table_checks=checks, parser_instructions=selected,
                  source_asset=str(asset), source_asset_sha256=hashlib.sha256(asset.read_bytes()).hexdigest(),
                  limitation='Selected instruction/table/string equality only. No parsing invocation, evaluated expression value, loaded definition, phase units or rendering was observed.')
    (root / 'wheelset-parser-map.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(dict(label=report['label'], instructions=len(selected), bytes=sum(len(bytes.fromhex(x['bytes'])) for x in selected))))
finally:
    K.CloseHandle(reader.h)
