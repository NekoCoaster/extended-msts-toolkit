"""Validate the retained loose-stock track fixture and describe a topology route."""
import collections
import hashlib
import json
import math
from pathlib import Path

root = Path(__file__).resolve().parent
context_path = root/'captures/loose-yard-track-01/context.json'
topology_path = root/'captures/loose-yard-topology-01/topology.json'
context = json.loads(context_path.read_text())
topology = json.loads(topology_path.read_text())
objects = context['objects']
lead = next(o for o in objects if o['address']==context['player_car'])
loose = [o for o in objects if o['owner']==0]
nodes = {n['address']:n for n in topology['topology']['nodes']}
checks = []
for o in objects:
    t=o['track']
    checks.append(dict(address=o['address'], loose=o['owner']==0,
                       valid_node=t['node'] in nodes and nodes[t['node']]['kind']==1,
                       section_in_bounds=0<=t['section_index']<t['node_section_count'],
                       section_pointer_matches=t['section_pointer_matches'],
                       node_distance_in_bounds=0<=t['node_distance']<=t['node_length'],
                       owner_stable=o['owner_stable'],
                       body_track_delta=[a-b for a,b in zip(o['position'],t['position_candidate'])]))

nearest = min(loose,key=lambda o:sum((a-b)**2 for a,b in zip(o['position'],lead['position'])))
# Identify the five-car component by the prior independently retained graph.
components=json.loads((root/'loose-yard-summary.json').read_text())['components']
target_component=next(c for c in components if c['count']==5)
target=next(o for o in objects if o['address'] in target_component['addresses'])
start,end=lead['track']['node'],target['track']['node']
queue=collections.deque([[start]])
seen={start}
route=None
while queue:
    path=queue.popleft()
    if path[-1]==end:
        route=path
        break
    for link in nodes[path[-1]]['links']:
        n=link['node']
        if n and n not in seen:
            seen.add(n)
            queue.append(path+[n])
report=dict(sources={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (context_path,topology_path)},
            time=context['time'],end_time=context['end_time'],paused=context['paused'],origin_stable=context['origin_stable'],
            count=len(objects),loose_count=len(loose),checks=checks,
            failed_checks=[c for c in checks if not all(c[k] for k in ('valid_node','section_in_bounds','section_pointer_matches','node_distance_in_bounds','owner_stable'))],
            nearest_loose=dict(address=nearest['address'],node=nearest['track']['node'],
                               centre_distance=math.dist(nearest['position'],lead['position']),
                               same_node=nearest['track']['node']==start),
            player=lead,target_component=target_component,topology_path=None if route is None else [nodes[n] for n in route],
            limitations='Shortest unweighted graph path is not a drivable route or clearance. A turnout path between two output pins needs a reversal through its input leg; switch selection alone does not connect the output pins directly. Centre distance is not along-track distance or coupler gap. Captures are separately paused snapshots,not atomic. No coupling/uncoupling or turnout action has occurred.')
(root/'loose-track-context-summary.json').write_text(json.dumps(report,indent=2))
print(json.dumps(dict(count=report['count'],loose_count=report['loose_count'],failed_checks=len(report['failed_checks']),nearest=report['nearest_loose'],route=route,delta_ranges={axis:[min(c['body_track_delta'][i] for c in checks if c['loose']),max(c['body_track_delta'][i] for c in checks if c['loose'])] for i,axis in enumerate('xyz')})))
