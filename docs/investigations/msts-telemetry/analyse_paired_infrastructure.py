"""Summarize paired sequential reads, retaining nested failures and join ambiguity."""
import argparse, collections, hashlib, json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('name')
a = p.parse_args()
if Path(a.name).name != a.name or a.name in ('.', '..'):
    p.error('Invalid capture name')
root = Path(__file__).resolve().parent
source = root / 'captures' / a.name / 'samples.jsonl'
errors, joins, observations, counts, speeds, cab = [], [], [], [], [], collections.defaultdict(list)
windows, origin_stability, iterator_stability = [], [], []
with source.open(encoding='utf-8') as f:
    for index, line in enumerate(f):
        row = json.loads(line)
        def nested_errors(value, path=''):
            if isinstance(value, dict):
                for k, v in value.items():
                    if k == 'error' or k.endswith('_error'):
                        errors.append(dict(sample=index, path=path + '/' + k, value=v))
                    else:
                        nested_errors(v, path + '/' + k)
            elif isinstance(value, list):
                for j, v in enumerate(value):
                    nested_errors(v, path + '/' + str(j))
        nested_errors(row)
        if 'error' in row:
            continue
        detail, tracks = row['monitor_and_cab'], row['physical_tracks']
        windows.append(row['monotonic_after'] - row['monotonic'])
        origin_stability.append(tracks['origin_stable'])
        iterator_stability.append(detail['iterator_stable'])
        speeds.append(detail['player']['speed'])
        for k, v in detail.get('diesel_cab', {}).items():
            cab[k].append(v)
        counts.append(dict(sample=index, time=row['sim_time'], time_after=row['sim_time_after'],
                           physical_cars=sum(len(t['cars']) for t in tracks['trains']),
                           physical_trains=len(tracks['trains'])))
        signal = detail.get('next_signal', {})
        head = signal.get('selected_normal')
        matches = [s for s in row['signals'] if head and s['address'] == head['address']
                   and s['definition'] == head['definition']]
        joins.append(dict(sample=index, matches=len(matches),
                          aspect_equal=matches[0]['aspect'] == head['aspect'] if len(matches) == 1 else None))
        observations.append(dict(iterator=signal.get('iterator'), distance=signal.get('distance'),
                                 head=head, database_index=matches[0]['index'] if len(matches) == 1 else None))
transitions = [dict(before=x, after=y) for x, y in zip(counts, counts[1:])
               if (x['physical_cars'], x['physical_trains']) != (y['physical_cars'], y['physical_trains'])]
out = dict(source=str(source.relative_to(root)), sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
           samples=len(joins), nested_errors=errors, max_read_seconds=max(windows),
           unstable_origins=origin_stability.count(False), unstable_iterators=iterator_stability.count(False),
           signal_join_counts=dict(collections.Counter(j['matches'] for j in joins)),
           signal_aspect_disagreements=[j for j in joins if j['aspect_equal'] is False],
           distinct_monitor_states=[json.loads(s) for s in sorted({json.dumps(o, sort_keys=True) for o in observations})],
           player_speed_range=[min(speeds), max(speeds)],
           cab_ranges={k: [min(v), max(v)] for k, v in cab.items()},
           physical_count_transitions=transitions,
           limitations='Infrastructure, monitor and physical tracks are successive phases, not an atomic snapshot. '
           'Pointer/clock rereads cannot exclude intermediate mutations or pointer reuse. '
           'Stationary monitor continuity does not validate moving distance updates or node crossing. '
           'Read duration is not a measurement of gameplay performance impact.')
(root / (a.name + '-paired-summary.json')).write_text(json.dumps(out, indent=2), encoding='utf-8')
print(json.dumps(out, indent=2))
