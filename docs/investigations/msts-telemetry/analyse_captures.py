import json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
results={}
for folder in sorted((ROOT/'captures').iterdir()):
    path=folder/'samples.jsonl'
    if not path.exists():continue
    rows=[json.loads(l) for l in path.read_text().splitlines()];good=[s for s in rows if 'error' not in s]
    if not good:results[folder.name]={'samples':len(rows),'errors':len(rows)};continue
    trains={}
    for s in good:
        for t in s.get('registered_trains',[]):
            k=str(t['id']);a=trains.setdefault(k,dict(player=t['is_player'],samples=0,counts=set(),speed=[],body_speed=[],derailed=set(),positions=[],wrappers=set()))
            a['samples']+=1;a['counts'].add(len(t['cars']));a['speed'].append(t['speed_raw']);a['wrappers'].add(t['controller_wrapper'])
            a['body_speed'].append(t['cars'][0]['longitudinal_speed']);a['positions'].append(t['cars'][0]['position'])
            a['derailed'].add(sum(c['derailed'] for c in t['cars']))
    for t in trains.values():
        t['speed_range']=[min(t['speed']),max(t['speed'])];t['max_train_body_speed_difference']=max(abs(a-b) for a,b in zip(t['speed'],t['body_speed']))
        t['first_position']=t['positions'][0];t['last_position']=t['positions'][-1]
        t['coordinate_jumps_over_1000m']=sum(math.dist(a,b)>1000 for a,b in zip(t['positions'],t['positions'][1:]))
        for key in ('positions','speed','body_speed'):del t[key]
        for key in ('counts','derailed','wrappers'):t[key]=sorted(t[key])
    signal_history={}
    for s in good:
        for e in s['monitor_entries']:
            if e['type'] not in (1,2,3):continue
            k=hex(e['object']);h=signal_history.setdefault(k,[])
            state=[e['type'],e['f10'],e['object_flags_1c']]
            if not h or state!=h[-1]['state']:h.append(dict(sim_time=s['sim_time'],distance=e['f04'],state=state))
    results[folder.name]=dict(samples=len(rows),errors=len(rows)-len(good),registry_errors=sum('registry_error' in s for s in good),
                             start_time=good[0]['sim_time'],end_time=good[-1]['sim_time'],paused_samples=sum(bool(s['paused']) for s in good),
                             crossed_simulation_step=sum(not s['same_sim_time'] for s in good),unstable_player_pointer=sum(not s['train_pointer_stable'] for s in good),
                             player_counts=sorted(set(len(s.get('cars',[])) for s in good)),trains=trains,signal_history=signal_history)
(ROOT/'capture-summary.json').write_text(json.dumps(results,indent=2))
print(json.dumps({k:{x:v for x,v in r.items() if x not in ('trains','signal_history')} for k,r in results.items()},indent=2))
game=Path('C:/MSTS');provenance={}
for rel in ['train.exe','DINPUT.dll','NEMT/settings.ini','ROUTES/USA2/ACTIVITIES/evegrain.act','ROUTES/USA2/SERVICES/EveGrain.srv','ROUTES/USA2/SERVICES/EveGrain (Traffic).srv','ROUTES/USA2/SERVICES/EveGrain (Traffic01).srv','TRAINS/CONSISTS/Dash921gran.con','TRAINS/CONSISTS/2 x Dash 9, 20 Intermodal.con']:
    p=game/rel
    if p.exists():provenance[rel]=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
b=bytearray((game/'train.exe').read_bytes());b[0x116]&=0xdf
provenance['executable_LAA_bit_cleared_sha256']=hashlib.sha256(b).hexdigest()
provenance['ghidra_program_sha256']='69218fce876298c684a2140c7d3925a452c47bb10037ffd8c491f65c5c0c6e7a'
provenance['matches_ghidra_after_LAA_bit_only']=provenance['executable_LAA_bit_cleared_sha256']==provenance['ghidra_program_sha256']
(ROOT/'runtime-provenance.json').write_text(json.dumps(provenance,indent=2))
(ROOT/'installed-settings-observed.ini').write_bytes((game/'NEMT/settings.ini').read_bytes())
