"""Guard-qualified sampled body state variation, not native producer-rate estimation."""
import collections,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent;source=root/'captures/body-accumulators-series-20261013-01/samples.jsonl';rows=[json.loads(x) for x in source.read_text().splitlines()]
states={};errors=0;excluded=collections.Counter();accepted=0
for x in rows:
 if 'error' in x:errors+=1;continue
 for v in x['vehicles']:
  reason='vehicle_error' if 'error' in v else 'population' if not x['population_available'] or not x['manager_stable'] else 'clock_crossing' if x['clock']!=x['clock_after'] else 'identity' if not v['identity_stable'] else 'state_change' if not v['state_stable'] else None
  if reason:excluded[reason]+=1;continue
  accepted+=1;key=(v['object_id'],v['car'],v['body'],v['owner']);group='ownerless' if v['train'] is None else 'player' if v['train']['is_player'] else 'ai'
  item=states.setdefault(key,dict(group=group,force=set(),torque=set(),velocity=set(),count=0,clocks=set()))
  item['count']+=1;item['clocks'].add(x['clock'])
  for field in ['force','torque','velocity']:item[field].add(tuple(v[field]))
groups={}
for key,v in states.items():
 g=groups.setdefault(v['group'],dict(body_identities=0,accepted_observations=0,varying_force_identities=0,varying_velocity_identities=0,nonzero_force_identities=0,nonzero_torque_identities=0,nonzero_velocity_identities=0))
 g['body_identities']+=1;g['accepted_observations']+=v['count'];g['varying_force_identities']+=len(v['force'])>1;g['varying_velocity_identities']+=len(v['velocity'])>1
 for field in ['force','torque','velocity']:g['nonzero_'+field+'_identities']+=any(any(a) for a in v[field])
result=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),samples=len(rows),outer_errors=errors,clock_range=[min(x['clock'] for x in rows if 'clock'in x),max(x['clock_after'] for x in rows if 'clock_after'in x)],paused_samples=sum(x.get('paused')==1 for x in rows),clock_crossing_samples=sum(x.get('clock')!=x.get('clock_after') for x in rows if 'clock'in x),excluded_vehicle_observations=dict(excluded),groups=groups,limitation='Counts are body identities,not unique vehicles:buffer swaps can split one car. Guard-passing distinct stored values are sampled variation,not producer cadence,force decomposition or proof of independent AI dynamics. Ownerless label uses registry ownership mapping.')
(root/'body-accumulators-series-20261013-summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
