"""Read-only loaded resource words used by native Version_* header lists."""
import argparse, datetime, hashlib, json, shutil
from pathlib import Path
from read_services import ServiceReader
from read_live import K

p = argparse.ArgumentParser()
p.add_argument('--pid', type=int, required=True)
p.add_argument('--name', required=True)
a = p.parse_args()
if Path(a.name).name != a.name:
    raise ValueError('Invalid capture name')
root = Path(__file__).resolve().parent
out = root / 'captures' / a.name
out.mkdir(exist_ok=False)
r = ServiceReader(a.pid)
try:
    registry = r.registry()
    rows = []
    for entry in registry['entries']:
        s = entry['address']
        row = dict(service=s, is_player=entry['is_player'])
        try:
            path, consist, name = r.u(s+0x130), r.u(s+0x18), r.u(s+8)
            row.update(path=path, consist=consist, eligible=bool(path))
            row['service_name'] = r.wide(name, 4096) if name else None
            row['service_word'] = r.u(s+4)
            if path:
                path_name = r.u(path+4)
                row['path_name'] = r.wide(path_name, 4096) if path_name else None
                row['path_word'] = r.u(path+0x18)
                row['path_name_pointer_stable'] = r.u(path+4) == path_name
            if consist:
                row['consist_name'] = r.wide(consist+8, 64)
                row['consist_word'] = r.u(consist+0x88)
            row['source_pointers_stable'] = (r.u(s+0x130), r.u(s+0x18), r.u(s+8)) == (path, consist, name)
        except (OSError, ValueError) as e:
            row['error'] = str(e)
        rows.append(row)
    traffic = r.u(0x809ae0)
    result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), image_sha256=r.sha,
                  services=rows, traffic_name=r.wide(traffic,4096) if traffic else None,
                  traffic_word=r.u(0x809ae8), traffic_pointer_stable=r.u(0x809ae0)==traffic,
                  registry_stable=[x['address'] for x in r.registry()['entries']]==[x['address'] for x in registry['entries']],
                  dayclock=r.f(0x80acd4), paused=r.u(0x7be0f4),
                  limitations='Non-atomic sequential reads; pointer rereads do not prove contents stable. Native Version_* words have no independently traced producer/uniqueness semantics. No save generated or loaded.')
    (out/'versions.json').write_text(json.dumps(result,indent=2))
    hashes = {}
    for name in ['read_header_resource_versions.py','read_services.py','read_live.py']:
        shutil.copy2(root/name,out/name)
        hashes[name] = hashlib.sha256((out/name).read_bytes()).hexdigest()
    (out/'probe-hashes.json').write_text(json.dumps(hashes,indent=2))
    print(json.dumps(result,indent=2))
finally:
    K.CloseHandle(r.h)
