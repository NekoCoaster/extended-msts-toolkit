"""Compare native squared distance and preserve targeted SMS metadata hashes."""
import hashlib,json,re,struct
from pathlib import Path
root=Path(__file__).resolve().parent
s=json.loads((root/'captures/receiver-distance-paused-01/receivers.json').read_text(encoding='utf-8'))['snapshot']
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
rows=[]
for r in s['receivers']:
    delta=[f32(a-b) for a,b in zip(r['position'],s['listener_position'])]
    expected=f32(sum(x*x for x in delta))
    rows.append(dict(handle=r['handle'],label=r['definition_label'],skipped=bool(r['flags']&4),stored=r['stored_squared_distance'],reconstructed=expected,absolute_error=abs(expected-r['stored_squared_distance'])))
assets=[]
for name in ['acelacab.sms','acelaeng.sms','acelawag.sms','acelapas.sms']:
    p=Path('C:/MSTS/TRAINS/TRAINSET/ACELA/SOUND')/name;b=p.read_bytes();text=b.decode('utf-16') if b.startswith((b'\xff\xfe',b'\xfe\xff')) else b.decode('cp1252')
    assets.append(dict(path=str(p),sha256=hashlib.sha256(b).hexdigest(),distance_declarations=re.findall(r'\bDistance\s*\(\s*([\d.]+)',text,re.I),stream_count_declarations=re.findall(r'\bStreams\s*\(\s*(\d+)',text,re.I),limitations='All literal occurrences; not a scalability-group resolver or full SMS parser.'))
d=dict(rows=rows,assets=assets,limitations='Float32 coordinate differences, then double sum and float32 rounding approximate native x87 path. Snapshot only; not moving accuracy or global coordinate-origin validation.')
(root/'receiver-distance-summary.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
print(json.dumps(dict(compared=sum(not x['skipped'] for x in rows),exact=sum(not x['skipped'] and x['absolute_error']==0 for x in rows),max_error=max(x['absolute_error'] for x in rows if not x['skipped']),skipped=sum(x['skipped'] for x in rows),assets=assets)))
