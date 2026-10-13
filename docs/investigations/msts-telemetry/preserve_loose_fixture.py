"""Preserve fixture provenance and the new grain save without altering game files."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
out = root / 'captures/loose-fixture-provenance-01'
out.mkdir(exist_ok=False)
paths = [Path('C:/MSTS/ROUTES/USA2/ACTIVITIES/yard_one.act'),
         Path('C:/MSTS/saves/USA2/evegrain_27092026_184329.sav')]
records = []
for p in paths:
    data = p.read_bytes()
    (out / p.name).write_bytes(data)
    records.append(dict(path=str(p), bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), copy=p.name))
old = Path('C:/MSTS/saves/USA2/evegrain_27092026_051532.sav')
old_hash = hashlib.sha256(old.read_bytes()).hexdigest()
report = dict(files=records, previous_save=dict(path=str(old), sha256=old_hash,
             matches_previous_checkpoint=old_hash=='787f435189dcd5b645c3f448070d5d94e42330f8bca5275555d8e75b1b915a9d'),
             limitations='UI reported save success. New save has not been reloaded; this copy is preservation, not validation of complete restoration.')
(out / 'provenance.json').write_text(json.dumps(report, indent=2))
(out / Path(__file__).name).write_bytes(Path(__file__).read_bytes())
print(json.dumps(report, indent=2))
