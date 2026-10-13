"""Bounded player aggregate/history probe; external reads only, never native calls."""
import argparse
import hashlib
import json
import math
import shutil
import struct
import time
from pathlib import Path
from read_live import Reader, K


def sample(r):
    clock = r.f(0x80acd4)
    train = r.u(0x7c2ac0)
    row = dict(time=clock, paused=r.u(0x7be0f4), train=train, available=bool(train))
    if not train:
        return row
    first = r.u(train+0x62)
    aggregate = r.read(train+0x92, 8)
    history = r.read(0x80a974, 40)
    index = r.u(0x80a9b4)
    row.update(speed=struct.unpack('<2f', aggregate)[0],
               acceleration=struct.unpack('<2f', aggregate)[1],
               history=list(struct.unpack('<10f', history)), history_index=index,
               unfiltered_mean=r.f(0x80a9b0), step=r.f(0x828fb4))
    cars = []
    seen = set()
    car = first
    complete = True
    while car:
        if car in seen or len(cars) >= 512:
            complete = False
            break
        seen.add(car)
        raw = r.read(car+0x1bc, 8)
        nxt = r.u(car+0xa8)
        owner = r.u(car+0x98)
        speed, acceleration = struct.unpack('<2f', raw)
        cars.append(dict(address=car, owner=owner, next=nxt, speed=speed,
                         acceleration=acceleration,
                         stable=raw == r.read(car+0x1bc, 8) and nxt == r.u(car+0xa8)
                         and owner == r.u(car+0x98)))
        car = nxt
    row.update(cars=cars, complete=complete, history_index_valid=index < 10,
               sampled_car_mean=sum(c['acceleration'] for c in cars)/len(cars) if cars and complete else None,
               roots_stable=train == r.u(0x7c2ac0) and first == r.u(train+0x62),
               aggregate_stable=aggregate == r.read(train+0x92, 8),
               history_stable=history == r.read(0x80a974, 40) and index == r.u(0x80a9b4),
               time_after=r.f(0x80acd4))
    return row


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--pid', type=int, required=True)
    p.add_argument('--name', required=True)
    p.add_argument('--seconds', type=float, default=20)
    p.add_argument('--interval', type=float, default=.1)
    a = p.parse_args()
    if Path(a.name).name != a.name or a.name in ('.', '..') or not all(math.isfinite(v) and v > 0 for v in (a.seconds, a.interval)):
        p.error('Invalid name or timing')
    root = Path(__file__).resolve().parent
    out = root/'captures'/a.name
    out.mkdir(exist_ok=False)
    r = Reader(a.pid)
    try:
        sources = {}
        for name in ('read_train_acceleration.py', 'read_live.py'):
            shutil.copy2(root/name, out/name)
            sources[name] = hashlib.sha256((root/name).read_bytes()).hexdigest()
        (out/'metadata.json').write_text(json.dumps(dict(pid=a.pid, sha256=r.sha,
            seconds=a.seconds, interval=a.interval, sources=sources,
            limits='Sequential reads;matching rereads do not prove atomicity. History index can cycle between reads. Player only; no AI freshness claim.'), indent=2)+'\n')
        start = time.perf_counter()
        count = errors = 0
        with (out/'samples.jsonl').open('w') as f:
            while time.perf_counter()-start < a.seconds:
                try:
                    row = sample(r)
                    line = json.dumps(row, allow_nan=False)
                except (OSError, ValueError) as e:
                    line = json.dumps(dict(error=str(e)))
                    errors += 1
                f.write(line+'\n')
                f.flush()
                count += 1
                time.sleep(a.interval)
        result = dict(samples=count, errors=errors, wall_elapsed=time.perf_counter()-start)
        (out/'completion.json').write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result))
    finally:
        K.CloseHandle(r.h)
