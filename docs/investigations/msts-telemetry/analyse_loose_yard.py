"""Compare configured loose-consist sizes with independent runtime link components."""
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
activity = Path('C:/MSTS/ROUTES/USA2/ACTIVITIES/yard_one.act')
retained_activity = root / 'captures/loose-fixture-provenance-01/yard_one.act'
data = retained_activity.read_bytes()
text = data.decode('utf-16') if data[:2] in (b'\xff\xfe', b'\xfe\xff') else data.decode('utf-8-sig')
tokens = re.findall(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()]+', text)
pos = 0
def parse(nested=False):
    global pos
    result = []
    while pos < len(tokens):
        t = tokens[pos]
        pos += 1
        if t == ')':
            if not nested:
                raise ValueError('Unexpected closing parenthesis')
            return result
        if pos < len(tokens) and tokens[pos] == '(':
            pos += 1
            result.append((t, parse(True)))
        else:
            result.append(t)
    if nested:
        raise ValueError('Unclosed SIMIS node')
    return result
def walk(tree, name):
    for value in tree:
        if isinstance(value, tuple):
            if value[0].lower() == name.lower():
                yield value[1]
            yield from walk(value[1], name)
def direct(tree, name):
    return next((v[1] for v in tree if isinstance(v, tuple) and v[0].lower() == name.lower()), [])
tree = parse()
configured = []
for obj in walk(tree, 'ActivityObject'):
    if direct(obj, 'ObjectType') != ['WagonsList']:
        continue
    wagons = [dict(uid=direct(w, 'UiD'), asset=direct(w, 'WagonData')) for w in walk(obj, 'Wagon')]
    engines = [dict(uid=direct(w, 'UiD'), asset=direct(w, 'EngineData')) for w in walk(obj, 'Engine')]
    configured.append(dict(id=direct(obj, 'ID'), tile=direct(obj, 'Tile'),
                           direction=direct(obj, 'Direction'), wagons=wagons, engines=engines,
                           count=len(wagons)+len(engines)))

source = root / 'captures/loose-yard-notebook-01/registry.json'
snapshot = json.loads(source.read_text())
registry = snapshot['registry']
outside = set(registry['physical_not_in_train_chains'])
objects = {r['address']:r for r in registry['objects']}
remaining = set(outside)
components = []
while remaining:
    pending = [min(remaining)]
    component = set()
    while pending:
        address = pending.pop()
        if address in component:
            continue
        if address not in outside:
            raise ValueError('Loose graph links outside the set difference')
        component.add(address)
        pending.extend(a for a in objects[address]['physics']['links'] if a)
    remaining -= component
    rows = [objects[a] for a in sorted(component)]
    components.append(dict(addresses=sorted(component), count=len(rows),
                           object_ids=[r['object_id'] for r in rows],
                           owners=sorted({r['owner'] for r in rows}),
                           native_kinds=sorted({r['native_kind'] for r in rows}),
                           endpoints=sum(sum(bool(v) for v in r['physics']['links']) == 1 for r in rows),
                           reciprocal=all(r['address'] in objects[a]['physics']['links'] for r in rows for a in r['physics']['links'] if a)))
report = dict(activity=str(activity), activity_sha256=hashlib.sha256(data).hexdigest(),
              retained_activity=str(retained_activity.relative_to(root)),
              source=str(source.relative_to(root)), source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
              paused=snapshot['paused'], time=snapshot['sim_time'], time_after=snapshot['sim_time_after'],
              configured=configured, configured_count=sum(c['count'] for c in configured),
              physical_count=len(objects), outside_count=len(outside), connected_trains=registry['trains'],
              components=components, component_sizes_match=sorted(c['count'] for c in configured)==sorted(c['count'] for c in components),
              registered_outside=sum(objects[a]['registered_bit'] for a in outside),
              stable_outside=sum(objects[a]['stable'] and objects[a]['physics']['body_pointer_stable'] for a in outside),
              outside_kinds={hex(k):sum(objects[a]['native_kind']==k for a in outside) for k in sorted({objects[a]['native_kind'] for a in outside})},
              outside_zero_linear_velocity=sum(all(v==0 for v in objects[a]['physics']['velocity']) for a in outside),
              outside_resting_flags=sum(objects[a]['physics']['resting'] for a in outside),
              outside_derailed_flags=sum(objects[a]['physics']['derailed'] for a in outside),
              limitations='Matching component size multiset and fixture context support loose-stock coverage; no exact activity-ID-to-native-ID or per-group asset identity mapping is established. Paused initial loading is not coupling, detachment, moving loose-stock or remote unphysicalized coverage.')
(root / 'loose-yard-summary.json').write_text(json.dumps(report, indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ('configured', 'components')}, indent=2))
print(json.dumps(dict(configured_sizes=[c['count'] for c in configured], runtime_sizes=[c['count'] for c in components])))
