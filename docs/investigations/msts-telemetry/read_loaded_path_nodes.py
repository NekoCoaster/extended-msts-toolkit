"""Read-only bounded path-node snapshot through an observed service iterator."""
import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path
from read_live import Reader, K


def snapshot(r, service):
    iterator = r.u(service+0x1d4)
    result = dict(service=service, iterator=iterator, time=r.f(0x80acd4), available=False)
    if not iterator:
        result['reason'] = 'Null service iterator'
        return result
    path = r.u(iterator)
    result['path'] = path
    if not path:
        result['reason'] = 'Null iterator path'
        return result
    header = r.read(path+0xc, 12)
    flags, base, count = struct.unpack('<3I', header)
    if count > 4096 or (count and not base):
        raise ValueError('Invalid or excessive path node count/base')
    raw = r.read(base, count*0x24) if count else b''
    nodes = []
    for i in range(count):
        block = raw[i*0x24:(i+1)*0x24]
        u = lambda off: struct.unpack_from('<I', block, off)[0]
        typ, node_flags = struct.unpack_from('<2H', block, 4)
        nodes.append(dict(index=i, address=base+i*0x24, raw_hex=block.hex(),
                          point=u(0), type=typ, flags=node_flags,
                          duration_raw=u(8), track_node=u(0x10),
                          primary=u(0x14), secondary=u(0x18),
                          position=struct.unpack_from('<f', block, 0x1c)[0],
                          wait_flag=bool(node_flags & 2),
                          reversal_precedence=bool(node_flags & 1)))
    result.update(available=True, flags=flags, node_base=base, node_count=count, nodes=nodes,
                  iterator_type=r.u(iterator+0xc), event_node=r.u(iterator+0x24),
                  header_stable=header == r.read(path+0xc, 12),
                  nodes_stable=raw == (r.read(base, count*0x24) if count else b''),
                  roots_stable=iterator == r.u(service+0x1d4) and path == r.u(iterator),
                  time_after=r.f(0x80acd4))
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--pid', type=int, required=True)
    p.add_argument('--service', type=lambda s:int(s,0), default=0x809890)
    p.add_argument('--name', required=True)
    a = p.parse_args()
    if Path(a.name).name != a.name or a.name in ('.', '..'):
        p.error('Invalid capture name')
    root = Path(__file__).resolve().parent
    out = root/'captures'/a.name
    out.mkdir(exist_ok=False)
    r = Reader(a.pid)
    try:
        sources = {}
        for name in ('read_loaded_path_nodes.py','read_live.py'):
            shutil.copy2(root/name,out/name)
            sources[name] = hashlib.sha256((root/name).read_bytes()).hexdigest()
        result = snapshot(r,a.service)
        result.update(pid=a.pid, executable_sha256=r.sha, sources=sources,
                      limits='Sequential snapshot;equal rereads do not establish atomicity. '
                             'Use an observed live service address. Wait flag alone does not prove '
                             'reachability,dwell,valid path or event execution.')
        (out/'path.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k not in ('nodes','sources','limits')}))
    finally:
        K.CloseHandle(r.h)
