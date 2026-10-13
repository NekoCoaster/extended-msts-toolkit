"""Corroborate observed geometry against installed definitions; retain error measures."""
import json,math,re,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
s=json.loads((root/'captures/geometry-services-paused-01/lifecycle.jsonl').read_text())
asset=Path('C:/MSTS/GLOBAL/tsection.dat');raw=asset.read_bytes()
text=raw.decode('utf-16') if raw[:2] in [b'\xff\xfe',b'\xfe\xff'] else raw.decode('utf-8-sig')
records=[v['track'] for v in s['services']['entries']]
for t in s['tracks']['trains']:records.extend(c['track'] for c in t['cars'])
definitions={}
for r in records:
    index=r['section_definition_index']
    if index in definitions:continue
    g=r['geometry_definition'];m=re.search(r'\bTrackSection\s*\(\s*'+str(index)+r'\s',text)
    if not m:raise ValueError(f'Missing definition {index}')
    end=m.end();depth=1
    while depth and end<len(text):
        depth+=(text[end]=='(')-(text[end]==')');end+=1
    excerpt=text[m.start():end];size=re.search(r'SectionSize\s*\(\s*([^()]+)\)',excerpt)
    curve=re.search(r'SectionCurve\s*\(\s*([^()]+)\)',excerpt)
    width,length=map(float,size[1].split());radius,angle=map(float,curve[1].split()) if curve else (0.,0.)
    native_angle=g['curve_angle_candidate'];expected_length=abs(radius*math.radians(angle)) if radius else length
    definitions[index]=dict(native=g,asset_excerpt=excerpt,expected_radius=radius,expected_angle_radians=math.radians(angle),expected_length=expected_length,length_error=g['length']-expected_length,radius_error=g['radius_candidate']-radius,angle_error=native_angle-math.radians(angle))
comparisons=[]
for train in s['tracks']['trains']:
    for a,b in zip(train['cars'],train['cars'][1:]):
        x=a['track'];y=b['track'];ds=y['node_distance']-x['node_distance']
        if x['section']!=y['section'] or abs(ds)<.01:continue
        measured=(y['position_candidate'][1]-x['position_candidate'][1])/ds
        predicted=-math.sin(x['angles_candidate'][0])
        comparisons.append(dict(section=x['section_index'],definition=x['section_definition_index'],direction=x['direction'],radius=x['geometry_definition']['radius_candidate'],distance_delta=ds,dy_per_path_distance=measured,negative_sine_pitch=predicted,error=measured-predicted))
out=dict(capture='geometry-services-paused-01',source=dict(path=str(asset),sha256=hashlib.sha256(raw).hexdigest()),definitions=definitions,grade_comparisons=comparisons,limitations='Grade comparisons use separate car reference points, float precision and section interpolation. Curves can change tangent gradient. This does not establish signed grade in arbitrary travel direction or native HUD convention.')
(root/'geometry-summary.json').write_text(json.dumps(out,indent=2))
print(json.dumps(dict(definitions=len(definitions),grade_comparisons=len(comparisons),max_length_error=max(abs(g['length_error']) for g in definitions.values()),straight_grade_max_error=max(abs(g['error']) for g in comparisons if g['radius']==0))))
