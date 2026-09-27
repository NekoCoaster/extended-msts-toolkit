"""Compare a bounded layer capture with literal declarations of the selected ENV."""
import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parent;source=root/'captures/sky-layers-paused-01/layers.json'
asset=Path('C:/MSTS/ROUTES/USA2/ENVFILES/USA2snow.env');b=asset.read_bytes()
text=b.decode('utf-16') if b[:2] in (b'\xff\xfe',b'\xfe\xff') else b.decode('utf-8-sig')
blocks=[]
for m in re.finditer(r'\bworld_sky_layer\s*\(',text):
    start=end=m.end();depth=1;quoted=False
    while depth and end<len(text):
        c=text[end]
        if c=='"':quoted=not quoted
        if not quoted:depth+=(c=='(')-(c==')')
        end+=1
    if depth:raise ValueError('Unbalanced layer')
    blocks.append(text[start:end-1])
capture=json.loads(source.read_text());checks=[]
if len(blocks)!=len(capture['layers']):raise ValueError('Layer count differs')
for row,block in zip(capture['layers'],blocks):
    def tokens(name):return re.findall(r'\bworld_sky_layer_'+name+r'\s*\(\s*([^()]+)\)',block)
    def check(name,actual,expected,note=''):
        checks.append(dict(layer=row['index'],field=name,actual=actual,expected=expected,equal=actual==expected,note=note))
    for field,token in [('top_faces','top_nfaces'),('top_radius','top_radius'),('top_height','top_height')]:
        values=tokens(token)
        if len(values)!=1:raise ValueError('Missing/ambiguous token '+token)
        check(field,row[field],float(values[0]),'Face match does not prove token is consumed;parser initializes8.' if field=='top_faces' else 'Loaded scaling ratio1 here,not universal.')
    counts=re.findall(r'\bworld_sky_layer_edge_steps\s*\(\s*(\d+)',block)
    check('edge_count',row['edge_count'],int(counts[0]))
    for field in ('height','radius'):
        check('edge_'+field,[e[field] for e in row['edges']],[float(x) for x in tokens('edge_step_'+field)])
    for phase in ('fadein','fadeout'):
        values=tokens(phase)
        expected=[sum(float(x)*m for x,m in zip(t.split(':'),(3600,60,1))) for t in values[0].split()] if values else [0,0]
        check(phase,[row[phase+'_start'],row[phase+'_end']],expected,'Absent pair remains zero-initialized;not proof of current opacity.')
out=dict(source=str(source.relative_to(root)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),asset=str(asset),asset_sha256=hashlib.sha256(b).hexdigest(),
         checks=checks,check_count=len(checks),mismatches=[x for x in checks if not x['equal']],
         limitations='Scoped literal comparison,not complete SIMIS grammar. Geometry/time parameters are not current opacity/UV/render output. Face count8 is initialized by native parser;all declarations8 cannot distinguish parsing from default. Loader scale and edge ordering preserved.')
(root/'sky-layers-summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(dict(check_count=len(checks),mismatches=out['mismatches'])))
