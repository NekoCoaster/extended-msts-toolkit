"""Summarize fixed-global transitions without interpreting pointers as readiness."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
NAME='tokyo-result-reset-20261010-01'
rows=[json.loads(x) for x in (ROOT/'captures'/NAME/'samples.jsonl').read_text().splitlines()]
good=[x for x in rows if 'error' not in x]
fields=('paused','player','controller','control_type','station_sentinel','selected','previous','event_sentinel','stop','success','boarding_active')
changes=[];resets=[];previous=None
for row in good:
    if previous is None or any(row[k]!=previous[k] for k in fields):changes.append(dict(before=previous,after=row))
    if previous and (row['elapsed']<previous['elapsed'] or row['day_seconds']<previous['day_seconds']):resets.append(dict(before=previous,after=row))
    previous=row
result=dict(capture=NAME,samples=len(rows),errors=len(rows)-len(good),clock_crossings=sum(x['day_seconds']!=x['day_seconds_after'] for x in good),
    transitions=changes,clock_decreases=resets,final=good[-1],
    stale_selected_without_station_root_samples=sum(not x['station_sentinel'] and bool(x['selected']) for x in good),
    zero_result_without_player_samples=sum(not x['player'] and not x['stop'] and not x['success'] for x in good),
    limits='Sequential read-only fixed globals. Pointer values may be stale during unload/loading;no heap dereference,atomicity or load-complete detector. UI observations establish phase separately.')
(ROOT/'session-reset-20261010-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ('transitions','clock_decreases','final')},indent=2))
for x in changes:
    a=x['after'];print('edge',a['wall_elapsed'],a['day_seconds'],{k:a[k] for k in fields})
for x in resets:print('clock decrease',x['before']['wall_elapsed'],x['after']['wall_elapsed'],x['before']['elapsed'],x['after']['elapsed'],x['before']['day_seconds'],x['after']['day_seconds'])
print('final',good[-1])
