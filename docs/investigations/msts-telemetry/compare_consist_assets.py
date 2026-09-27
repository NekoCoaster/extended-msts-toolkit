"""Bounded comparison of the two definitions observed in the paused grain consist."""
import json,re,hashlib,struct
from pathlib import Path
root=Path(__file__).resolve().parent
capture=root/'captures/consist-totals-paused-01/snapshot.json'
data=json.loads(capture.read_text());rows=[]
assets={155000.0:Path('C:/MSTS/TRAINS/TRAINSET/DASH9/dash9.eng'),106747.0:Path('C:/MSTS/TRAINS/TRAINSET/US2GRAINCAR/us2graincar.wag')}
# The explicit two-asset mapping is scoped corroboration, not a general asset resolver.
seen=set()
for train in data['trains']:
    for car in train['cars']:
        if car['definition'] in seen:continue
        seen.add(car['definition']);p=assets[car['definition_mass_candidate']];raw=p.read_bytes()
        text=raw.decode('utf-16') if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else raw.decode('utf-8-sig')
        mass=re.findall(r'(?im)^\s*Mass\s*\(\s*([\d.]+)t\s*\)',text)
        size=re.findall(r'(?im)^\s*Size\s*\(\s*([\d.]+)m\s+([\d.]+)m\s+([\d.]+)m\s*\)',text)
        assert len(mass)==len(size)==1
        f32=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
        kg=f32(float(mass[0])*1000);length=f32(float(size[0][2]))
        rows.append(dict(definition=car['definition'],asset=str(p),sha256=hashlib.sha256(raw).hexdigest(),declared_mass_tonnes=mass[0],declared_size_m=size[0],native_mass=car['definition_mass_candidate'],native_length=car['definition_length_candidate'],mass_matches=kg==car['definition_mass_candidate'],length_matches=length==car['definition_length_candidate']))
assert all(r['mass_matches'] and r['length_matches'] for r in rows)
report=dict(capture=str(capture.relative_to(root)),capture_sha256=hashlib.sha256(capture.read_bytes()).hexdigest(),scope='Two explicitly mapped installed assets, not automatic asset resolution or arbitrary units',comparisons=rows)
(root/'consist-asset-summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
