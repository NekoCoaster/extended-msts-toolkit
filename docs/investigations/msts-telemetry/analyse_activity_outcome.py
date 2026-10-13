"""Station completion, event latch and activity result samples;no atomicity claim."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
NAME='tokyo-activity-outcome-20261010-01'
rows=[json.loads(x) for x in (ROOT/'captures'/NAME/'samples.jsonl').read_text().splitlines()]
good=[r for r in rows if 'error' not in r]
seq=[]
for r in good:
    p=next(x for x in r['services'] if x['is_player'])
    event=next(x for x in r['events']['events'] if x['id']==0)
    selected=next((x for x in p['records'] if x['address']==p['selected']),None)
    seq.append(dict(time=r['sim_time'],time_after=r['sim_time_after'],paused=r['paused'],speed=r['player']['speed'] if r['player'] else None,
        activity=r['activity'],event_latch=event['state_10'],event_activation=event['activation_level'],event_type=event['type'],outcomes=event['outcomes_raw'],
        second_stop=r['events']['event_evaluation_stop'],second_success=r['events']['event_outcome_success'],
        selected=p['selected'],previous=p['previous'],selected_platform=selected['platform'] if selected else None,
        all_stops_model=(False if not p['records'] else True if not p['selected'] else bool(selected['flags'] & 0x20) if selected is p['records'][-1] else False if selected else None),
        records=[{k:x[k] for k in ('address','platform','flags','scheduled_arrival','recorded_arrival','scheduled_departure','recorded_departure')} for x in p['records']]))
def signature(r):
    return (r['event_latch'],r['activity']['stop'],r['activity']['success'],r['activity']['boarding_active'],r['selected'],tuple((x['flags'],x['recorded_arrival'],x['recorded_departure']) for x in r['records']))
changes=[];last=None
for r in seq:
    if last is None or signature(last)!=signature(r):changes.append(dict(before=last,after=r))
    last=r
success=[r for r in seq if r['activity']['stop'] and r['activity']['success']]
result=dict(capture=NAME,samples=len(rows),errors=len(rows)-len(good),clock_crossings=sum(r['sim_time']!=r['sim_time_after'] for r in good),
    unstable_event_roots=sum(not r['event_root_stable'] for r in good),
    unstable_services=sum(not s['selection_stable'] or not s['sentinel_stable'] or any(not x['node_stable'] for x in s['records']) for r in good for s in r['services']),
    split_result_reads=sum(r['activity']['stop']!=r['second_stop'] or r['activity']['success']!=r['second_success'] for r in seq),
    success_samples=len(success),first_success=success[0] if success else None,changes=changes,final=seq[-1],
    limitations='Read-only sequential observations. Native success is not proof of perfect timetable/loading performance or every completion path;UI result separately observed. No failure/reload/reset validation.')
(ROOT/'activity-outcome-20261010-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('changes','final','first_success')},indent=2))
for x in changes:
    a=x['after'];b=x['before'];print('edge',b['time'] if b else None,a['time'],a['activity'],'latch',a['event_latch'],'platform',a['selected_platform'],'flags',[(r['platform'],hex(r['flags'])) for r in a['records']])
print('final',seq[-1]['time'],seq[-1]['paused'],seq[-1]['speed'])
