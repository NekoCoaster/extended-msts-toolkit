"""Describe sampled physical section/node transitions without assuming atomicity."""
import argparse,collections,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid name')
root=Path(__file__).resolve().parent;source=root/'captures'/a.name/'samples.jsonl'
rows=[json.loads(x) for x in source.read_text().splitlines()]
previous={};events=[];origins=set();distances=[];clocks=[];paused=0;errors=[]
for index,row in enumerate(rows):
    if 'error' in row:errors.append(dict(sample=index,error=row['error']));previous={};continue
    tracks=row['physical_tracks'];origins.add(tuple(tracks['origin_tile']));clocks.append(row['sim_time']);paused+=bool(row['paused'])
    distances.append(row['monitor_and_cab']['next_signal']['distance'])
    now={}
    for train in tracks['trains']:
        for car in train['cars']:
            if 'error' in car:errors.append(dict(sample=index,address=car['address'],error=car['error']));continue
            t=car['track'];key=(train['train'],car['address'])
            now[key]=dict(node=t['node'],section=t['section_index'],distance=t['node_distance'],route=row['node_map'].get(str(t['node'])),is_player=train['is_player'],body=car['body'],sample=index,time=row['sim_time'])
            old=previous.get(key)
            if old and old['body']==car['body'] and (old['node'],old['section'])!=(t['node'],t['section_index']):
                events.append(dict(train=key[0],car=key[1],before=old,after=now[key],node_changed=old['node']!=t['node']))
    previous=now
out=dict(source=str(source.relative_to(root)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),samples=len(rows),paused_samples=paused,clock_range=[min(clocks),max(clocks)],origins=sorted(origins),monitor_distance_range=[min(distances),max(distances)],errors=errors,
         section_or_node_transitions=len(events),player_transitions=sum(e['after']['is_player'] for e in events),node_transitions=sum(e['node_changed'] for e in events),events=events,
         limitations='Sequential samples with matching train/car/body identities within one run. Section changes can skip intermediates; brackets are not exact event times. No global identity guarantee, full-vehicle occupancy or origin-shift validation.')
(root/(a.name+'-moving-tracks.json')).write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='events'},indent=2))
