"""Describe completed aggregate captures; never infer cadence from polling rate."""
import argparse
import hashlib
import json
from pathlib import Path


def analyse(rows):
    good = [r for r in rows if 'error' not in r and r.get('available')]
    def bounds(key):
        values = [r[key] for r in good]
        return [min(values), max(values)] if values else None
    coherent = [r for r in good if r['complete'] and r['roots_stable']
                and r['aggregate_stable'] and r['history_stable']
                and r['history_index_valid'] and r['cars']
                and all(c['stable'] and c['owner'] == r['train'] for c in r['cars'])]
    differences=[]
    for before, after in zip(rows, rows[1:]):
        if ('error' in before or 'error' in after or not before.get('available')
                or not after.get('available') or before['train']!=after['train']
                or before['paused'] or after['paused']):
            continue
        dt=after['time']-before['time']
        if dt>0:
            differences.append((after['speed']-before['speed'])/dt-after['acceleration'])
    return dict(samples=len(rows), errors=sum('error' in r for r in rows),
                available=len(good), speed_range=bounds('speed'),
                acceleration_range=bounds('acceleration'),
                unfiltered_mean_range=bounds('unfiltered_mean'),
                car_counts=sorted({len(r['cars']) for r in good}),
                indexes=sorted({r['history_index'] for r in good}),
                root_changes=sum(not r['roots_stable'] for r in good),
                unstable_aggregate=sum(not r['aggregate_stable'] for r in good),
                unstable_history=sum(not r['history_stable'] for r in good),
                unstable_cars=sum(not c['stable'] for r in good for c in r['cars']),
                owner_mismatches=sum(c['owner'] != r['train'] for r in good for c in r['cars']),
                incomplete=sum(not r['complete'] for r in good),
                invalid_index=sum(not r['history_index_valid'] for r in good),
                clock_crossings=sum(r['time'] != r['time_after'] for r in good),
                coherent_read_rows=len(coherent),
                finite_difference_pairs=len(differences),
                max_abs_finite_difference_minus_stored=max(map(abs,differences),default=None),
                max_abs_stored_minus_unfiltered=max((abs(r['acceleration']-r['unfiltered_mean']) for r in coherent),default=None),
                max_sampled_mean_difference=max((abs(r['sampled_car_mean']-r['unfiltered_mean']) for r in coherent), default=None),
                time=[good[0]['time'],good[-1]['time']] if good else None,
                paused_values=sorted({r['paused'] for r in good}),
                limits='Sequential read consistency flags do not establish atomicity or exclude ABA reuse. '
                       'Sampled car mean may differ from earlier producer input. Finite differences span observed clock intervals, '
                       'not exact producer invocations; differences are descriptive,not a physical error estimate. '
                       'No reset,AI freshness or exact cadence claim follows from this summary.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('capture', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    completion_path = a.capture/'completion.json'
    if not completion_path.is_file():
        p.error('Capture must be complete')
    source = a.capture/'samples.jsonl'
    raw = source.read_bytes()
    result = analyse([json.loads(line) for line in raw.splitlines()])
    completion = json.loads(completion_path.read_text())
    assert result['samples'] == completion['samples']
    assert result['errors'] == completion['errors']
    result.update(source=source.as_posix(), sha256=hashlib.sha256(raw).hexdigest(), completion=completion)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
