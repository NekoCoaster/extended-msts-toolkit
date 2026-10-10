"""Summarize sampled event latch/activation changes and stop predicates."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
NAME='tokyo-stop-activation-20261010-01'
rows=[json.loads(x) for x in (ROOT/'captures'/NAME/'samples.jsonl').read_text().splitlines()]
good=[r for r in rows if 'error' not in r]
changes=[]
previous={}
for r in good:
    conditions={e['id']:e for e in r['events']}
    for e in r['activity']['events']:
        now=dict(sim_time=r['sim_time'],sim_time_after=r['sim_time_after'],event_clock=r['event_clock'],
            paused=r['paused'],speed=r['speed'],origin=r['origin'],event=e,condition=conditions.get(e['id']))
        old=previous.get(e['id'])
        if old and any(old['event'][k]!=e[k] for k in ('state_10','activation_level','state_20')):
            changes.append(dict(id=e['id'],before=old,after=now))
        previous[e['id']]=now
stop_sources={}
for event_id in (31,32,33):
    seq=[(r,next(e for e in r['events'] if e['id']==event_id)) for r in good]
    stop_sources[str(event_id)]=dict(inside_moving_unlatched=sum(e['inside_radius'] and not e['stop_condition'] and e['latched_raw']==0 for r,e in seq),
        true_predicate_samples=sum(e['predicate'] for r,e in seq),final=seq[-1][1])
result=dict(capture=NAME,samples=len(rows),errors=len(rows)-len(good),
    clock_crossings=sum(r['sim_time']!=r['sim_time_after'] for r in good),
    unstable_origin=sum(not r['origin_stable'] for r in good),unstable_player=sum(not r['player_stable'] for r in good),
    unstable_sentinel=sum(not r['event_sentinel_stable'] for r in good),
    origins=sorted({tuple(r['origin']) for r in good}),changes=changes,stop_sources=stop_sources,
    final=dict(sim_time=good[-1]['sim_time_after'],paused=good[-1]['paused'],speed=good[-1]['speed']),
    limitations='Sequential samples;reconstructed finite-input conditions are not native invocations. No atomicity or universal cadence claim. Target latch and activation have different semantics.')
(ROOT/'event-activation-20261010-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('changes','stop_sources')},indent=2))
for x in changes:
    a=x['after'];b=x['before'];print(x['id'],b['sim_time'],a['sim_time'],'latch',b['event']['state_10'],a['event']['state_10'],'activation',b['event']['activation_level'],a['event']['activation_level'],'speed',a['speed'],'condition',a['condition'])
