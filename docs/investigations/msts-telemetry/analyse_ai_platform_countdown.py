"""AI loading countdown/selection/motion observations;not an atomic instruction trace."""
import collections,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
NAME='winter-ai-stops-20261010-01'
raw=[json.loads(x) for x in (ROOT/'captures'/NAME/'samples.jsonl').read_text().splitlines()]
good=[x for x in raw if 'error' not in x]
series=collections.defaultdict(list)
for r in good:
    for s in r['services']:
        if s['is_player']:continue
        c=s['service_context'];selected=next((x for x in s['records'] if x['address']==s['selected']),None)
        previous=next((x for x in s['records'] if x['address']==s['previous']),None)
        series[c['service_id']].append(dict(time=r['sim_time'],time_after=r['sim_time_after'],paused=r['paused'],address=s['address'],
            speed=c['speed'],target=c['target_speed'],progress=s['progress'],physical=c['physicalized_raw'],train=c['train'],update=c['update_candidate_words']['0x144'],
            gate=c['stop_state_words']['0x214'],remaining=s['ai_wait']['0x210'],path_wait=c['stop_state_words']['0x1e8'],wait_elapsed=s['ai_wait']['0x1ec'],wait_duration=s['ai_wait']['0x1f0'],
            selected=s['selected'],selected_platform=selected['platform'] if selected else None,previous=s['previous'],previous_platform=previous['platform'] if previous else None,
            records=[{k:x[k] for k in ('address','platform','scheduled_arrival','recorded_arrival','scheduled_departure','recorded_departure','flags')} for x in s['records']]))
summary={}
for sid,rows in series.items():
    changes=[]
    def sig(r):return (r['gate'],r['selected'],r['previous'],r['speed']==0,r['physical'],r['update'])
    for before,after in zip(rows,rows[1:]):
        if sig(before)!=sig(after):
            changes.append(dict(before={k:v for k,v in before.items() if k!='records'},after={k:v for k,v in after.items() if k!='records'}))
    active=[r for r in rows if r['gate']]
    falling=[a['remaining']-b['remaining'] for a,b in zip(rows,rows[1:]) if a['gate'] and b['gate'] and a['remaining']>b['remaining']]
    paused=[(a,b) for a,b in zip(rows,rows[1:]) if a['paused'] and b['paused'] and a['gate'] and b['gate'] and a['time']==b['time']]
    summary[sid]=dict(samples=len(rows),active_samples=len(active),active_zero_speed=sum(r['speed']==0 for r in active),
        positive_gate_zero_remaining=sum(r['remaining']==0 for r in active),falling_pairs=len(falling),decrement_range=[min(falling),max(falling)] if falling else None,
        paused_active_pairs=len(paused),paused_remaining_changed=sum(a['remaining']!=b['remaining'] for a,b in paused),
        path_wait_nonzero=sum(bool(r['path_wait']) for r in rows),record_fields_changed=any(r['records']!=rows[0]['records'] for r in rows),
        initial=rows[0],final=rows[-1],changes=changes)
result=dict(capture=NAME,samples=len(raw),errors=len(raw)-len(good),clock_crossings=sum(r['sim_time']!=r['sim_time_after'] for r in good),
    unstable_services=sum(not s['selection_stable'] or not s['sentinel_stable'] or not s['wait_selection_stable'] or any(not x['node_stable'] for x in s['records']) for r in good for s in r['services']),
    nested_service_errors=sum('error' in s['service_context'] for r in good for s in r['services']),services=summary,
    final_time=good[-1]['sim_time'],final_paused=good[-1]['paused'],final_player=good[-1]['player'],
    limits='Sequential samples;same roots and clocks do not prove atomicity. Gate is AI platform countdown,distinct from path-wait dwell and player boarding. AI timetable/recorded-time writers are separate questions.')
(ROOT/'ai-platform-countdown-20261010-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='services'},indent=2))
for sid,s in summary.items():
    print(sid,{k:v for k,v in s.items() if k not in ('initial','final','changes')})
    for c in s['changes']:
        b,a=c['before'],c['after'];print('edge',sid,b['time'],a['time'],'gate',b['gate'],a['gate'],'remaining',a['remaining'],'speed',a['speed'],'selected',a['selected_platform'],'previous',a['previous_platform'],'physical',a['physical'])
