"""Identity-qualified AI extrapolation comparison; preserves sample exclusions."""
import argparse,collections,hashlib,json,statistics
from pathlib import Path
root=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
source=root/'captures'/a.name/'samples.jsonl'
rows=[json.loads(s) for s in source.read_text(encoding='utf-8').splitlines()]
valid=[s for s in rows if 'error' not in s];comparisons=[];excluded=collections.Counter();identities={};changes=[];node_changes=[];prior={};update_times=set()
def stats(values):
    return dict(count=len(values),min=min(values),median=statistics.median(values),max=max(values)) if values else dict(count=0)
for i,s in enumerate(valid):
    services={v['address']:v for v in s['services']['entries']}
    for r in s['rows']:
        identity=(r['physical_car_candidate'],r['service'])
        if r['address'] in identities and identities[r['address']]!=identity:changes.append(dict(sample=i,record=r['address'],before=identities[r['address']],after=identity))
        identities[r['address']]=identity
        if r['address'] in prior and prior[r['address']]!=r['track_node']:node_changes.append(dict(sample=i,record=r['address'],before=prior[r['address']],after=r['track_node']))
        prior[r['address']]=r['track_node']
        if 'train_id' not in r:excluded['unjoined']+=1;continue
        if r['is_player']:continue
        if not all(r[k] for k in ('record_stable','same_node','service_matches','backlink_matches')):excluded['identity_or_node_or_record']+=1;continue
        v=services[r['service']];update=v['update_candidate_floats']['0x150'];age=s['sim_time']-update;update_times.add(update)
        if not 0<=age<=60:excluded['age_outside_same_day_0_60']+=1;continue
        speed=abs(v['speed']);acc=v['acceleration'];target=v['target_speed']
        if acc==0:distance=speed*age
        else:
            reach=abs((target-speed)/acc)
            distance=(age-reach)*target+(speed+target)*reach*.5 if reach<=age else (2*speed+age*acc)*age*.5
        after_age=s['sim_time_after']-update
        if acc==0:after_distance=speed*after_age
        else:after_distance=(after_age-reach)*target+(speed+target)*reach*.5 if reach<=after_age else (2*speed+after_age*acc)*after_age*.5
        comparisons.append(dict(sample=i,car=r['physical_car_candidate'],paused=bool(s['paused']),same_clock=s['sim_time']==s['sim_time_after'],age=age,prediction=distance,gap=r['presence_minus_physical'],absolute_gap_error=abs(abs(r['presence_minus_physical'])-distance),end_clock_error=abs(abs(r['presence_minus_physical'])-after_distance)))
groups={}
for name,predicate in [('moving_all',lambda c:not c['paused']),('moving_same_clock',lambda c:not c['paused'] and c['same_clock']),('paused',lambda c:c['paused'])]:
    selected=[c for c in comparisons if predicate(c)];groups[name]=dict(error=stats([c['absolute_gap_error'] for c in selected]),end_clock_error=stats([c['end_clock_error'] for c in selected]),age=stats([c['age'] for c in selected]),gap=stats([c['gap'] for c in selected]),samples=len({c['sample'] for c in selected}))
out=dict(source=str(source.relative_to(root)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),samples=len(rows),errors=len(rows)-len(valid),clock_range=[valid[0]['sim_time'],valid[-1]['sim_time_after']],max_read_seconds=max(s['monotonic_after']-s['monotonic'] for s in valid),unique_presence_records=len(identities),identity_changes=changes,node_changes=node_changes,distinct_ai_update_times=len(update_times),exclusions=dict(excluded),comparisons=groups,limitations='Per-car sequential snapshots,not atomic. Same-clock filter cannot exclude internal phase differences. Python double reconstruction;single AI and route segment,not universal correction. Statistics count correlated cars separately;sample count also reported. Pointer reuse between samples can go undetected.')
(root/(a.name+'-summary.json')).write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out))
