"""Reproduce bounded statistics without treating non-atomic reads as exact frames."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
source='captures/steam-scotsman-controls-01/samples.jsonl'
records=[json.loads(line) for line in (ROOT/source).read_text(encoding='utf-8').splitlines()]
samples=[r['snapshot'] for r in records if 'snapshot' in r]
channels={}
for name in samples[0]['values']:
    values=[s['values'][name]['raw'] for s in samples]
    transitions=[dict(index=i,time=samples[i]['sim_time'],value=v) for i,v in enumerate(values) if i==0 or v!=values[i-1]]
    channels[name]=dict(min=min(values),max=max(values),first=values[0],last=values[-1],changes=len(transitions)-1)
    if len(transitions)<=10:channels[name]['transitions']=transitions
result=dict(source=source,samples=len(samples),errors=[r for r in records if 'error' in r],
    unstable_contexts=sum(not s['context_stable'] for s in samples),
    cross_step_reads=sum(s['sim_time']!=s['sim_time_after'] for s in samples),
    paused_samples=sum(bool(s['paused']) for s in samples),
    time_range=[samples[0]['sim_time'],samples[-1]['sim_time']],
    speed_range=[min(s['train_speed'] for s in samples),max(s['train_speed'] for s in samples)],
    channels=channels,limitations='External non-atomic reads. Later final paused snapshot is separate; constant channels are not actuator validation.')
(ROOT/'steam-runtime-summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
