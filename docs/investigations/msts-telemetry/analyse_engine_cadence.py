"""Cadence and mass-balance checks for unchanged steam controls."""
from pathlib import Path
import json,statistics
root=Path(__file__).resolve().parent
rows=[json.loads(x) for x in (root/'captures/steam-cadence-01/samples.jsonl').read_text(encoding='utf-8').splitlines()]
s=[x for x in rows if 'error' not in x];pairs=[];drops=0
for a,b in zip(s,s[1:]):
 if b['fire_mass']!=a['fire_mass']:
  drops+=1
  if b['fire_mass']<a['fire_mass']:
   predicted=b['burn']*b['interval']/3600
   pairs.append(dict(clock=b['clock'],drop=a['fire_mass']-b['fire_mass'],predicted=predicted,error=a['fire_mass']-b['fire_mass']-predicted))
a,b=s[0],s[-1]
result=dict(samples=len(s),errors=[x for x in rows if 'error'in x],unstable=sum(not x['stable'] for x in s),cross_step=sum(x['clock']!=x['clock_after'] for x in s),paused=sum(bool(x['paused']) for x in s),elapsed_clock=b['clock']-a['clock'],elapsed_physics=b['physics_time']-a['physics_time'],intervals=sorted(set(x['interval'] for x in s)),fire_mass_changes=drops,falling_pairs=len(pairs),max_mass_balance_error=max(abs(x['error']) for x in pairs) if pairs else None,first=a,last=b,limitations='Non-atomic external reads; missed/overlapping updates can invalidate adjacent-pair equations. Physics accumulator advance is compared with independently stored seconds clock; no stock timing claim.')
(root/'steam-cadence-summary.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(root/'steam-cadence-mass-checks.json').write_text(json.dumps(pairs,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
