"""Relate observed vigilance latch edges to timers, clocks and brake state."""
import json,struct,collections
from pathlib import Path
root=Path(__file__).resolve().parent;name='monitor-alerter-enabled-01';rows=[json.loads(x) for x in (root/'captures'/name/'samples.jsonl').read_text().splitlines()];ok=[x for x in rows if 'error' not in x]
def vals(x):
 b=bytes.fromhex(x['monitors']['vigilance']['raw']);return struct.unpack('<4I4f',b[:32])
events=[]
for i,x in enumerate(ok):
 v=vals(x)
 if i and v[1:4]!=vals(ok[i-1])[1:4]:
  events.append(dict(before={k:ok[i-1][k] for k in ('day','physics_time','speed','brake_cylinder','brake_pipe','equalizing_reservoir')},after={k:x[k] for k in ('day','physics_time','speed','brake_cylinder','brake_pipe','equalizing_reservoir')},state_before=vals(ok[i-1]),state_after=v))
remaining=[vals(x)[4] for x in ok];alarm=[vals(x)[5] for x in ok]
report=dict(capture=name,samples=len(rows),events=events,monitor_delta_counts=dict(collections.Counter(b-a for a,b in zip(remaining,remaining[1:]) if a!=b)),alarm_delta_counts=dict(collections.Counter(b-a for a,b in zip(alarm,alarm[1:]) if a!=b)),field_ranges={k:[min(x[k] for x in ok),max(x[k] for x in ok)] for k in ('speed','brake_cylinder','brake_pipe','equalizing_reservoir')},final={k:ok[-1][k] for k in ('day','paused','vigilance_global','aws_global','speed','brake_cylinder','brake_pipe','equalizing_reservoir')},limitations='Observed ordering and physical response in one player run,not a universal causal isolation test;50ms sampling can miss intermediate writes. No warning audio recorded,acknowledgement or AI case.')
(root/'monitor-enabled-events.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
