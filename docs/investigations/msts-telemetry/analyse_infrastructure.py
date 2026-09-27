"""Compare every native registry index against installed route topology."""
import json,re,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent;s=json.loads((root/'captures/infrastructure-paused-01/infrastructure.json').read_text());x=s['infrastructure']
assetpath=Path('C:/MSTS/ROUTES/USA2/marias.tdb');raw=assetpath.read_bytes();text=raw.decode('utf-16');asset={}
for m in re.finditer(r'\bTrackNode\s*\(\s*(\d+)',text):
    end=m.end();depth=1
    while depth:depth+=(text[end]=='(')-(text[end]==')');end+=1
    block=text[m.end():end];kind=1 if 'TrVectorNode' in block else 2 if 'TrJunctionNode' in block else 3
    row=dict(kind=kind,pins=sorted(tuple(map(int,p)) for p in re.findall(r'\bTrPin\s*\(\s*(\d+)\s+(\d+)\s*\)',block)))
    if kind==1:
        v=re.search(r'TrVectorSections\s*\(\s*([^()]*)\)',block)[1].split();row['count']=int(v[0]);q=list(map(float,v[1:17]));row['definition']=int(q[0]);row['tile']=[int(q[8]),int(q[9])];row['offset']=q[10:13]
    asset[int(m[1])]=row
assert len(x['databases'])==1,'This comparison is scoped to one loaded route database'
mapping={n['address']:n['route_id_candidate'] for n in x['databases'][0]['nodes'] if n['address']};errors=[]
for n in x['topology']['nodes']:
    ident=mapping[n['address']];a=asset[ident]
    if n['kind']!=a['kind']:errors.append([ident,'kind'])
    if sorted((mapping[p['node']],p['direction']) for p in n['links'])!=a['pins']:errors.append([ident,'pins'])
    if n['kind']==1:
        q=n['first_section_signature']
        if n['section_count']!=a['count'] or q['definition']!=a['definition'] or q['tile']!=a['tile'] or max(abs(b-c) for b,c in zip(q['offset'],a['offset']))>=.005:errors.append([ident,'geometry'])
services={n['address']:n['service_id'] for n in x['topology']['services']['entries']}
presence=[dict(route_id=mapping[v['node']],entries=len(v['entries']),services=sorted(set(services.get(e['service'],'unknown') for e in v['entries'])),bad_node_backlinks=sum(e['track_node']!=v['node'] for e in v['entries'])) for v in x['vector_presence']]
signals=[i for d in x['databases'] for i in d['items'] if i['kind']==0]
associated=[dict(address=i['address'],service_pointer=i['associated_service'],service_id=services.get(i['associated_service'])) for i in signals if i['associated_service']]
out=dict(source=dict(path=str(assetpath),sha256=hashlib.sha256(raw).hexdigest()),native_nodes=len(mapping),asset_nodes=len(asset),node_set_complete=set(mapping.values())==set(asset),errors=errors,matched_prior_derived_ids=sum(mapping.get(int(k))==v for k,v in json.loads((root/'topology-summary.json').read_text())['mapping'].items()),presence=presence,signal_count=len(signals),signals_with_service=associated,sim_time_stable=s['sim_time']==s['sim_time_after'],limitations='Route index plus one verified only for this loaded route build; presence records are abstract car positions, not physical train objects or track-block occupancy booleans. Signal ownership meaning still requires acquisition-path validation.')
(root/'infrastructure-summary.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
