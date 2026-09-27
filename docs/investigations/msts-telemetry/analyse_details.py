"""Summarize completed detailed captures without promoting hypotheses to facts."""
import json
from pathlib import Path
R=Path(__file__).resolve().parent
out=[]
for path in sorted((R/'captures').glob('*/details.jsonl')):
    samples=[json.loads(s) for s in path.read_text().splitlines()]
    good=[s for s in samples if 'error' not in s]
    corrected=0
    for s in good:
        cab=s.get('diesel_cab',{})
        if 'current_traction_kiloamps' in cab:
            # Legacy probe misnamed native amps and erroneously multiplied display by 1000.
            # Preserve raw capture; correct only this derived summary.
            cab['current_traction_amps']=cab.pop('current_traction_kiloamps')
            cab['current_dynamic_amps']=cab.pop('current_dynamic_kiloamps')
            cab['ammeter_amps']=cab['current_traction_amps'] if cab['dynamic_braking_raw']<=0 else -cab['current_dynamic_amps']
            corrected+=1
    transitions=[];previous=None
    for i,s in enumerate(samples):
        h=s.get('next_signal',{}).get('selected_normal')
        if not h:continue
        key=(h['address'],h['aspect'])
        if key!=previous:
            transitions.append(dict(sample=i,utc=s['utc'],sim_time=s['sim_time'],head=h['address'],aspect=h['aspect'],aspect_speed=h['aspect_speed'],distance=s['next_signal']['distance'],player_speed=s['player']['speed']))
            previous=key
    ranges={}
    for name in sorted({k for s in good for k in s.get('diesel_cab',{})}):
        vals=[s['diesel_cab'][name] for s in good if name in s.get('diesel_cab',{})]
        ranges[name]=dict(min=min(vals),max=max(vals),first=vals[0],last=vals[-1])
    out.append(dict(capture=path.parent.name,samples=len(samples),legacy_current_units_corrected_samples=corrected,errors=len(samples)-len(good),signal_errors=sum('signal_error' in s for s in good),crossed_sim_step=sum(not s['same_sim_time'] for s in good),unstable_iterator=sum(not s['iterator_stable'] for s in good),signal_transitions=transitions,diesel_ranges=ranges))
(R/'detail-summary.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
