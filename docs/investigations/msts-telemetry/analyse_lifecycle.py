"""Summarize registry transitions and movement without equating physical absence with deletion."""
import argparse,json,math,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('capture');a=p.parse_args();root=Path(__file__).resolve().parent;path=root/'captures'/a.capture/'lifecycle.jsonl'
rows=[json.loads(line) for line in path.read_text().splitlines()];good=[s for s in rows if 'error' not in s];services={};previous={};events=[];origins=[]
for index,s in enumerate(good):
    origin=s['tracks']['origin_tile']
    if not origins or origin!=origins[-1]['origin']:origins.append(dict(sample=index,sim_time=s['sim_time'],origin=origin))
    physical={t['train']:t for t in s['tracks']['trains']}
    for v in s['services']['entries']:
        ident=v['service_id'];summary=services.setdefault(ident,dict(name=v.get('strings',{}).get('service_key'),samples=0,speeds=[],targets=[],accelerations=[],movement_errors=[],physical_samples=0,unphysical_positive_speed_samples=0,node_transitions=0,section_transitions=0))
        summary['samples']+=1;summary['speeds'].append(v['speed']);summary['targets'].append(v['target_speed']);summary['accelerations'].append(v['acceleration'])
        summary['physical_samples']+=int(bool(v['train']))
        summary['unphysical_positive_speed_samples']+=int(not v['train'] and abs(v['speed'])>.01)
        old=previous.get(ident);key=(v['train'],v['physicalized_raw'],v['flags_raw'])
        if not old or key!=old['key']:events.append(dict(service_id=ident,sim_time=s['sim_time'],sample=index,train=v['train'],physicalized=v['physicalized_raw'],flags=v['flags_raw'],speed=v['speed']))
        track=v.get('track');pos=None
        if track and track['node']:
            q=track['position_candidate'];pos=[q[0]+2048*origin[0],q[1],q[2]+2048*origin[1]]
            if old and old['track'] and old['track']['node']:
                summary['node_transitions']+=int(track['node']!=old['track']['node'])
                summary['section_transitions']+=int((track['node'],track['section_index'])!=(old['track']['node'],old['track']['section_index']))
        dt=s['sim_time']-old['sim_time'] if old else 0
        if old and pos and old['pos'] and dt>0 and s['same_sim_time'] and old['same_sim_time']:
            observed=math.dist(pos,old['pos'])/dt;expected=(abs(v['speed'])+abs(old['speed']))/2
            summary['movement_errors'].append(abs(observed-expected))
            if abs(observed-expected)>1:
                anomalies=summary.setdefault('movement_anomalies',dict(count=0,examples=[]))
                anomalies['count']+=1
                if len(anomalies['examples'])<5:
                    anomalies['examples'].append(dict(sample=index,sim_time=s['sim_time'],dt=dt,position_chord_speed=observed,native_speed=v['speed'],expected_average_speed=expected,train=v['train'],node=track['node'],section=track['section_index']))
        previous[ident]=dict(key=key,track=track,pos=pos,sim_time=s['sim_time'],speed=v['speed'],same_sim_time=s['same_sim_time'])
for v in services.values():
    for key in ['speeds','targets','accelerations','movement_errors']:
        vals=v[key];v[key]=dict(count=len(vals),min=min(vals) if vals else None,max=max(vals) if vals else None,median=statistics.median(vals) if vals else None)
result=dict(capture=a.capture,samples=len(rows),errors=len(rows)-len(good),crossed_sim_step=sum(not s['same_sim_time'] for s in good),sim_start=good[0]['sim_time'],sim_end=good[-1]['sim_time'],origin_changes=origins,service_transitions=events,services=services,limitation='Position/speed comparison uses chords and asynchronous samples; it does not prove exact integration, axis conventions or global origin-shift handling.')
(root/(a.capture+'-summary.json')).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
