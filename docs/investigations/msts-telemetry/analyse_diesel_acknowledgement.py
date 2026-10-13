"""Summarize monitored emergency acknowledgement and separate effort snapshots."""
import json,struct
from pathlib import Path
root=Path(__file__).resolve().parent;rows=[json.loads(l) for l in (root/'captures/diesel-acknowledgement-01/samples.jsonl').read_text().splitlines()];v=[r for r in rows if 'error'not in r];changes=[];prev=None
for r in v:
 words=struct.unpack('<4I',bytes.fromhex(r['monitors']['emergency']['raw'])[:16])
 if words!=prev:changes.append(dict(day=r['day'],words=words,stable=r['monitors']['emergency']['stable']));prev=words
snapshots=[json.loads((root/'captures'/n/'gates.json').read_text()) for n in ['diesel-effort-gates-paused-01','diesel-effort-after-ack-01']]
report=dict(samples=len(rows),errors=len(rows)-len(v),day_range=[v[0]['day'],v[-1]['day']],paused_samples=sum(r['paused']!=0 for r in v),changes=changes,unstable_context=sum(not r['context_stable'] for r in v),unstable_monitors={n:sum(not r['monitors'][n]['stable'] for r in v) for n in v[0]['monitors']},speed_range=[min(r['speed'] for r in v),max(r['speed'] for r in v)],final=dict(day=v[-1]['day'],paused=v[-1]['paused'],speed=v[-1]['speed'],brake_flags=v[-1]['brake_flags']),effort_snapshots=[dict(day=r['day'],paused=r['paused'],values=r['values'],cut_gate=r['cut_gate_conjunction'],stable=r['fields_stable'] and r['identity_stable']) for r in snapshots],limitations='Semicolon toContinuousService thenZ,thenN1 with brakes held,Idle,Pause. Monitor stream does not sample controller370 or current;separate guarded snapshots do. After-ack snapshot is running despite legacy boilerplate sayingPaused;its paused0 field and UI are authoritative. Exact Z event time and prior rollback cause not established;current is not wheel force.')
(root/'diesel-acknowledgement-summary.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
