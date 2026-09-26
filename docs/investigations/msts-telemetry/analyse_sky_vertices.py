"""Measure sampled buffer changes; never equate retained buffers with visible draws."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
root=Path(__file__).resolve().parent;source=root/'captures'/a.name/'samples.jsonl'
rows=[json.loads(x) for x in source.read_text().splitlines()];errors=[];objects={};good=[];unstable=[]
for i,r in enumerate(rows):
    if 'error' in r:errors.append(dict(sample=i,error=r['error']));continue
    good.append(r)
    if not r['structure_stable']:unstable.append(dict(sample=i,kind='structure'))
    for o in r['objects']:
        key=f"{o['kind']}:{o['index']}:{o['address']}:{o['vertex_pointer']}"
        group=objects.setdefault(key,[]);group.append(o)
        if not o['header_stable'] or not o['shader_stable']:unstable.append(dict(sample=i,object=key))
summaries=[]
for key,items in objects.items():
    changes=dict(uv=0,diffuse=0,secondary=0,position=0,selected_frame=0,clock_raw=0)
    for x,y in zip(items,items[1:]):
        for field in ('uv','diffuse','secondary','position'):
            changes[field]+=([v[field] for v in x['vertices']] != [v[field] for v in y['vertices']])
        for field in ('selected_frame','clock_raw'):changes[field]+=x[field]!=y[field]
    summaries.append(dict(identity=key,observations=len(items),vertex_counts=sorted({x['vertex_count'] for x in items}),
        frame_counts=sorted({x['frames'] for x in items}),selected_frames=sorted({x['selected_frame'] for x in items}),
        clock_range=[min(x['clock_raw'] for x in items),max(x['clock_raw'] for x in items)],
        diffuse_values=sorted({v['diffuse'] for x in items for v in x['vertices']}),
        changes_between_observations=changes,first_vertex=items[0]['vertices'][0] if items[0]['vertices'] else None,
        last_vertex=items[-1]['vertices'][0] if items[-1]['vertices'] else None))
out=dict(source=str(source.relative_to(root)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),samples=len(rows),errors=errors,unstable=unstable,
    paused_samples=sum(bool(x['paused']) and bool(x['paused_after']) for x in good),
    time_range=[min(x['sim_time'] for x in good),max(x['sim_time_after'] for x in good)] if good else None,
    delta_range=[min(x['delta'] for x in good),max(x['delta'] for x in good)] if good else None,
    max_read_seconds=max((x['monotonic_after']-x['monotonic'] for x in good),default=None),objects=summaries,
    limitations='Non-atomic reads;sampled buffer retention/change is not active visibility,draw calls or exact producer cadence. '
    'Same pointers across this bounded capture are not persistent lifetime identity. Changed UVs alone do not establish wall/simulation time units.')
(root/(a.name+'-summary.json')).write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
