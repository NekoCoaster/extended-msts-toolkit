"""Summarize completed read-only clock captures without conflating load and wrap."""
import argparse
import hashlib
import json
from pathlib import Path


def compact(row):
    keys = ('utc', 'wall_elapsed', 'day', 'month', 'year', 'hour', 'minute',
            'second', 'elapsed', 'day_seconds', 'paused', 'player',
            'activity_start', 'clock_block_stable', 'step')
    return {key: row.get(key) for key in keys}


def analyse(rows):
    result = dict(samples=0, errors=0, unstable_clock_blocks=0,
                  wrap_candidates=[], resets_or_other_discontinuities=[],
                  calendar_changes=[], player_changes=[], paused_pairs=0,
                  paused_clock_changes=0, active_pairs=0, step_changes=[])
    previous = None
    first = last = None
    for row in rows:
        result['samples'] += 1
        if 'error' in row:
            result['errors'] += 1
            previous = None
            continue
        first = first or row
        last = row
        result['unstable_clock_blocks'] += not row['clock_block_stable']
        if previous is not None:
            pair = dict(before=compact(previous), after=compact(row))
            same_player = row['player'] == previous['player'] and row['player'] != 0
            same_start = row['activity_start'] == previous['activity_start']
            elapsed_delta = row['elapsed'] - previous['elapsed']
            day_delta = row['day_seconds'] - previous['day_seconds']
            pair.update(elapsed_delta=elapsed_delta, day_delta=day_delta)
            if row.get('step') != previous.get('step'):
                result['step_changes'].append(pair)
            if row['player'] != previous['player']:
                result['player_changes'].append(pair)
            if tuple(row[k] for k in ('day', 'month', 'year')) != tuple(previous[k] for k in ('day', 'month', 'year')):
                result['calendar_changes'].append(pair)
            if day_delta < 0 or elapsed_delta < 0:
                wrap = (same_player and same_start and elapsed_delta >= 0
                        and previous['day_seconds'] > 86000 and row['day_seconds'] < 1000)
                if wrap:
                    pair['wrapped_day_delta'] = day_delta + 86400
                    pair['derived_day_minus_start_after'] = row['day_seconds'] - row['activity_start']
                result['wrap_candidates' if wrap else 'resets_or_other_discontinuities'].append(pair)
            if same_player and same_start:
                if row['paused'] and previous['paused']:
                    result['paused_pairs'] += 1
                    result['paused_clock_changes'] += elapsed_delta != 0 or day_delta != 0
                elif not row['paused'] and not previous['paused']:
                    result['active_pairs'] += 1
        previous = row
    result['first'] = compact(first) if first else None
    result['last'] = compact(last) if last else None
    result['limits'] = ('External reads are sequential, not atomic; matching block rereads do not prove atomicity. '
                        'Wrap candidates require stable nonnull player and start-time, high-to-low day clock and '
                        'nondecreasing elapsed; inspect surrounding samples and UI/session evidence. '
                        'No month-end, leap-year, save restoration or narrative-date claim follows from one rollover.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('capture', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    completion_path = args.capture / 'completion.json'
    if not completion_path.is_file():
        parser.error('Capture is not complete; do not publish a partial analysis.')
    path = args.capture / 'samples.jsonl'
    raw = path.read_bytes()
    result = analyse(json.loads(line) for line in raw.splitlines())
    result['capture'] = args.capture.as_posix()
    result['samples_sha256'] = hashlib.sha256(raw).hexdigest()
    result['completion'] = json.loads(completion_path.read_text())
    assert result['samples'] == result['completion']['samples']
    assert result['errors'] == result['completion']['errors']
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: len(value) if isinstance(value, list) else value
                      for key, value in result.items()
                      if key in ('samples', 'errors', 'unstable_clock_blocks', 'wrap_candidates',
                                 'resets_or_other_discontinuities', 'calendar_changes')}))
