"""Summarize the retained opening capture; excludes its broken service_stable check."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
source = ROOT / 'captures/automatic-opening-20261013-01/samples.jsonl'
rows = [json.loads(line) for line in source.read_text().splitlines()]
valid = []
for i, row in enumerate(rows):
    player = next((s for s in row.get('services', []) if s['is_player']), None)
    if player is not None:
        valid.append((i, row, player))


def compact(item):
    i, row, service = item
    return dict(sample=i, time=row['sim_time'], speed=row['player']['speed'],
                driver_gate=row['automatic_driver']['gate'],
                control_type=row['automatic_driver']['control_type'],
                selected=service['selected'], previous=service['previous'],
                remaining=service['ai_wait']['0x210'],
                gate=service['service_context'].get('stop_state_words', {}).get('0x214'),
                records=[{k: r[k] for k in ('platform', 'flags', 'recorded_arrival', 'recorded_departure')}
                         for r in service['records']])


edges = []
for before, after in zip(valid, valid[1:]):
    a, b = compact(before), compact(after)
    if any(a[k] != b[k] for k in ('selected', 'previous', 'gate', 'records')):
        edges.append(dict(before=a, after=b, adjacent=after[0] == before[0] + 1))
active = [item for item in valid if item[2]['ai_wait']['0x210'] > 0]
report = dict(source=source.relative_to(ROOT).as_posix(),
              source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              samples=len(rows), errors=sum('error' in r for r in rows),
              unavailable=sum(r.get('available') is False for r in rows),
              player_samples=len(valid), positive_countdown_samples=len(active),
              first=compact(valid[0]), last=compact(valid[-1]),
              first_positive=compact(active[0]), last_positive=compact(active[-1]), edges=edges,
              station_guard_failures=sum(not s['selection_stable'] or not s['sentinel_stable'] or
                  not s['wait_selection_stable'] or any(not x['node_stable'] for x in s['records'])
                  for _, _, s in valid),
              clock_crossings=sum(r['sim_time'] != r['sim_time_after'] for _, r, _ in valid),
              limitations='Opening initialization/hold, not arrival after a journey. service_stable is invalid in this archived probe because a loop variable shadows the numeric service pointer; excluded. Other equal rereads do not prove atomicity. No instruction execution trace.')
(ROOT / 'automatic-opening-20261013-summary.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({k: report[k] for k in ('samples', 'errors', 'unavailable', 'player_samples',
                                       'positive_countdown_samples', 'station_guard_failures', 'clock_crossings')}))
print(json.dumps(report['edges'], indent=2))
