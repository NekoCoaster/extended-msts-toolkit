"""Summarize the immutable paused per-car identity join, without lifetime claims."""
import collections,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'captures/presence-identity-paused-01/identity.json'
d=json.loads(p.read_text(encoding='utf-8'))
assert d['paused'] and d['paused_after'] and d['sim_time']==d['sim_time_after']
groups=[]
for player in (True,False):
    rows=[x for x in d['rows'] if x.get('is_player')==player]
    groups.append(dict(is_player=player,count=len(rows),unique_car_pointers=len({x['physical_car_candidate'] for x in rows}),bad_backlinks=sum(not x['backlink_matches'] for x in rows),bad_services=sum(not x['service_matches'] for x in rows),unstable=sum(not x['record_stable'] for x in rows),different_nodes=sum(not x['same_node'] for x in rows),direction_pairs=dict(collections.Counter(str((x['direction_raw'],x['track_direction'])) for x in rows)),delta_min=min(x['presence_minus_physical'] for x in rows),delta_max=max(x['presence_minus_physical'] for x in rows),in_refresh_lists=[sum(x['address'] in l['records'] for x in rows) for l in d['physical_refresh_lists']]))
out=dict(source=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sim_time=d['sim_time'],records=len(d['rows']),unjoined=sum('train_id' not in x for x in d['rows']),groups=groups,limitations='Exact pointer/backlink joins at one paused state;not proof of stable lifetime identity,creation/destruction,reversal,or other consists/routes. Refresh-list ownership inferred only for this snapshot.')
(root/'presence-identity-summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out))
