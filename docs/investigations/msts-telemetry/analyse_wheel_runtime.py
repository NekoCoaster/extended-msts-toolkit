"""Summarize retained wheel captures without re-reading or controlling MSTS."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
report=dict(sequences=[],manager_surveys=[],limitations='Short sampled moving intervals;unsampled tails exist before final UI pause. Stored rates/zeros do not prove physical slip,visible animation or all-AI cadence.')
for name in ('wheel-moving-opening-01','wheel-moving-player-ai-01','wheel-external-view-01'):
    path=root/'captures'/name/'samples.jsonl'
    rows=[json.loads(line) for line in path.read_text().splitlines()]
    cars=[v for row in rows for v in row.get('sample',{}).get('vehicles') or []]
    valid=[v for v in cars if 'error' not in v]
    engines={}
    for v in valid:
        if not v.get('driver'):continue
        key=str(v['object_id'])
        entry=engines.setdefault(key,dict(train=v.get('train'),rates=[],adhesion=[],phase=[],shape_current=[],shape_processed=[]))
        for dest,src in (('rates','rotation_rate'),('adhesion','adhesion_force_limit'),('phase','phase')):entry[dest].append(v['driver'][src])
        if v['shape']['available']:
            entry['shape_current'].append(v['shape']['current_animation_seconds'])
            entry['shape_processed'].append(v['shape']['processed_animation_seconds'])
    for entry in engines.values():
        for key in ('rates','adhesion','phase','shape_current','shape_processed'):
            values=entry[key]
            entry[key]=dict(min=min(values),max=max(values),distinct=len(set(values))) if values else None
    report['sequences'].append(dict(capture=name,samples=len(rows),clock_first=rows[0].get('sim_time'),clock_last=rows[-1].get('sim_time'),paused_samples=sum(bool(x.get('paused')) for x in rows),outer_errors=sum('error'in x for x in rows),vehicle_errors=sum('error'in x for x in cars),unstable_vehicle_identity=sum(not x['identity_stable'] for x in valid),unstable_shape_identity=sum(not x['shape']['identity_stable'] for x in valid if x['shape']['available']),vehicle_counts=sorted({len(x.get('sample',{}).get('vehicles') or []) for x in rows}),engines=engines))
for name in ('manager-loaded-01','manager-after-motion-01'):
    data=json.loads((root/'captures'/name/'manager.json').read_text())
    survey=data['survey']
    report['manager_surveys'].append(dict(capture=name,sim_time=data['sim_time'],roots_stable=survey['roots_stable'],lists=[dict(offset=x['offset'],stored=x['stored_count'],observed=len(x['objects']),stable=x['root_stable'] and all(v['stable'] and v['reciprocal_links'] for v in x['objects'])) for x in survey['lists']]))
(root/'wheel-runtime-summary.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
