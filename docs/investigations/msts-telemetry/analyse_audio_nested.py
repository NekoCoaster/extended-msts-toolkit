"""Analyze nested request identities and explicit vehicle associations."""
import collections,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent;p=root/'captures/audio-nested-paused-01/nested.json'
d=json.loads(p.read_text());pending=d['pending'];nodes=pending['nodes'];samples=pending['samples']
owners={(s['receiver'],s['index']):s for s in d['snapshot']['streams']}
sample_rows=[]
for sample in samples:
    refs=[n for n in nodes if n['kind']==1 and n['payload']==sample['address']]
    sources=[]
    for key in sorted({(n['receiver'],n['stream_index']) for n in refs}):
        s=owners[key];sources.append(dict(receiver=key[0],index=key[1],label=s['label'],associations=s['associations']))
    sample_rows.append(dict(address=sample['address'],name=sample.get('name'),reference_count=sample.get('reference_count'),
        observed_references=len(refs),sources=sources,stable_header=sample.get('stable_header'),stable_pair=sample.get('stable_pair')))
out=dict(source=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),time=d['time_after'],paused=d['paused_after'],
    top_level_nodes=sum(len(s.get('queue_nodes',[])) for s in d['snapshot']['streams']),
    groups=[dict(wrapper=g['wrapper'],label=g['label'],index=g['stream_index'],children=len(g['children']),
                 returned_to_wrapper=g.get('returned_to_wrapper'),stable_wrapper=g.get('stable_wrapper'),stable_children=g.get('stable_children'),
                 error=g.get('error')) for g in d['nested_groups']],
    total_resolved_nodes=len(nodes),node_errors=[n for n in nodes if 'error' in n],
    sample_rows=sample_rows,limitations='Nested rings preserve parent identity; sample objects may be shared. Counts are partial for the bounded top-level traffic chain. No playback, AI lifetime or sequence-index interpretation inferred.')
(root/'audio-nested-summary.json').write_text(json.dumps(out,indent=2));print(json.dumps(dict(groups=len(out['groups']),children=sum(g['children'] for g in out['groups']),samples=len(samples),node_errors=len(out['node_errors']),shared_samples=sum(len(s['sources'])>1 for s in sample_rows))))
