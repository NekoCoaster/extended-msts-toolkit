"""Preserve observed infrastructure field transitions; no causal/occupancy inference."""
import argparse,collections,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):raise ValueError('Invalid name')
root=Path(__file__).resolve().parent;src=root/'captures'/a.name/'samples.jsonl';rows=[json.loads(s) for s in src.read_text(encoding='utf-8').splitlines()]
def states(r):
    result={}
    for kind,fields in [('junctions',('branch','owner','flags')),('vectors',('constraint','state','services')),('signals',('aspect','associated_service','flags'))]:
        for x in r[kind]:
            key=(kind,x['address']);result[key]=dict(id=x.get('route_id',x.get('index')),values={k:x[k] for k in fields},stable=x.get('owner_stable',x.get('list_stable',True)))
    for n in r['presence']:
        counts=collections.Counter(str(v['service']) for v in n['entries'])
        result[('presence',n['node'])]=dict(id=r['node_map'].get(str(n['node'])),values=dict(service_car_counts=dict(counts)),stable=True)
    return result
events=[];before=None;good=[];errors=[];map_changes=0
for index,r in enumerate(rows):
    if 'error' in r:errors.append(dict(index=index,**r));before=None;continue
    good.append(r);now=states(r)
    if before is not None:
        b,old=before
        if b['node_map']!=r['node_map']:map_changes+=1
        else:
            for key in sorted(set(old)|set(now)):
                x=old.get(key);y=now.get(key)
                xv=x['values'] if x else None;yv=y['values'] if y else None
                if xv==yv:continue
                events.append(dict(kind=key[0],address=key[1],id=(y or x)['id'],time0=b['sim_time'],time0_after=b['sim_time_after'],time1=r['sim_time'],time1_after=r['sim_time_after'],before=xv,after=yv,pointer_checks_pass=all(z is None or z['stable'] for z in (x,y)),same_clock_reads=all(z['sim_time']==z['sim_time_after'] for z in (b,r)),both_unpaused=all(not z['paused'] and not z['paused_after'] for z in (b,r))))
    before=(r,now)
presence_ranges={}
for r in good:
    for n in r['presence']:
        for service in sorted({e['service'] for e in n['entries']}):
            values=[e['node_distance'] for e in n['entries'] if e['service']==service]
            key=f"{n['node']}:{service}";v=dict(time=r['sim_time'],count=len(values),min=min(values),max=max(values))
            g=presence_ranges.setdefault(key,dict(node=n['node'],route_id=r['node_map'].get(str(n['node'])),service=service,first=v,last=v,observations=0,min_seen=min(values),max_seen=max(values)))
            g['last']=v;g['observations']+=1;g['min_seen']=min(g['min_seen'],min(values));g['max_seen']=max(g['max_seen'],max(values))
out=dict(capture=a.name,sha256=hashlib.sha256(src.read_bytes()).hexdigest(),samples=len(rows),errors=errors,paused_samples=sum(bool(r['paused']) for r in good),time_range=[good[0]['sim_time'],good[-1]['sim_time_after']],max_read_seconds=max(r['monotonic_after']-r['monotonic'] for r in good),map_changes=map_changes,event_counts=dict(collections.Counter(e['kind'] for e in events)),events=events,presence_distance_ranges=list(presence_ranges.values()),first_trains=good[0]['trains'],last_trains=good[-1]['trains'],service_identities=[dict(address=s['address'],id=s.get('service_id'),is_player=s['is_player']) for s in good[0]['services']['entries']],limitations='Changes bracketed between sequential snapshots;not exact transition times,atomic states or causal proof. Errors/map changes break continuity. Event counts include presence membership/count changes but exclude continuously varying distances,which are summarized separately. Presence reports per-service record counts,not physical occupancy;list duplicates preserved. Signal index is database item index,not universal asset ID. Complete route map checked each row;no lifecycle identity guarantee.')
(root/(a.name+'-summary.json')).write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='events'},indent=2))
