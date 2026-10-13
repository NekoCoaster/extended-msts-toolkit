"""Offline comparison of the fixed trailing monitor payloads in retained SaveEngine blocks."""
import json,struct,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
meta=json.loads((root/'generated-save-structure.json').read_text(encoding='utf-8'))
p=root/'captures/save-generated-01'/Path(meta['source']).name;d=p.read_bytes();assert hashlib.sha256(d).hexdigest()==meta['sha256']
s=json.loads((root/'captures/save-object-sources-paused-01/sources.json').read_text(encoding='utf-8'));cars=[c for t in s['trains'] for c in t['cars'] if 'engine_raw' in c];rows=[]
for block in (child for b in meta['blocks'] for child in b.get('children',[]) if child['token']=='0x404a3'):
 start,end=block['offset'],block['end'];token,size=struct.unpack_from('<II',d,start);assert token==0x404a3 and start+8+size==end and d[start+8]==0
 nested=start+9;token,n=struct.unpack_from('<II',d,nested);assert token==0x404a2;rawstart=nested+8+n
 raw=d[rawstart:rawstart+0x36c];matched=[c for c in cars if bytes.fromhex(c['engine_raw']['hex'])==raw];assert len(matched)==1;c=matched[0]
 tail=end-4*0x40;assert tail>=rawstart+0x36c
 for i,sub in enumerate(c['subobjects']):
  at=tail+i*0x40;payload=d[at:at+0x3c];index=struct.unpack_from('<I',d,at+0x3c)[0]
  assert payload==bytes.fromhex(sub['raw']['hex']) and index==sub['saved_definition_index']
  rows.append(dict(vehicle_id=c['id'],slot=sub['offset'],file_offset=at,raw60_matches=True,definition_index=index))
out=dict(save_sha256=meta['sha256'],matched_engine_blocks=len(rows)//4,monitor_payloads=rows,limits='Fixed tail layout from005f2d65/006106e2;engine identity joined by unique full876byte source match. Monitor payloads and indexes match pre-save source. Does not identify when later load/UI updates changed state;not general save-schema validation.')
(root/'saved-monitor-payload-comparison-20261010.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out))
