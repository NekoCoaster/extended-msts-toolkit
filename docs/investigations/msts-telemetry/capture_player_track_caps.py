"""Bounded read-only pairing of physical track positions and service speed caps."""
import argparse
import hashlib
import json
import math
import time
from pathlib import Path
from read_live import K
from read_track import TrackReader
from read_services import ServiceReader
from read_signals_cab import DetailReader
from read_speed_caps import capture as capture_caps

class Reader(TrackReader, ServiceReader, DetailReader):
    pass

def sample(r):
    row = r.details()
    row['physical_tracks'] = r.tracks()
    row['speed_caps'] = capture_caps(r)
    row['end_time'] = r.f(0x80acd4)
    row['end_paused'] = r.u(0x7be0f4)
    row['player_pointer_stable'] = row['player']['train'] == r.u(0x7c2ac0)
    return row

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--pid', type=int, required=True)
    p.add_argument('--name', required=True)
    p.add_argument('--seconds', type=float, default=90)
    p.add_argument('--interval', type=float, default=.25)
    a = p.parse_args()
    if Path(a.name).name != a.name or a.name in ('.', '..') or not all(math.isfinite(v) for v in (a.seconds, a.interval)) or not 0 <= a.seconds <= 600 or not .1 <= a.interval <= 10:
        p.error('Invalid name/timing bounds')
    root = Path(__file__).resolve().parent
    out = root / 'captures' / a.name
    out.mkdir(exist_ok=False)
    r = Reader(a.pid)
    try:
        meta = dict(pid=a.pid, sha256=r.sha, seconds=a.seconds, interval=a.interval,
                    access='QUERY_LIMITED_INFORMATION | VM_READ', sources={},
                    limitations='Sequential external reads; not atomic. Existing field interpretations apply. Cap reproduction covers finite inputs only. Physical and service track references need not coincide.')
        for name in ('capture_player_track_caps.py', 'read_live.py', 'read_track.py', 'read_services.py', 'read_signals_cab.py', 'read_speed_caps.py'):
            data = (root / name).read_bytes()
            (out / name).write_bytes(data)
            meta['sources'][name] = hashlib.sha256(data).hexdigest()
        (out / 'metadata.json').write_text(json.dumps(meta, indent=2))
        start = time.perf_counter()
        count = errors = 0
        with (out / 'samples.jsonl').open('w') as f:
            while True:
                begin = time.perf_counter()
                try:
                    row = sample(r)
                    line = json.dumps(row, allow_nan=False)
                except (OSError, ValueError) as e:
                    line = json.dumps(dict(error=str(e), monotonic=begin))
                    errors += 1
                f.write(line + '\n')
                f.flush()
                count += 1
                if time.perf_counter() - start >= a.seconds:
                    break
                time.sleep(max(0, a.interval - (time.perf_counter() - begin)))
        print(json.dumps(dict(output=str(out), samples=count, errors=errors)))
    finally:
        K.CloseHandle(r.h)
