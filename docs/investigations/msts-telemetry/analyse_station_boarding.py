"""Summarize boarding state without treating sequential reads as atomic."""
import argparse
import json
from pathlib import Path

root = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('capture', nargs='+')
p.add_argument('--output', required=True)
a = p.parse_args()
result = {}
for name in a.capture:
    rows = [json.loads(s) for s in (root/'captures'/name/'samples.jsonl').read_text().splitlines()]
    good = [r for r in rows if 'error' not in r]
    if not good:
        raise ValueError(f'No valid rows in {name}')
    changes = []
    prior = None
    active = []
    for index, row in enumerate(good):
        state = dict(active=row['activity']['boarding_active'], stop=row['activity']['stop'], success=row['activity']['success'], services=[])
        for service in row['services']:
            state['services'].append(dict(address=service['address'], player=service['is_player'], selected=service['selected'], previous=service['previous'], efficiency=service['efficiency'], records=[{k:c[k] for k in ('address','platform','flags','recorded_arrival','recorded_departure')} for c in service['records']]))
        if state != prior:
            changes.append(dict(index=index, prior_observation_start=good[index-1]['sim_time'] if index else None, start=row['sim_time'], end=row['sim_time_after'], remaining=row['activity']['remaining'], speed=row['player']['speed'] if row['player'] else None, state=state))
        prior = state
        if row['activity']['boarding_active']:
            active.append(row)
    consecutive = [(u,v) for u,v in zip(good,good[1:]) if u['activity']['boarding_active'] and v['activity']['boarding_active']]
    falling = [(u,v) for u,v in consecutive if v['activity']['remaining'] < u['activity']['remaining']]
    paused_pairs = [(u,v) for u,v in consecutive if u['paused'] and v['paused'] and u['sim_time']==v['sim_time_after']]
    result[name] = dict(samples=len(rows), errors=len(rows)-len(good), sim_time_range=[good[0]['sim_time'],good[-1]['sim_time_after']],
        paused_samples=sum(bool(r['paused']) for r in good), clock_crossings=sum(r['sim_time']!=r['sim_time_after'] for r in good),
        unstable_services=sum(not s['selection_stable'] or not s['sentinel_stable'] or any(not c['node_stable'] for c in s['records']) for r in good for s in r['services']),
        active_samples=len(active), remaining_range=[min(r['activity']['remaining'] for r in good),max(r['activity']['remaining'] for r in good)],
        active_time_range=[active[0]['sim_time'],active[-1]['sim_time_after']] if active else None,
        falling_pairs=len(falling), decrement_range=[min(u['activity']['remaining']-v['activity']['remaining'] for u,v in falling),max(u['activity']['remaining']-v['activity']['remaining'] for u,v in falling)] if falling else None,
        paused_active_pairs=len(paused_pairs), paused_remaining_changes=sum(u['activity']['remaining']!=v['activity']['remaining'] for u,v in paused_pairs),
        final_paused=good[-1]['paused'], changes=changes)
result['limitations']='Capture streams are separate and gaps must not be joined. Record and global fields are sequential reads; stable checks do not prove atomicity. Timer decrements may contain multiple native updates. Zero AI schedule/event times have no universal interpretation. UI input times are not embedded in the sample stream.'
(root/a.output).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:{f:v[f] for f in ('samples','errors','active_samples','remaining_range','falling_pairs','paused_active_pairs','paused_remaining_changes')} for k,v in result.items() if isinstance(v,dict)},indent=2))
