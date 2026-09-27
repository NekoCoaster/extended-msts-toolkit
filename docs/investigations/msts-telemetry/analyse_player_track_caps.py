"""Analyze paired track and finite-input speed-cap captures without joining gaps."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('name')
a = p.parse_args()
if Path(a.name).name != a.name:
    p.error('Invalid capture name')
root = Path(__file__).resolve().parent
source = root / 'captures' / a.name / 'samples.jsonl'
raw = [json.loads(s) for s in source.read_text().splitlines()]
previous_tracks = {}
previous_caps = {}
events = []
cap_events = []
errors = []
caps = []
good = []
signal_events = []
previous_signal = None
for i, row in enumerate(raw):
    if 'error' in row:
        errors.append(dict(sample=i, error=row['error']))
        previous_tracks = {}
        previous_caps = {}
        previous_signal = None
        continue
    good.append(row)
    signal = row.get('next_signal')
    if signal:
        current_signal = dict(sample=i, time=row['sim_time'], signal=signal,
                              iterator_stable=row['iterator_stable'], same_sim_time=row['same_sim_time'])
        signature = lambda s: (s['iterator'], [(h['address'], h['aspect']) for h in s['heads']])
        if previous_signal and signature(previous_signal['signal']) != signature(signal):
            signal_events.append(dict(before=previous_signal, after=current_signal))
        previous_signal = current_signal
    now = {}
    for train in row['physical_tracks']['trains']:
        tracks = [('service', None, train.get('service_track'))]
        tracks += [(c['address'], c['body'], c.get('track')) for c in train['cars']]
        for identity, body, track in tracks:
            if track is None:
                errors.append(dict(sample=i, identity=identity, error='Track unavailable'))
                continue
            key = (train['train'], identity)
            value = dict(sample=i, time=row['sim_time'], end_time=row['end_time'],
                         node=track['node'], section=track['section_index'],
                         direction=track['direction'], distance=track['node_distance'],
                         body=body, is_player=train['is_player'])
            now[key] = value
            old = previous_tracks.get(key)
            if old and old['body'] == body and (old['node'], old['section']) != (value['node'], value['section']):
                events.append(dict(train=key[0], identity=identity, before=old, after=value,
                                   node_changed=old['node'] != value['node']))
    previous_tracks = now
    current_caps = {}
    for cap in row['speed_caps']['services']:
        caps.append(cap)
        value = dict(sample=i, time=row['speed_caps']['sim_time'],
                     end_time=row['speed_caps']['sim_time_after'],
                     is_player=cap['is_player'], flags=cap['flags'], update_gate=cap['update_gate'],
                     fields={k:v['value'] for k,v in cap['fields'].items()},
                     reproduced=cap['reproduced'], source=cap['limiting_source'],
                     matches=cap['matches'])
        key = cap['address']
        current_caps[key] = value
        old = previous_caps.get(key)
        if old and (old['fields'], old['source'], old['flags'], old['update_gate']) != (value['fields'], value['source'], value['flags'], value['update_gate']):
            cap_events.append(dict(service=key, before=old, after=value))
    previous_caps = current_caps

report = dict(source=str(source.relative_to(root)), sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              samples=len(raw), errors=errors, paused_samples=sum(bool(r['paused']) for r in good),
              time_range=[good[0]['sim_time'], good[-1]['end_time']],
              speed_range=[min(r['player']['speed'] for r in good), max(r['player']['speed'] for r in good)],
              clock_crossings=sum(r['sim_time'] != r['end_time'] for r in good),
              player_pointer_differences=sum(not r['player_pointer_stable'] for r in good),
              origin_reread_differences=sum(not r['physical_tracks']['origin_stable'] for r in good),
              cap_reproductions=len(caps), cap_mismatches=sum(not c['matches'] for c in caps),
              mismatches_by_service={str(s):dict(count=sum(not c['matches'] for c in caps if c['address']==s), update_gates=sorted({c['update_gate'] for c in caps if c['address']==s and not c['matches']})) for s in sorted({c['address'] for c in caps})},
              track_changes=len(events), node_changes=sum(e['node_changed'] for e in events),
              track_events=events, cap_events=cap_events, signal_events=signal_events,
              final=dict(time=good[-1]['sim_time'], paused=good[-1]['paused'], speed=good[-1]['player']['speed'],
                         signal=good[-1]['next_signal'], cab=good[-1]['diesel_cab']),
              limitations='Sample brackets are not exact event times. Service and car references differ. Matching pointers do not prove global identity or atomicity. Cap agreement validates sampled finite inputs, not all native branches or speedpost causation.')
(root / (a.name + '-summary.json')).write_text(json.dumps(report, indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('track_events', 'cap_events', 'signal_events', 'final')}, indent=2))
print(json.dumps(dict(node_changes=sum(e['node_changed'] for e in events), cap_changes=len(cap_events), signal_changes=len(signal_events))))
