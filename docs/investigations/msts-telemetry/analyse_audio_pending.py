"""Summarize typed pending-node snapshot and native validation scope."""
import collections,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent;p=root/'captures/audio-pending-paused-01/pending.json'
d=json.loads(p.read_text());pending=d['pending'];nodes=pending['nodes'];samples=pending['samples']
out=dict(source=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
    time=d['time_after'],paused=d['paused_after'],node_count=len(nodes),
    kinds=dict(collections.Counter(str(n['kind']) for n in nodes)),stable_nodes=sum(n.get('stable_node',False) for n in nodes),
    node_errors=[n for n in nodes if 'error' in n],sample_objects=len(samples),
    sample_rows=[dict(address=s['address'],name=s.get('name'),directory=s.get('directory'),reference_count=s.get('reference_count'),
                     loaded_resource=s.get('loaded_resource'),stable_header=s.get('stable_header'),stable_pair=s.get('stable_pair'),
                     observed_type1_references=sum(n['kind']==1 and n['payload']==s['address'] for n in nodes)) for s in samples],
    queue_stops=[dict(label=s['label'],index=s['index'],stop=s['queue_traversal_stop']) for s in d['snapshot']['streams'] if 'queue_traversal_stop' in s],
    limitations='Node type2 payloads are not sample references. Partial chain counts cannot explain global sample reference counts. Loaded path labels not file hash identity, output playback, or AI ownership.')
(root/'audio-pending-summary.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
