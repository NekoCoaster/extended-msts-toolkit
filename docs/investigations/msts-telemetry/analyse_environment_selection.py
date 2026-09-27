"""Compare a captured selection to explicitly named installed route assets."""
import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parent
source=root/'captures/environment-selection-paused-01/selection.json'
capture=json.loads(source.read_text(encoding='utf-8'));s=capture['selection']
# Deliberately explicit paths: no filesystem traversal using process-read strings.
route=Path('C:/MSTS/ROUTES/USA2/usa2.trk')
environment=Path('C:/MSTS/ROUTES/USA2/ENVFILES/USA2snow.env')
raw=route.read_bytes();text=raw.decode('utf-16') if raw[:2] in (b'\xff\xfe',b'\xfe\xff') else raw.decode('utf-8-sig')
checks=[]
for row in s['route_slots']:
    token=['Spring','Summer','Autumn','Winter'][row['season']]+['Clear','Rain','Snow'][row['slot']]
    matches=re.findall(r'\b'+token+r'\s*\(\s*"([^"\r\n]+)"\s*\)',text)
    checks.append(dict(token=token,declarations=matches,loaded=row['filename'],matches=matches==[row['filename']]))
out=dict(source=str(source.relative_to(root)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
         files={str(p):dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in (route,environment)},
         checks=checks,all_slots_match=all(x['matches'] for x in checks),
         selected_literal_matches_explicit_file=s['selected_filename']==environment.name,
         captured_selection_matches=s['selection_matches'],stable=s['inputs_stable'] and s['selected_filename_stable'],
         limitations='Literal declarations and paused selected buffer match. Not an OS file-open trace or content identity stored in the runtime object. '
         'All seasons use the same three filenames in this route, so this asset comparison alone cannot distinguish season order. '
         'Editor, invalid-season and fallback-weather branches are statically traced but not exercised. No path from process memory was opened.')
(root/'environment-selection-summary.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
