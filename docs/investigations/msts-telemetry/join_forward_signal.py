"""Join paused forward-signal head to same-run infrastructure evidence."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
paths=[root/'captures/clearance-forward-signal-paused-01/details.jsonl',root/'captures/infrastructure-clearance-final-paused-01/owners.json',root/'captures/infrastructure-ai-clearance-01/samples.jsonl']
d=json.loads(paths[0].read_text(encoding='utf-8').splitlines()[0]);o=json.loads(paths[1].read_text(encoding='utf-8'))
assert d['paused'] and d['same_sim_time'] and d['iterator_stable'] and o['paused'] and o['paused_after']
assert d['sim_time']==o['sim_time']==o['sim_time_after']
h=d['next_signal']['selected_normal'];matches=[dict(database=db['address'],**i) for db in o['infrastructure']['databases'] for i in db['items'] if i['address']==h['address']]
assert len(matches)==1
m=matches[0];assert all(m[k]==h[k] for k in ('aspect','flags','definition','direction'))
history=[];last=None;observed=0
for index,line in enumerate(paths[2].read_text(encoding='utf-8').splitlines()):
    s=json.loads(line)
    if 'error' in s:raise ValueError('Cannot bridge capture error')
    heads=[x for x in s['signals'] if x['address']==h['address'] and x['definition']==h['definition']]
    assert len(heads)==1
    x=heads[0];assert x['index']==m['index'];observed+=1
    state={k:x[k] for k in ('aspect','flags','associated_service')}
    if state!=last:
        history.append(dict(sample=index,sim_time=s['sim_time'],sim_time_after=s['sim_time_after'],state=state));last=state
out=dict(sources=[dict(path=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths],paused_time=d['sim_time'],head=h['address'],definition=h['definition'],database=m['database'],database_item_index=m['index'],iterator_node=d['next_signal']['iterator'][0],iterator_item_index=h['index'],distance=d['next_signal']['distance'],observations=observed,history=history,limitations='Current paused iterator joined by exact head/definition to same-clock route snapshot. Historical pointer/definition continuity within this run supports attribution;iterator itself was not continuously captured. Iterator index46 and database index318 are different index spaces. Not a portable signal ID or all-mode/route validation. No screenshot from this new join;earlier separate Stop/Clear validation supplies aspect interpretation.')
(root/'forward-signal-clearance-join.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out))
