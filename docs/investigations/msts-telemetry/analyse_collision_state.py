"""Summarize retained collision snapshots; no causal or angular-unit inference."""
import hashlib,json,math
from pathlib import Path
root=Path(__file__).resolve().parent
live_path=root/'captures/collision-paused-01/samples.jsonl'
track_path=root/'captures/collision-track-paused-01/tracks.json'
live=json.loads(live_path.read_text());tracks=json.loads(track_path.read_text())
assert live['paused']==tracks['paused']==1
assert live['sim_time']==live['sim_time_after']==tracks['sim_time']==tracks['sim_time_after']
tm={c['address']:c for t in tracks['tracks']['trains'] for c in t['cars']}
rows=[]
for train in live['registered_trains']:
    records=[]
    for c in train['cars']:
        t=tm[c['address']];assert t['body']==c['body']
        basis=[c[k] for k in ['right','up','forward']]
        orthogonality=max(abs(sum(a*b for a,b in zip(basis[i],basis[j]))) for i in range(3) for j in range(i+1,3))
        lengths=[math.sqrt(sum(v*v for v in b)) for b in basis]
        records.append(dict(address=c['address'],body=c['body'],flags=c['body_flags'],derailed=c['derailed'],resting=c['resting'],angular_velocity_norm=math.sqrt(sum(v*v for v in c['angular_velocity'])),angular_momentum_norm=math.sqrt(sum(v*v for v in c['angular_momentum'])),body_track_separation=math.dist(c['position'],t['track']['position_candidate']),basis_lengths=lengths,max_basis_dot=orthogonality,section_pointer_matches=t['track']['section_pointer_matches']))
    rows.append(dict(id=train['id'],is_player=train['is_player'],cars=len(records),derailed=sum(c['derailed'] for c in records),resting=sum(c['resting'] for c in records),derailed_and_resting=sum(c['derailed'] and c['resting'] for c in records),nonzero_angular_velocity=sum(c['angular_velocity_norm']>0 for c in records),nonzero_angular_momentum=sum(c['angular_momentum_norm']>0 for c in records),max_angular_velocity_norm=max(c['angular_velocity_norm'] for c in records),max_body_track_separation=max(c['body_track_separation'] for c in records),all_section_pointers_match=all(c['section_pointer_matches'] for c in records),records=records))
out=dict(sources={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [live_path,track_path]},clock=live['sim_time'],paused=1,origin=tracks['tracks']['origin_tile'],origin_stable=tracks['tracks']['origin_stable'],trains=rows,
    limitations='Paused snapshot after an unrecorded collision interval,not impact-time or causal evidence. Angular values are inherited native-field candidates;nonzero values do not validate units or frame convention. Matching track section pointers do not make track position the derailed physical-body position. Separate reads with matching identities/clock are not atomic.')
(root/'collision-state-summary.json').write_text(json.dumps(out,indent=2))
print(json.dumps({**out,'trains':[{k:v for k,v in t.items() if k!='records'} for t in rows]},indent=2))
