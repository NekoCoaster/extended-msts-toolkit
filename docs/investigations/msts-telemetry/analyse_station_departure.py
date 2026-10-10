"""Summarize retained departure capture; no inferred exact crossing time."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
name = 'maryland-resume-departure-20261010-01'
rows = [json.loads(line) for line in (root/'captures'/name/'samples.jsonl').read_text().splitlines()]
good = [r for r in rows if 'error' not in r]
transitions = []
previous = None
for index, row in enumerate(good):
    players = [s for s in row['services'] if s['is_player']]
    if len(players) != 1:
        raise ValueError('Expected exactly one player service')
    player = players[0]
    state = {k: player[k] for k in ('selected', 'previous', 'efficiency')}
    state['boarding'] = row['activity']
    state['records'] = [{k: r[k] for k in ('address', 'platform', 'flags', 'recorded_arrival', 'recorded_departure', 'efficiency')} for r in player['records']]
    if previous is None or state != previous:
        transitions.append(dict(index=index, previous_observation_start=good[index-1]['sim_time'] if index else None,
                                observation_start=row['sim_time'], observation_end=row['sim_time_after'],
                                speed=row['player']['speed'], state=state))
    previous = state
result = dict(capture=name, samples=len(rows), errors=len(rows)-len(good),
              sim_time_range=[good[0]['sim_time'], good[-1]['sim_time_after']],
              paused_samples=sum(bool(r['paused']) for r in good),
              clock_crossings=sum(r['sim_time'] != r['sim_time_after'] for r in good),
              unstable_services=sum(not s['selection_stable'] or not s['sentinel_stable'] or any(not c['node_stable'] for c in s['records']) for r in good for s in r['services']),
              speed_range=[min(r['player']['speed'] for r in good), max(r['player']['speed'] for r in good)],
              final_paused=good[-1]['paused'], transitions=transitions,
              limitations='Sequential external reads, not atomic events. Stored departure time is a native record value, not an independently measured physical platform crossing. No nonzero boarding countdown or populated AI stop is established. Selection and effective efficiency are distinct fields.')
(root/'station-departure-20261010-summary.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
