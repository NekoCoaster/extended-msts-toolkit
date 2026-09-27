"""Summarize retained forward-start and next-signal transition evidence."""
import json
import argparse
from pathlib import Path

root = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--name', default='player-cleared-passage-01')
args = parser.parse_args()
source = root / 'captures' / args.name / 'details.jsonl'
raw = [json.loads(line) for line in source.read_text().splitlines()]
rows = [r for r in raw if 'error' not in r and 'next_signal' in r]

def compact(r):
    return {k: r[k] for k in ('utc', 'sim_time', 'paused', 'player',
                              'next_signal', 'diesel_cab', 'same_sim_time',
                              'iterator_stable')}

transitions = []
for before, after in zip(rows, rows[1:]):
    if before['next_signal']['iterator'] != after['next_signal']['iterator']:
        transitions.append({'before': compact(before), 'after': compact(after)})

report = dict(
    source=str(source.relative_to(root)), samples=len(raw),
    errors=sum('error' in r for r in raw),
    signal_errors=sum('signal_error' in r for r in raw),
    paused_samples=sum(r['paused'] != 0 for r in rows),
    clock_crossings=sum(not r['same_sim_time'] for r in rows),
    iterator_reread_differences=sum(not r['iterator_stable'] for r in rows),
    day_range=[rows[0]['sim_time'], rows[-1]['sim_time']],
    signed_speed_range=[min(r['player']['speed'] for r in rows),
                        max(r['player']['speed'] for r in rows)],
    throttle_values=sorted({r['diesel_cab']['throttle'] for r in rows}),
    traction_current_range=[min(r['diesel_cab']['current_traction_amps'] for r in rows),
                            max(r['diesel_cab']['current_traction_amps'] for r in rows)],
    iterator_transitions=transitions, first=compact(rows[0]), last=compact(rows[-1]),
    limitations='External reads are asynchronous. Consecutive rows bracket observed iterator changes, not exact geometric crossing or native event time. Iterator indices are node-table-local. This stream does not capture speedpost or track-node topology transitions independently.'
)
(root / f'{args.name}-summary.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
