"""Summarize force accumulator availability without treating total force as drag."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent;capture='captures/body-accumulators-paused-01/accumulators.json';data=json.loads((root/capture).read_text());groups={}
for name,flag in [('player',True),('AI',False)]:
 rows=[x for x in data['vehicles'] if x['train']['is_player']==flag];valid=[x for x in rows if 'error' not in x]
 groups[name]=dict(vehicles=len(rows),errors=[x['error'] for x in rows if 'error'in x],nonzero_force=sum(any(v!=0 for v in x['force']) for x in valid),nonzero_torque=sum(any(v!=0 for v in x['torque']) for x in valid),unstable_identity=sum(not x['identity_stable'] for x in valid),unstable_state=sum(not x['state_stable'] for x in valid),unstable_definition=sum(not x['definition_stable'] for x in valid),example=valid[0] if valid else None)
report=dict(capture=capture,day=data['day'],paused=data['paused'],groups=groups,limitation='Total body accumulators contain multiple contributions. Paused values do not establish force decomposition,solver phase,AI dynamics or a standalone resistance measurement.')
(root/'body-accumulators-summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
