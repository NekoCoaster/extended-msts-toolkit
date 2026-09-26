"""Map runtime graph to route IDs using geometry then endpoint adjacency."""
import json,re,hashlib
from pathlib import Path
from collections import Counter
root=Path(__file__).resolve().parent;path=Path('C:/MSTS/ROUTES/USA2/marias.tdb');raw=path.read_bytes();text=raw.decode('utf-16')
native=json.loads((root/'captures/topology-route-map-paused-01/topology.json').read_text())['topology'];asset={}
for m in re.finditer(r'\bTrackNode\s*\(\s*(\d+)',text):
    i=m.end();depth=1
    while depth and i<len(text):depth+=(text[i]=='(')-(text[i]==')');i+=1
    block=text[m.end():i];kind=1 if 'TrVectorNode' in block else 2 if 'TrJunctionNode' in block else 3
    row=dict(id=int(m[1]),kind=kind,pins=[tuple(map(int,x)) for x in re.findall(r'\bTrPin\s*\(\s*(\d+)\s+(\d+)\s*\)',block)])
    if kind==1:
        vals=re.search(r'TrVectorSections\s*\(\s*([^()]*)\)',block)[1].split();row['sections']=int(vals[0]);v=list(map(float,vals[1:17]));row['signature']=dict(definition=int(v[0]),tile=[int(v[8]),int(v[9])],offset=v[10:13])
    asset[row['id']]=row
mapping={};ambiguities=[]
for n in native['nodes']:
    if n['kind']!=1:continue
    s=n['first_section_signature'];matches=[]
    for v in asset.values():
        if v['kind']!=1 or v['sections']!=n['section_count']:continue
        q=v['signature']
        if q['definition']==s['definition'] and q['tile']==s['tile'] and max(abs(a-b) for a,b in zip(q['offset'],s['offset']))<.005:matches.append(v['id'])
    if len(matches)==1:mapping[n['address']]=matches[0]
    else:ambiguities.append(dict(address=n['address'],matches=matches))
for n in native['nodes']:
    if n['kind']==1:continue
    links=sorted((mapping.get(p['node'],-1),p['direction']) for p in n['links'])
    matches=[v['id'] for v in asset.values() if v['kind']==n['kind'] and sorted(v['pins'])==links]
    if len(matches)==1:mapping[n['address']]=matches[0]
    else:ambiguities.append(dict(address=n['address'],matches=matches))
initial_ambiguities=ambiguities.copy()
candidates={x['address']:x['matches'] for x in ambiguities if x['matches']}
changed=True
while changed:
    changed=False;used=set(mapping.values())
    for n in native['nodes']:
        if n['address'] in mapping:continue
        known=[(mapping[p['node']],p['direction']) for p in n['links'] if p['node'] in mapping]
        pool=candidates.get(n['address'],list(asset))
        matches=[i for i in pool if i not in used and asset[i]['kind']==n['kind'] and len(asset[i]['pins'])==len(n['links']) and all(x in asset[i]['pins'] for x in known)]
        candidates[n['address']]=matches
        if len(matches)==1:mapping[n['address']]=matches[0];used.add(matches[0]);changed=True
ambiguities=[dict(address=n['address'],matches=candidates.get(n['address'],[])) for n in native['nodes'] if n['address'] not in mapping]
mismatches=[];partial_checks=[]
for n in native['nodes']:
    if n['address'] not in mapping:continue
    links=sorted((mapping.get(p['node'],-1),p['direction']) for p in n['links'])
    if any(p[0]==-1 for p in links):
        partial_checks.append(n['address']);continue
    if links!=sorted(asset[mapping[n['address']]]['pins']):mismatches.append(dict(address=n['address'],native=links,asset=asset[mapping[n['address']]]['pins']))
remaining=set(asset);components=[]
while remaining:
    todo=[next(iter(remaining))];component=[]
    while todo:
        n=todo.pop()
        if n not in remaining:continue
        remaining.remove(n);component.append(n);todo.extend(p[0] for p in asset[n]['pins'])
    components.append(sorted(component))
result=dict(source=dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest()),asset_counts=dict(Counter(str(n['kind']) for n in asset.values())),component_sizes=sorted(map(len,components),reverse=True),small_components=[c for c in components if len(c)<20],mapping={str(k):v for k,v in mapping.items()},ambiguities=ambiguities,pin_mismatches=mismatches,partial_link_checks=partial_checks,unmapped_asset_ids=sorted(set(asset)-set(mapping.values())),limitation='Derived geometry and adjacency match for this route build; runtime IDs are not established native fields, and disconnected runtime objects were not enumerated.')
(root/'topology-summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['source','mapping']},indent=2))
