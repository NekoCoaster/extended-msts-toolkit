"""Summarize observed edges; repeated buffer rows are not extra input events."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent;p=root/'captures/keyboard-shift-paused-01/samples.jsonl'
rows=[json.loads(x) for x in p.read_text().splitlines()];good=[r for r in rows if 'error' not in r]
edges=[];previous=None
for r in good:
    if r['held']!=previous:edges.append(dict(t=r['t'],held=r['held'],stable_bits=r['stable_bits']));previous=r['held']
records={}
for r in good:
    for record in r['records']:
        key=tuple(record)
        if key not in records:records[key]=dict(words=record,first_t=r['t'],last_t=r['t'],observations=0,stable_header_observations=0)
        records[key]['last_t']=r['t'];records[key]['observations']+=1;records[key]['stable_header_observations']+=r['stable_header']
out=dict(source=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),samples=len(rows),errors=sum('error' in r for r in rows),
    first_t=rows[0]['t'],last_t=rows[-1]['t'],paused_values=sorted({r['paused'] for r in good}),dayclock_values=sorted({r['dayclock'] for r in good}),
    observed_held_edges=edges,held_sample_count=sum(bool(r['held']) for r in good),buffer_nonempty_samples=sum(bool(r['records']) for r in good),
    distinct_buffer_records=list(records.values()),nonempty_buffer_headers=[dict(t=r['t'],cursor=r['cursor'],count=r['count'],capacity=r['capacity']) for r in good if r['records']],unstable_headers=sum(not r['stable_header'] for r in good),unstable_bits=sum(not r['stable_bits'] for r in good),
    max_read_s=max(r['read_s'] for r in rows),max_sample_gap_s=max(b['t']-a['t'] for a,b in zip(rows,rows[1:])),
    limitations='One Shift_L press issued through computer-use while pause dialog visible. Sequential samples can miss edges/events; distinct raw buffer records are not a guaranteed event log. No gameplay command dispatch or timing/overhead guarantee inferred.')
(root/'keyboard-transition-summary.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
