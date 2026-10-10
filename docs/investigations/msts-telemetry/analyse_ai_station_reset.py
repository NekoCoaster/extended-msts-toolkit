"""AI gate, physical-instance and station selection edges; sampled bounds only."""
import json
from pathlib import Path

root=Path(__file__).resolve().parent
name='tokyo-ai-end-context-20261010-01'
rows=[json.loads(s) for s in (root/'captures'/name/'samples.jsonl').read_text().splitlines()]
good=[r for r in rows if 'error' not in r]
services={}
for r in good:
    for s in r['services']:
        if s['is_player']:continue
        c=s['service_context']
        key=str(c['service_id'])
        services.setdefault(key,[]).append(dict(start=r['sim_time'],end=r['sim_time_after'],paused=r['paused'],address=s['address'],selected=s['selected'],previous=s['previous'],progress=s['progress'],context=c))
result=dict(capture=name,samples=len(rows),errors=len(rows)-len(good),
    clock_crossings=sum(r['sim_time']!=r['sim_time_after'] for r in good),
    context_errors=sum('error' in s.get('service_context',{}) for r in good for s in r['services']),
    unstable_services=sum(not s['selection_stable'] or not s['sentinel_stable'] or any(not c['node_stable'] for c in s['records']) for r in good for s in r['services']),
    time_range=[good[0]['sim_time'],good[-1]['sim_time_after']],final_paused=good[-1]['paused'],services={})
for key,seq in services.items():
    changes=[];last=None;previous=None
    for r in seq:
        c=r['context']
        signature=(r['address'],r['selected'],r['previous'],c.get('train'),c.get('physicalized_raw'),c.get('update_candidate_words',{}).get('0x144'),tuple(c.get('stop_state_words',{}).items()))
        if signature!=last:
            changes.append(dict(previous_observation=previous,observation=r))
        last=signature;previous=r
    inactive=[r for r in seq if r['context'].get('update_candidate_words',{}).get('0x144')==0]
    result['services'][key]=dict(changes=changes,inactive_samples=len(inactive),
        inactive_speeds=sorted({r['context']['speed'] for r in inactive}),
        inactive_progress=sorted({r['progress'] for r in inactive}),
        inactive_last_updates=sorted({r['context']['update_candidate_floats']['0x150'] for r in inactive}),
        final=seq[-1])
result['limitations']='Sequential reads of registry context and station fields, not atomic native events. Context errors and pointer checks are limited checks. A retained positive speed with an inactive gate is not proof of current movement. Native byte comparison covers exported ranges only.'
(root/'ai-station-reset-20261010-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='services'},indent=2))
for key,v in result['services'].items():
    print(key,json.dumps({k:x for k,x in v.items() if k not in ('changes','final')}))
    for t in v['changes']:
        b=t['previous_observation'];r=t['observation'];c=r['context']
        print('edge',b['start'] if b else None,r['start'],'selected',r['selected'],'progress',r['progress'],'gate',c['update_candidate_words']['0x144'],'physical',c['physicalized_raw'],'speed',c['speed'],'stop',c['stop_state_words'])
