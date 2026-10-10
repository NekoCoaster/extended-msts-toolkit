"""Lexical scan for explicit arrival/departure intervals;no asset modification."""
import hashlib,json,re
from pathlib import Path
files=[];positive=[]
for p in sorted(Path('C:/MSTS/ROUTES').glob('*/TRAFFIC/*.trf')):
    raw=p.read_bytes();text=raw.decode('utf-16') if raw[:2] in (b'\xff\xfe',b'\xfe\xff') else raw.decode('utf-8-sig',errors='replace')
    pairs=[(float(a),float(b)) for a,b in re.findall(r'ArrivalTime\s*\(\s*([^()\s]+)\s*\)\s*DepartTime\s*\(\s*([^()\s]+)',text,re.I)]
    files.append(dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest(),arrival_tokens=len(re.findall(r'\bArrivalTime\s*\(',text,re.I)),pairs=len(pairs),equal=sum(a==b for a,b in pairs),positive=sum(b>a for a,b in pairs),negative=sum(b<a for a,b in pairs),negative_arrival=sum(a<0 for a,b in pairs)))
    positive.extend(dict(file=str(p),arrival=a,departure=b) for a,b in pairs if b>a)
report=dict(files=files,file_count=len(files),pairs=sum(x['pairs'] for x in files),arrival_tokens=sum(x['arrival_tokens'] for x in files),positive_pairs=positive,
    limitations='Lexical scan of installed route TRAFFIC/*.trf,not full SIMIS parser or runtime-use proof. Adjacent numeric fields only;report token/pair counts expose unmatched cases. Preliminary unsigned-number scan missed8negative equal-time pairs;this signed numeric scan supersedes it.')
(Path(__file__).resolve().parent/'ai-timetable-fixture-scan-20261010.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('files','limitations')}))
