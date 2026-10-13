"""Compare consecutive scheduler states with the native target-capped integration rule."""
import json,struct
from pathlib import Path
root=Path(__file__).resolve().parent
rows=[json.loads(x) for x in (root/'captures/ai-systems-moving-02/samples.jsonl').read_text(encoding='utf-8').splitlines()]
states=[];disagreements=0
for index,row in enumerate(rows):
    if row.get('paused') or 'error' in row:continue
    for s in row['service_registry']['entries']:
        if s.get('train_id')!=400005 or 'error' in s:continue
        t=next((t for t in row['trains'] if t['id']==400005),None)
        if t and any(s[k]!=t['service'][v] for k,v in [('speed','speed'),('target_speed','target'),('acceleration','acceleration')]):disagreements+=1
        state=dict(index=index,sim_time=row['sim_time'],scheduler_time=s['update_candidate_floats']['0x150'],interval=s['update_candidate_floats']['0x14c'],speed=s['speed'],target=s['target_speed'],acceleration=s['acceleration'],sign=s['stop_state_words']['0x1dc'])
        if not states or state['scheduler_time']!=states[-1]['scheduler_time']:states.append(state)
comparisons=[]
for old,new in zip(states,states[1:]):
    dt=new['scheduler_time']-old['scheduler_time']
    if dt!=old['interval'] or old['sign']!=1 or new['sign']!=1:continue
    v=abs(old['speed']);a=old['acceleration'];target=old['target']
    reach=abs((target-v)/a) if a else None
    prediction=v if not a else target if reach<=dt else v+a*dt
    rounded=struct.unpack('<f',struct.pack('<f',prediction))[0]
    comparisons.append(dict(from_index=old['index'],to_index=new['index'],dt=dt,predicted=rounded,observed=new['speed'],residual=new['speed']-rounded,target_capped=bool(a and reach<=dt)))
extreme=min(states,key=lambda x:x['acceleration'])
out=dict(capture='ai-systems-moving-02',scheduler_states=states,comparisons=comparisons,summary=dict(states=len(states),comparisons=len(comparisons),exact=sum(x['residual']==0 for x in comparisons),max_abs_residual=max((abs(x['residual']) for x in comparisons),default=None),two_read_disagreements=disagreements),most_negative_state=extreme,extreme_target_reach_seconds=abs((extreme['target']-abs(extreme['speed']))/extreme['acceleration']),limitations='First observed state per scheduler time; sequential reads can straddle producers. Positive travel sign and consecutive nominal intervals only. Float32 final rounding, not full x87 emulation. This tests service integration, not wheel acceleration or comfort forces.')
(root/'ai-acceleration-summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k not in ('scheduler_states','comparisons')}))
