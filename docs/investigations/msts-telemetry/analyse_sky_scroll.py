"""Compare sampled UV changes with shader-clock and wall-time intervals."""
import collections,hashlib,json,statistics,struct
from pathlib import Path
root=Path(__file__).resolve().parent;source=root/'captures/sky-vertices-paused-02/samples.jsonl'
rows=[json.loads(x) for x in source.read_text().splitlines()];groups={};excluded=collections.Counter()
for a,b in zip(rows,rows[1:]):
    if 'error' in a or 'error' in b:excluded['row_error']+=1;continue
    previous={(o['kind'],o['index'],o['address'],o['vertex_pointer']):o for o in a['objects']}
    for y in b['objects']:
        key=(y['kind'],y['index'],y['address'],y['vertex_pointer']);x=previous.get(key)
        if x is None:excluded['identity_change']+=1;continue
        if not all(r['structure_stable'] for r in (a,b)) or not all(o['header_stable'] and o['shader_stable'] for o in (x,y)):
            excluded['unstable_endpoints']+=1;continue
        if not x.get('frame_available') or not y.get('frame_available'):excluded['frame_unavailable']+=1;continue
        if x['selected_frame']!=y['selected_frame'] or x['frame_raw']!=y['frame_raw'] or len(x['vertices'])!=len(y['vertices']):
            excluded['frame_or_geometry_change']+=1;continue
        scroll=struct.unpack_from('<ff',bytes.fromhex(y['frame_raw']),24)
        dt=y['clock_raw']-x['clock_raw'];wall=b['monotonic']-a['monotonic']
        g=groups.setdefault(str(key),dict(scroll=list(scroll),sample_pairs=0,vertices_per_pair=len(y['vertices']),shader_errors=[],wall_errors=[],nonzero_scroll_shader_errors=[],nonzero_scroll_wall_errors=[],clock_steps=[],wall_steps=[]))
        g['sample_pairs']+=1;g['clock_steps'].append(dt);g['wall_steps'].append(wall)
        for u,v in zip(x['vertices'],y['vertices']):
            for axis in (0,1):
                actual=v['uv'][axis]-u['uv'][axis]
                g['shader_errors'].append(abs(actual-scroll[axis]*dt))
                g['wall_errors'].append(abs(actual-scroll[axis]*wall))
                if scroll[axis]!=0:
                    g['nonzero_scroll_shader_errors'].append(abs(actual-scroll[axis]*dt))
                    g['nonzero_scroll_wall_errors'].append(abs(actual-scroll[axis]*wall))
def stats(x):return dict(count=len(x),minimum=min(x),median=statistics.median(x),maximum=max(x)) if x else dict(count=0,minimum=None,median=None,maximum=None)
out=dict(source=str(source.relative_to(root)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),excluded=dict(excluded),
         objects=[dict(identity=k,**{n:(stats(v) if isinstance(v,list) and n!='scroll' else v) for n,v in g.items()}) for k,g in groups.items()],
         limitations='Only consecutive stable-header/structure,constant-frame pairs retained. Vertex payloads still non-atomic. '
         'Prediction is a sampled-interval approximation,not per-render float32 replay. UV error is coordinate difference,not pixels. '
         'Shader time/wall time agreement does not prove universal clock equivalence or exact cadence. Zero-scroll cases are not timing discrimination.')
(root/'sky-scroll-summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
