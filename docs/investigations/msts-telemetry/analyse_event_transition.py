"""Summarize event13 boundary/latch observations without inferring atomicity."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = 'tokyo-event-transition-20261010-01'
rows = [json.loads(line) for line in (ROOT/'captures'/NAME/'samples.jsonl').read_text().splitlines()]
good = [r for r in rows if 'error' not in r]
observations = []
for r in good:
    e = next(e for e in r['events'] if e['id'] == 13)
    a = next(e for e in r['activity']['events'] if e['id'] == 13)
    observations.append(dict(time=r['sim_time'],time_after=r['sim_time_after'],paused=r['paused'],speed=r['speed'],
        distance=e['horizontal_distance'],predicate=e['predicate'],latch=e['latched_raw'],
        activation=e['activation_level'],second_latch=a['state_10'],reversible=a['reversible_candidate'],
        stop=r['activity']['event_evaluation_stop'],success=r['activity']['event_outcome_success']))
changes=[]
previous=None
for r in observations:
    if previous is None or tuple(r[k] for k in ('predicate','latch','paused')) != tuple(previous[k] for k in ('predicate','latch','paused')):
        changes.append(dict(before=previous,after=r))
    previous=r
time_edges=[]
previous_time=None
for r in good:
    e=next(e for e in r['activity']['events'] if e['id']==45)
    now=dict(sim_time=r['sim_time'],sim_time_after=r['sim_time_after'],event_clock=r['event_clock'],latch=e['state_10'],activation=e['activation_level'],outcome_count=e['outcome_count'])
    if previous_time and now['latch']!=previous_time['latch']:time_edges.append(dict(before=previous_time,after=now))
    previous_time=now
result=dict(time_event45_edges=time_edges,capture=NAME,samples=len(rows),errors=len(rows)-len(good),
    clock_crossings=sum(r['sim_time']!=r['sim_time_after'] for r in good),
    unstable_origin=sum(not r['origin_stable'] for r in good),unstable_player=sum(not r['player_stable'] for r in good),
    unstable_event_sentinel=sum(not r['event_sentinel_stable'] for r in good),
    split_latch_reads=sum(r['latch']!=r['second_latch'] for r in observations),
    outside_latched_samples=sum(not r['predicate'] and r['latch']==1 for r in observations),
    stop_success_values=sorted({(r['stop'],r['success']) for r in observations}),
    changes=changes,final=observations[-1],
    limitations='Sequential reads and sampled bounds, not atomic events. Reconstructed finite-input geometry does not fully emulate x87 boundaries. Message UI separately observed;no success/failure/reversal or activation transition established.')
(ROOT/'event-transition-20261010-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
