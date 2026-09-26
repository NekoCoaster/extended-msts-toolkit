"""Station-state transitions and observation bounds; no inferred event timestamps."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
result={}
for name in ('maryland-station-baseline-01','maryland-station-wait-01','maryland-station-departure-01'):
    rows=[json.loads(line) for line in (root/'captures'/name/'samples.jsonl').read_text(encoding='utf-8').splitlines()]
    good=[r for r in rows if 'error' not in r];transitions=[];previous=None
    for i,r in enumerate(good):
        p=next(s for s in r['services'] if s['is_player'])
        state=dict(selected=p['selected'],previous=p['previous'],efficiency=p['efficiency'],boarding=r['activity']['boarding_active'],remaining=r['activity']['remaining'],records=[{k:c[k] for k in ('address','flags','recorded_arrival','recorded_departure')} for c in p['records']])
        if previous is None or state!=previous['state']:
            transitions.append(dict(index=i,sim_time_before=r['sim_time'],sim_time_after=r['sim_time_after'],previous_observation_time=good[i-1]['sim_time_after'] if i else None,state=state))
        previous=dict(state=state)
    result[name]=dict(samples=len(rows),errors=len(rows)-len(good),sim_time_range=[good[0]['sim_time'],good[-1]['sim_time_after']],paused_samples=sum(bool(r['paused']) for r in good),clock_crossings=sum(r['sim_time']!=r['sim_time_after'] for r in good),unstable_services=sum(not s['selection_stable'] or not s['sentinel_stable'] or any(not c['node_stable'] for c in s['records']) for r in good for s in r['services']),player_speed_range=[min(r['player']['speed'] for r in good),max(r['player']['speed'] for r in good)],transitions=transitions)
result['limitations']='Non-atomic, sampled observations. Transition bounds are observation intervals, not proof of exact native write time. Capture name departure denotes intended test, not successful movement. No boarding-active or departure transition occurred if values remain zero.'
(root/'station-transition-summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
