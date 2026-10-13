"""Snapshot bounded loaded path nodes for the current service registry, read-only."""
import argparse
import datetime
import hashlib
import json
import shutil
from pathlib import Path
from read_live import K
from read_services import ServiceReader
from read_loaded_path_nodes import snapshot

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    if Path(args.name).name != args.name or args.name in ('.', '..'):
        parser.error('Invalid capture name')
    root = Path(__file__).resolve().parent
    out = root/'captures'/args.name
    out.mkdir(exist_ok=False)
    reader = ServiceReader(args.pid)
    try:
        sources = {}
        for name in ('read_service_paths.py', 'read_loaded_path_nodes.py', 'read_services.py', 'read_live.py'):
            shutil.copy2(root/name, out/name)
            sources[name] = hashlib.sha256((root/name).read_bytes()).hexdigest()
        registry = reader.registry()
        rows = []
        for service in registry['entries']:
            row = dict(service=service)
            try:
                row['path'] = snapshot(reader, service['address'])
            except (OSError, ValueError) as exc:
                row['error'] = str(exc)
            rows.append(row)
        after = reader.registry()
        result = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      pid=args.pid, sha256=reader.sha, sources=sources,
                      registry=registry, services=rows,
                      registry_addresses_stable=[s['address'] for s in registry['entries']] ==
                          [s['address'] for s in after['entries']],
                      limits='Sequential external reads; equal addresses/rereads do not exclude reuse or establish atomicity. Wait flags do not prove execution.')
        (out/'paths.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n', encoding='utf-8')
        print(json.dumps(dict(services=len(rows), errors=sum('error' in s for s in rows),
                             registry_addresses_stable=result['registry_addresses_stable'],
                             paths=[dict(service=s['service']['address'], strings=s['service'].get('strings'),
                                         count=s.get('path', {}).get('node_count'),
                                         waits=[n for n in s.get('path', {}).get('nodes', []) if n['wait_flag']]) for s in rows])))
    finally:
        K.CloseHandle(reader.h)
