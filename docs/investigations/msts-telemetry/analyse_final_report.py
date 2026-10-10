"""Compare copied report records to the retained pre-exit player station list."""
import json
from pathlib import Path
R=Path(__file__).resolve().parent
before=json.loads((R/'captures/final-report-before-exit-20261010-01/report.json').read_text())['snapshot']
after=json.loads((R/'captures/final-report-after-exit-20261010-01/report.json').read_text())['snapshot']
live=json.loads((R/'captures/final-report-pre-exit-stations-20261010-01/samples.jsonl').read_text())
stations=next(s for s in live['services'] if s['is_player'])['records']
copied=after['stations']['records']
fields=('scheduled_arrival','recorded_arrival','scheduled_departure','recorded_departure','flags')
comparisons=[dict(index=i,platform=a['platform'],live_address=a['address'],report_address=b['address'],fields_equal=all(a[k]==b[k] for k in fields),missed_by_native_flags=bool(a['flags']&4) or not bool(a['flags']&2)) for i,(a,b) in enumerate(zip(stations,copied))]
assert before['station_count']==len(before['stations']['records'])==0
assert len(stations)==len(copied)==after['station_count']==5
assert all(x['fields_equal'] for x in comparisons)
assert sum(x['missed_by_native_flags'] for x in comparisons)==after['missed_stop_count']==4
assert after['action_count']==len(after['actions']['records'])==0
assert after['stations']['root_stable'] and all(x['node_stable'] for x in copied)
out=dict(before=before,after=after,station_comparison=comparisons,checks='Five copied time/flag records equal pre-exit source;count5,missed4 and empty action count/list agree.',limits='Post-finalization snapshot;no instruction execution trace,positive action record,nonzero deviation or successful-report result tested. UI11seconds compared to10.8515625;not generic rounding proof.')
(R/'final-report-20261010-summary.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['checks'])
