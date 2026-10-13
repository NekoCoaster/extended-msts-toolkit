"""Report actual observed modes, including unsuccessful release attempts."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent;rows=[json.loads(x) for x in (root/'captures/brake-release-01/samples.jsonl').read_text(encoding='utf-8').splitlines()];v=[r for r in rows if 'error' not in r];lead=lambda r:r['trains'][0]['cars'][0]
changes=[];last=None
for r in v:
 pair=(r['train_brake'],r['selected_mode'])
 if pair!=last:changes.append(dict(elapsed=r['elapsed'],sim_time=r['sim_time'],handle=pair[0],mode=hex(pair[1]),fraction=r['selected_fraction'],pipe_command=r['pipe_command']));last=pair
last_change=changes[-1]['elapsed'];tail=[r for r in v if r['elapsed']>=last_change]
s=dict(samples=len(rows),errors=len(rows)-len(v),mode_values=[hex(x) for x in sorted(set(r['selected_mode'] for r in v))],release_observed=any(r['selected_mode']==4 for r in v),sim_time_range=[v[0]['sim_time'],v[-1]['sim_time']],changes=changes,speed_range=[min(r['speed'] for r in v),max(r['speed'] for r in v)],lead_cylinder_range=[min(lead(r)['floats']['0x230'] for r in v),max(lead(r)['floats']['0x230'] for r in v)],pipe_command_range=[min(r['pipe_command'] for r in v),max(r['pipe_command'] for r in v)],post_final_decrease_pipe_range=[min(r['pipe_command'] for r in tail),max(r['pipe_command'] for r in tail)],post_final_decrease_duration=tail[-1]['elapsed']-tail[0]['elapsed'],rise_latch_values=sorted(set(lead(r)['integers']['0x26c'] for r in v)),fall_latch_values=sorted(set(lead(r)['integers']['0x270'] for r in v)),limitations='Capture name describes intended test only: release not achieved if mode4 absent. Mouse drag first increased holding demand; subsequent downward drags did not change it; one keyboard decrement followed. Non-atomic50ms external sampling. No AI.')
(root/'brake-release-attempt-summary.json').write_text(json.dumps(s,indent=2),encoding='utf-8');print(json.dumps(s))
