"""Summarize captured native car-motion evidence without asserting atomicity."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('names',nargs='+');a=p.parse_args();root=Path(__file__).resolve().parent;result={}
for name in a.names:
    if Path(name).name!=name:raise ValueError('Invalid capture name')
    lines=[json.loads(x) for x in (root/'captures'/name/'samples.jsonl').read_text(encoding='utf-8').splitlines()]
    good=[x['snapshot'] for x in lines if 'snapshot' in x];groups={};previous={};speed_changes={}
    for s in good:
        for t in s['trains']:
            key=str(t['id']);g=groups.setdefault(key,dict(is_player=t['is_player'],train_speeds=[],car_counts=[],cars=[],same_step_cars=[]))
            old=previous.get(key)
            if old and s['sim_time']>old[0]:speed_changes.setdefault(key,[]).append((t['speed_raw']-old[1])/(s['sim_time']-old[0]))
            previous[key]=(s['sim_time'],t['speed_raw'])
            g['train_speeds'].append(t['speed_raw']);g['car_counts'].append(len(t['cars']));g['cars'].extend(t['cars'])
            if s['sim_time']==s['sim_time_after']:g['same_step_cars'].extend(c for c in t['cars'] if c['body_pointer_stable'] and c['body_pointer_stable_after'])
    def span(xs):return [min(xs),max(xs)] if xs else None
    summaries={}
    for key,g in groups.items():
        cars=g['cars'];stable=g['same_step_cars'];ordinary=[c for c in stable if not c['derailed'] and not c['car_flags84']&2]
        summaries[key]=dict(is_player=g['is_player'],train_speed_range=span(g['train_speeds']),train_sample_speed_change_per_second_range=span(speed_changes.get(key,[])),car_count_range=span(g['car_counts']),car_observations=len(cars),same_step_stable_car_observations=len(stable),ordinary_comparisons=len(ordinary),
            stored_speed_range=span([c['stored_velocity'] for c in cars]),stored_acceleration_range=span([c['stored_acceleration'] for c in cars]),body_speed_range=span([sum(v*v for v in c['velocity'])**.5 for c in cars]),
            max_same_step_speed_rebuild_error=max((abs(c['stored_velocity']-c['rebuilt_signed_velocity']) for c in ordinary),default=None),max_same_step_acceleration_rebuild_error=max((abs(c['stored_acceleration']-c['rebuilt_signed_acceleration']) for c in ordinary),default=None),
            durability_values=sorted({c['comparison_value'] for c in cars}),flags84=sorted({c['car_flags84'] for c in cars}),derailed_observations=sum(c['derailed'] for c in cars),qualification_observations=sum(bool(c['evaluation_kind']) and c['comparison_true'] for c in cars))
    result[name]=dict(samples=len(lines),errors=[x['error'] for x in lines if 'error' in x],sim_time_range=span([x['sim_time'] for x in good]),cross_step_samples=sum(x['sim_time']!=x['sim_time_after'] for x in good),paused_samples=sum(bool(x['paused']) for x in good),trains=summaries)
out=dict(captures=result,limitations='Same-step and stable-pointer checks do not guarantee an atomic read or same producer phase. Ranges aggregate car observations, not independent events. Stored motion may be stale in skipped branches; no finite-difference validation.')
(root/'vehicle-motion-summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out))
