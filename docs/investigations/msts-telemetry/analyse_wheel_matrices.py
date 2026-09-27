"""Compare retained wheel matrices without assigning angles or world-pose semantics."""
import argparse,collections,json,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args();root=Path(__file__).resolve().parent
if Path(a.name).name!=a.name:p.error('Invalid name')
rows=[json.loads(x) for x in (root/'captures'/a.name/'samples.jsonl').read_text().splitlines()];stats={};prev={};errors=[]
for row in rows:
 if 'error'in row:errors.append(row['error']);continue
 for v in row['vehicles']:
  key=str(v['object_id']);s=stats.setdefault(key,dict(kind=v['kind'],train=v['train'],samples=0,errors=[],unstable_identity=0,unstable_layout=0,unstable_matrix_reads=0,changed_matrices=0,stable_transition_changes=0,changes_between_paused_samples=0,changed_float_indices=set(),matrix_indices=set(),rate_min=v['rate'],rate_max=v['rate']))
  s['samples']+=1;s['rate_min']=min(s['rate_min'],v['rate']);s['rate_max']=max(s['rate_max'],v['rate'])
  if 'error'in v:s['errors'].append(v['error']);continue
  s['unstable_identity']+=not v['identity_stable'];s['unstable_layout']+=v.get('context_changed',False) or not v.get('layout_stable',True)
  for m in v['matrices']:
   s['matrix_indices'].add(m['index']);s['unstable_matrix_reads']+=not m['stable'];mk=(key,v['car'],v['shape'],m['index'],m['pointer']);old=prev.get(mk)
   if old and old[0]!=m['raw']:
    s['changed_matrices']+=1;s['stable_transition_changes']+=bool(old[2] and m['stable'] and v['identity_stable'] and not v.get('context_changed',False) and v.get('layout_stable',True));s['changes_between_paused_samples']+=bool(row['paused'] and old[1]);av=struct.unpack('<12f',bytes.fromhex(old[0]));bv=struct.unpack('<12f',bytes.fromhex(m['raw']));s['changed_float_indices'].update(i for i,(x,y) in enumerate(zip(av,bv)) if x!=y)
   prev[mk]=(m['raw'],row['paused'],m['stable'] and v['identity_stable'] and not v.get('context_changed',False) and v.get('layout_stable',True))
for s in stats.values():
 for k in ('changed_float_indices','matrix_indices'):s[k]=sorted(s[k])
report=dict(capture=a.name,samples=len(rows),outer_errors=errors,paused_samples=sum(bool(x.get('paused')) for x in rows),day_range=[min(x['day'] for x in rows if 'day'in x),max(x['day'] for x in rows if 'day'in x)],last={k:rows[-1].get(k) for k in ('day','paused')},vehicles=stats,limitations='One representative per player/AI and shape-kind class per sample,not all vehicles. Changes are stored-matrix observations,not visible wheel-angle/world-pose or per-frame cadence proof. Sequential reads may straddle updates;callback entry is hooked in this installation.')
(root/(a.name+'-summary.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report))
