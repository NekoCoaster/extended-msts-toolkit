"""Offline float32 model of the inspected automatic-player loading branch."""
import hashlib
import json
import struct
from pathlib import Path

root = Path(__file__).resolve().parent
path = root / 'captures/loading-duration-inputs-20261013-01/inputs.json'
data = json.loads(path.read_text())
f32 = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
remaining = f32(abs(f32(data['platform']['distance'] - data['platform']['pair_distance'])))
count = 0
trace = []
for i, car in enumerate(data['consist']):
    eligible = car['kind'] == 3 or car['capacity_field'] > 0
    if not eligible:
        trace.append(dict(index=i, eligible=False))
        continue
    remaining = f32(remaining - car['length'])
    negative_bit = bool(struct.unpack('<I', struct.pack('<f', remaining))[0] & 0x80000000)
    trace.append(dict(index=i, eligible=True, remaining=remaining, counted=not negative_bit))
    if negative_bit:
        break
    count += 1
duration = f32((2 * data['platform']['waiting'] * data['constants']['0x753fb0']['value']) / count) if count else 20.0
opening = json.loads((root / 'automatic-opening-20261013-summary.json').read_text())
observed = opening['first_positive']['remaining']
after_quarter = f32(duration - 0.25)
result = dict(source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), trace=trace,
              counted_vehicles=count, initial_duration=duration,
              after_assumed_quarter_step=after_quarter, captured_first_positive=observed,
              exact_float32_match=after_quarter == observed,
              minimum_wait_not_read_by_inspected_branch=data['platform']['minimum_wait'],
              limits='Later input snapshot,not simultaneous with onset. Quarter-step hypothesis agrees exactly but is not an instruction trace. Models finite captured inputs and camera-nonnull branch only;does not validate every definition kind,override or other loading path.')
(root / 'loading-duration-model-20261013.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
