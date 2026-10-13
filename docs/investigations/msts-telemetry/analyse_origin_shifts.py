"""Compare local and origin-corrected body deltas across retained origin changes."""
import argparse,hashlib,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('name');a=p.parse_args()
if Path(a.name).name!=a.name:raise ValueError('Invalid name')
root=Path(__file__).resolve().parent;src=root/'captures'/a.name/'samples.jsonl'
rows=[json.loads(l) for l in src.read_text().splitlines()];events=[]
for index,(before,after) in enumerate(zip(rows,rows[1:]),1):
    if 'error' in before or 'error' in after:continue
    x,y=before['physical_tracks'],after['physical_tracks']
    if x['origin_tile']==y['origin_tile']:continue
    def cars(snapshot):
        return {(t['train'],c['address']):(t['is_player'],c) for t in snapshot['trains'] for c in t['cars']}
    aa,bb=cars(x),cars(y);details=[]
    for key in sorted(aa.keys()&bb.keys()):
        player,c0=aa[key];_,c1=bb[key]
        if c0['body']!=c1['body']:continue
        delta=[v-u for u,v in zip(c0['body_position'],c1['body_position'])]
        corrected=[delta[0]+2048*(y['origin_tile'][0]-x['origin_tile'][0]),delta[1],delta[2]+2048*(y['origin_tile'][1]-x['origin_tile'][1])]
        details.append(dict(train=key[0],car=key[1],body=c0['body'],is_player=player,raw_delta=delta,corrected_delta=corrected))
    events.append(dict(sample=index,clock0=before['sim_time'],clock0_after=before['sim_time_after'],clock1=after['sim_time'],clock1_after=after['sim_time_after'],origin0=x['origin_tile'],origin1=y['origin_tile'],stable=[x['origin_stable'],y['origin_stable']],cars=len(details),player_cars=sum(d['is_player'] for d in details),max_raw=max(math.dist(d['raw_delta'],[0,0,0]) for d in details),max_corrected=max(math.dist(d['corrected_delta'],[0,0,0]) for d in details),details=details))
out=dict(source=str(src.relative_to(root)),sha256=hashlib.sha256(src.read_bytes()).hexdigest(),events=events,
    limitation='One-step sampled position continuity, not exact motion integration or atomic rebase timing. Float64 arithmetic applies the independently traced2048m tile translation; Y stays local-height. No latitude/longitude or arbitrary-route proof.')
(root/(a.name+'-origin-shifts.json')).write_text(json.dumps(out,indent=2))
print(json.dumps([{k:v for k,v in e.items() if k!='details'} for e in events],indent=2))
