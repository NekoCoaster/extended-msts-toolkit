"""Lexical PAT wait candidates; no runtime activation or complete parser claim."""
import hashlib,json,re
from pathlib import Path
files=[];candidates=[];errors=[]
for p in sorted(Path('C:/MSTS/ROUTES').glob('*/PATHS/*.pat')):
 raw=p.read_bytes();info=dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest())
 try:text=raw.decode('utf-16') if raw[:2] in (b'\xff\xfe',b'\xfe\xff') else raw.decode('utf-8-sig')
 except UnicodeError as e:errors.append(dict(**info,error=str(e)));continue
 matches=list(re.finditer(r'\bTrPathNode\s*\(\s*([0-9a-fA-F]+)\s+(\d+)\s+(\d+)\s+(\d+)\s*\)',text,re.I))
 tokens=len(re.findall(r'\bTrPathNode\s*\(',text,re.I));files.append(dict(**info,tokens=tokens,parsed=len(matches)))
 for index,m in enumerate(matches):
  packed=int(m[1],16)
  if packed&2:candidates.append(dict(**info,index=index,packed=m[1],flags=packed&65535,duration_candidate=packed>>16,primary_successor=int(m[2]),secondary_successor=int(m[3]),pdp_index=int(m[4]),reverse_bit_precedes_wait=bool(packed&1)))
report=dict(files=files,file_count=len(files),errors=errors,candidates=candidates,unparsed_tokens=sum(x['tokens']-x['parsed'] for x in files),limits='First packed word low bit2 candidates only. Other flag precedence,path validation,activity/service usage and runtime values remain to be checked. Lexical scan is not a full grammar parser; no files modified.')
Path(__file__).with_name('path-wait-fixture-scan-20261010.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(files=len(files),errors=len(errors),unparsed_tokens=report['unparsed_tokens'],candidate_count=len(candidates),examples=candidates[:5])))
