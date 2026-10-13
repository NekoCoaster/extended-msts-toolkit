"""Compare cab/external/cab snapshots; does not measure playback or latency."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
names=['receiver-distance-paused-01','receiver-external-camera-01','receiver-cab-restored-01']
snap=[json.loads((root/'captures'/n/'receivers.json').read_text(encoding='utf-8'))['snapshot'] for n in names]
maps=[{r['handle']:r for r in s['receivers']} for s in snap]
assert all(set(m)==set(maps[0]) for m in maps)
rows=[]
for handle in maps[0]:
    rs=[m[handle] for m in maps]
    rows.append(dict(handle=handle,label=rs[0]['definition_label'],flags=[r['flags'] for r in rs],inactive_bits=[bool(r['flags']&2) for r in rs],restored_flags=rs[0]['flags']==rs[2]['flags'],positions_unchanged=rs[0]['position']==rs[1]['position']==rs[2]['position'],squared_distances=[r['stored_squared_distance'] for r in rs]))
d=dict(captures=names,times=[s['time'] for s in snap],stable=[s['stable_list'] for s in snap],listener_positions=[s['listener_position'] for s in snap],rows=rows,limitations='Separate paused snapshots around normal camera controls; no transition latency, actual playback, or independent listener units validation.')
(root/'receiver-camera-summary.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
print(json.dumps(dict(changed=sum(r['flags'][0]!=r['flags'][1] for r in rows),restored=sum(r['restored_flags'] for r in rows),positions_unchanged=sum(r['positions_unchanged'] for r in rows),count=len(rows),times=d['times'])))
