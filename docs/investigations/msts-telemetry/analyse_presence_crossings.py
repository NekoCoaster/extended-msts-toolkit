"""Track abstract record identities across route nodes; no physical occupancy claim."""
import argparse,collections,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):raise ValueError('Invalid name')
root=Path(__file__).resolve().parent;source=root/'captures'/a.name/'samples.jsonl'
rows=[json.loads(x) for x in source.read_text(encoding='utf-8').splitlines()]
previous=None;events=[];problems=[];counts={};records=set()
for index,s in enumerate(rows):
    if 'error' in s:previous=None;problems.append(dict(sample=index,error=s['error']));continue
    now={}
    for n in s['presence']:
        for x in n['entries']:
            if x['address'] in now:problems.append(dict(sample=index,duplicate_record=x['address']))
            now[x['address']]=dict(x,node=n['node'],route=s['node_map'].get(str(n['node'])))
    records.update(now)
    for service,count in collections.Counter(x['service'] for x in now.values()).items():counts.setdefault(str(service),set()).add(count)
    if previous is not None:
        pi,ps,old=previous
        if ps['node_map']!=s['node_map']:problems.append(dict(sample=index,error='Route map changed;comparison skipped'))
        else:
            for key in old.keys()&now.keys():
                x,y=old[key],now[key]
                if (x['service'],x['configuration_reference'])!=(y['service'],y['configuration_reference']):problems.append(dict(sample=index,identity_change=key));continue
                if x['node']!=y['node']:
                    events.append(dict(record=key,service=y['service'],configuration=y['configuration_reference'],sample0=pi,sample1=index,time0=ps['sim_time'],time0_after=ps['sim_time_after'],time1=s['sim_time'],time1_after=s['sim_time_after'],from_route=x['route'],to_route=y['route'],distance0=x['node_distance'],distance1=y['node_distance']))
    previous=(index,s,now)
out=dict(source=str(source.relative_to(root)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),samples=len(rows),unique_records=len(records),counts_by_service={k:sorted(v) for k,v in counts.items()},problems=problems,crossing_count=len(events),crossings=events,limitations='Same record/configuration/service pointers across sequential samples are a bounded identity check,not a lifetime guarantee. Count sets omit absent services. Brackets are sample windows,not exact crossing instants. Nodes need not be adjacent if sampling skips intermediate state. Presence is abstract per-car state,not physical vehicle extent or block occupancy.')
(root/(a.name+'-crossings.json')).write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='crossings'}))
