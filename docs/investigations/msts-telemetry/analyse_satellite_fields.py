"""Decode retained sky records and compare literal ENV fields; no new game reads."""
import hashlib,json,re,struct
from pathlib import Path
root=Path(__file__).resolve().parent
source=root/'captures/sky-structure-paused-01/sky.json'
asset=Path('C:/MSTS/ROUTES/USA2/ENVFILES/USA2snow.env')
capture=json.loads(source.read_text(encoding='utf-8'))
spec=json.loads((root/'satellite-fields.json').read_text(encoding='utf-8'))
b=asset.read_bytes();text=b.decode('utf-16') if b[:2] in (b'\xff\xfe',b'\xfe\xff') else b.decode('utf-8-sig')
blocks=[]
for match in re.finditer(r'\bworld_sky_satellite\s*\(',text):
    start=match.end();depth=1;end=start;quoted=False
    while depth and end<len(text):
        c=text[end]
        if c=='"':quoted=not quoted
        if not quoted:depth+=(c=='(')-(c==')')
        end+=1
    if depth:raise ValueError('Unbalanced selected satellite block')
    blocks.append(text[start:end-1])
if len(blocks)!=len(capture['satellites']):raise ValueError('Satellite count differs')
rows=[]
for record,block in zip(capture['satellites'],blocks):
    raw=bytes.fromhex(record['raw_hex']);values={};comparisons=[]
    for name,offset,fmt,meaning,units in spec:
        value=struct.unpack_from('<'+fmt,raw,offset)[0];values[name]=value
        matches=re.findall(r'\bworld_sky_satellite_'+name+r'\s*\(\s*([^()]+)\)',block)
        if len(matches)>1:raise ValueError('Duplicate selected token')
        declared=matches[0].strip() if matches else None
        row=dict(field=name,loaded=value,declared=declared)
        if 'colour' in name and declared:
            row.update(expected=int(declared,16),exact=value==int(declared,16))
        elif name in ('rise_time','set_time','fade_time'):
            expected=sum(float(x)*m for x,m in zip(declared.split(':'),(3600,60,1))) if declared else (2400 if name=='fade_time' else None)
            row.update(expected=expected,exact=value==expected,default_used=declared is None)
        elif name=='fog':
            expected=(int(declared)&255) if declared else 255
            row.update(expected=expected,exact=value==expected,default_used=declared is None)
        elif name in ('low_scale','high_scale') and declared:
            row['observed_ratio_to_authored']=value/float(declared)
        elif name=='rise_position' and declared:
            row['nominal_radian_error']=value-float(declared)*3.141592653589793/180
        elif name=='light_pointer':
            row['light_token']=re.findall(r'\bworld_sky_satellite_light\s*\(\s*([^()]+)\)',block)
        comparisons.append(row)
    rows.append(dict(index=record['index'],address=record['address'],values=values,comparisons=comparisons))
out=dict(source=str(source.relative_to(root)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
         asset=str(asset),asset_sha256=hashlib.sha256(b).hexdigest(),rows=rows,
         exact_comparisons=sum('exact' in c for r in rows for c in r['comparisons']),
         mismatches=[c for r in rows for c in r['comparisons'] if c.get('exact') is False],
         limitations='Decodes an existing paused capture. Literal parser is scoped to these blocks,not a complete SIMIS parser. '
         'Scale ratio observed,not proof of loader argument or world-size semantics. Nominal angle comparison is not bit-exact native conversion. '
         'Keys/times are loaded parameters,not current output or evidence of active visibility. Light token0 may still allocate a light.')
(root/'satellite-fields-summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(dict(exact_comparisons=out['exact_comparisons'],mismatches=out['mismatches'],rows=rows),indent=2))
