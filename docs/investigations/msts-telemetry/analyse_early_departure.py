"""Sampled player departure while boarding is active; no atomicity assumption."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
NAME='tokyo-early-departure-20261010-01'
rows=[json.loads(s) for s in (ROOT/'captures'/NAME/'samples.jsonl').read_text().splitlines()]
good=[r for r in rows if 'error' not in r]
seq=[]
for r in good:
    p=next(s for s in r['services'] if s['is_player'])
    rec=next(s for s in p['records'] if s['platform']==70)
    seq.append(dict(time=r['sim_time'],time_after=r['sim_time_after'],paused=r['paused'],speed=r['player']['speed'],
        service_speed=p['service_context']['speed'],active=r['activity']['boarding_active'],remaining=r['activity']['remaining'],stop=r['activity']['stop'],success=r['activity']['success'],
        selected=p['selected'],previous=p['previous'],record=rec))
changes=[];previous=None
for r in seq:
    sig=lambda x:(x['active'],x['selected'],x['previous'],x['record']['flags'],x['record']['recorded_arrival'],x['record']['recorded_departure'])
    if previous is None or sig(previous)!=sig(r):changes.append(dict(before=previous,after=r))
    previous=r
result=dict(capture=NAME,samples=len(rows),errors=len(rows)-len(good),
    clock_crossings=sum(r['sim_time']!=r['sim_time_after'] for r in good),
    unstable_services=sum(not s['selection_stable'] or not s['sentinel_stable'] or any(not x['node_stable'] for x in s['records']) for r in good for s in r['services']),
    active_samples=sum(r['active']!=0 for r in seq),changes=changes,final=seq[-1],
    limitations='Sequential reads,not atomic branch tracing. Early departure relative to unfinished loading,not necessarily before scheduled time. Flags are branch-local;no global failure/result inference.')
(ROOT/'early-departure-20261010-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('changes','final')},indent=2))
for x in changes:
    a=x['after'];b=x['before'];print('edge',b['time'] if b else None,a['time'],'speed',a['speed'],'active',a['active'],'remaining',a['remaining'],'flags',hex(a['record']['flags']),'departure',a['record']['recorded_departure'],'selected',a['selected'],'prior remaining',b['remaining'] if b else None)
print('final',result['final']['time'],result['final']['paused'],result['final']['speed'])
