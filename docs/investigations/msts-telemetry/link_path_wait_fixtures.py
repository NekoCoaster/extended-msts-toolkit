"""Route-scoped lexical linkage for provisional path wait candidates."""
import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parent
scan=json.loads((root/'path-wait-fixture-scan-20261010.json').read_text())
name=r'(?:"([^"\r\n]+)"|([^\s()]+))'
def read(p):
 raw=p.read_bytes();return raw.decode('utf-16') if raw[:2] in (b'\xff\xfe',b'\xfe\xff') else raw.decode('utf-8-sig')
def provenance(p):return dict(file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
links=[]
for value in sorted({r['path'] for r in scan['candidates']}):
 path=Path(value);route=path.parent.parent
 for srv in sorted((route/'SERVICES').glob('*.srv')):
  m=re.search(r'\bPathID\s*\(\s*'+name,read(srv),re.I)
  if not m or (m[1] or m[2]).casefold()!=path.stem.casefold():continue
  refs=[]
  for folder,ext in [('TRAFFIC','trf'),('ACTIVITIES','act')]:
   for asset in sorted((route/folder).glob('*.'+ext)):
    for match in re.finditer(r'\b(Player_Service_Definition|Service_Definition)\s*\(\s*'+name,read(asset),re.I):
     if (match[2] or match[3]).casefold()==srv.stem.casefold():refs.append(dict(**provenance(asset),role=match[1],reference=match[2] or match[3]))
  links.append(dict(path=provenance(path),service=provenance(srv),references=refs))
result=dict(links=links,limits='Route-scoped lexical direct references only;not full grammar,availability,selected activity,compiled ASV or runtime reachability proof. Repeated scheduled references retained. No assets modified.')
(root/'path-wait-fixture-links-20261010.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps([dict(service=x['service']['file'],reference_count=len(x['references']),files=sorted({r['file'] for r in x['references']})) for x in links]))
