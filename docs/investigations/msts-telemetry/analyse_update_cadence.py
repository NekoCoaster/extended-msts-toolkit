"""Summarize the bounded pause/resume experiment without inferring unseen frames."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
rows=[json.loads(s) for s in (root/'captures/update-cadence-01/samples.jsonl').read_text().splitlines()]
good=[r for r in rows if 'error'not in r];segments=[]
for r in good:
    if not segments or segments[-1]['paused']!=r['paused']:segments.append(dict(paused=r['paused'],rows=[]))
    segments[-1]['rows'].append(r)
summary=[]
for group in segments:
    rr=group['rows'];first=rr[0];last=rr[-1]
    summary.append(dict(paused=group['paused'],samples=len(rr),wall_span=last['wall_elapsed']-first['wall_elapsed'],simulation_delta=last['sim_time']-first['sim_time'],elapsed_candidate_delta=last['train']['elapsed_candidate']-first['train']['elapsed_candidate'],observed_elapsed_changes=sum(a['train']['elapsed_candidate']!=b['train']['elapsed_candidate'] for a,b in zip(rr,rr[1:])),max_abs_player_speed=max(abs(x['train']['speed']) for x in rr)))
result=dict(samples=len(rows),errors=len(rows)-len(good),segments=summary,sim_time_range=[good[0]['sim_time'],good[-1]['sim_time']],cross_step_samples=sum(r['sim_time']!=r['end_sim_time'] for r in good),audio_record_variants=len({json.dumps(r['train']['audio_records']) for r in good}),audio_selection_variants=len({json.dumps(r['train']['audio']) for r in good}),mass_variants=len({r['train']['mass'] for r in good}),length_variants=len({r['train']['length'] for r in good}),distance_range=[min(r['train']['distance_candidate'] for r in good),max(r['train']['distance_candidate'] for r in good)],cap_mismatches=sum(not s['matches'] for r in good for s in r['services']),service_cap_variants={str(sid):sorted({s['fields']['0x220']['value'] for r in good for s in r['services'] if s['service_id']==sid}) for sid in {s['service_id'] for r in good for s in r['services']}},limitation='0.1s target external sampling cannot count all simulation callbacks; paused stationary player with existing default audio only. No moving post crossing, audio expiry or coupling transition.')
(root/'update-cadence-summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
