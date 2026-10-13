"""Read track references and dimensions for independently enumerated vehicles."""
import argparse
import hashlib
import json
from pathlib import Path
from read_physical_registry import PhysicalRegistryReader
from read_track import TrackReader
from read_live import K

class Reader(PhysicalRegistryReader, TrackReader):
    pass

p = argparse.ArgumentParser()
p.add_argument('--pid', type=int, required=True)
p.add_argument('--name', required=True)
a = p.parse_args()
if Path(a.name).name != a.name or a.name in ('.', '..'):
    p.error('Invalid name')
root = Path(__file__).resolve().parent
out = root / 'captures' / a.name
out.mkdir(exist_ok=False)
r = Reader(a.pid)
try:
    result = dict(pid=a.pid, sha256=r.sha, time=r.f(0x80acd4), paused=r.u(0x7be0f4),
                  origin=list(r.unpack(0x79d118,'ii')), access='QUERY_LIMITED_INFORMATION | VM_READ')
    reg = r.physical_registry()
    player = next(t for t in reg['trains'] if t['is_player'])
    player_car = player['cars'][0]
    result['player_car'] = player_car
    result['objects'] = []
    for o in reg['objects']:
        if o['native_kind'] not in (0x4000d, 0x4000e):
            continue
        addr = o['address']
        result['objects'].append(dict(address=addr, object_id=o['object_id'], owner=o['owner'],
                                      kind=o['native_kind'], body=o['physics']['body'],
                                      links=o['physics']['links'], position=o['physics']['position'],
                                      length=r.f(o['physics']['definition']+0x400),
                                      track=r.track(addr+0x128), owner_stable=o['owner']==r.u(addr+0x98)))
    result['end_time'] = r.f(0x80acd4)
    result['origin_stable'] = result['origin']==list(r.unpack(0x79d118,'ii'))
    result['sources'] = {}
    for name in ('read_loose_track_context.py','read_physical_registry.py','read_track.py','read_live.py'):
        data=(root/name).read_bytes()
        (out/name).write_bytes(data)
        result['sources'][name]=hashlib.sha256(data).hexdigest()
    (out/'context.json').write_text(json.dumps(result,indent=2))
    lead = next(o for o in result['objects'] if o['address']==player_car)
    nearest=sorted((o for o in result['objects'] if not o['owner']), key=lambda o:sum((x-y)**2 for x,y in zip(o['position'],lead['position'])))[:6]
    print(json.dumps(dict(player=lead, nearest=nearest),indent=2))
finally:
    K.CloseHandle(r.h)
