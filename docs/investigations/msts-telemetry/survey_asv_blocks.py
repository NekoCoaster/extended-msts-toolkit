"""Test a bounded top-level token/length partition; payloads remain undecoded."""
import hashlib,json,struct
from pathlib import Path
root=Path(__file__).resolve().parent;p=Path('C:/MSTS/ROUTES/USA2/ACTIVITIES/evegrain.asv');data=p.read_bytes()
mapping=json.loads((root/'save-token-map.json').read_text());names={int(pair['token'],16):r['label'] for r in mapping['labels'] for pair in r['pairs']}
rows=[];at=32;error=None
while at<len(data):
    if len(rows)>=4096 or at+8>len(data):error='Header/count bound';break
    token,size=struct.unpack_from('<II',data,at);end=at+8+size
    if end>len(data) or size<1:error='Payload length bound';break
    rows.append(dict(offset=at,token=hex(token),label=names.get(token),payload_bytes=size,end=end,prefix16_hex=data[at+8:min(end,at+24)].hex()))
    at=end
out=dict(source=str(p),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),header_ascii=data[:32].decode('ascii',errors='replace'),
         assumed_layout='32-byte header then repeated uint32 native-token,uint32 payload-byte-length,payload',blocks=rows,
         terminal_offset=at,exact_partition=at==len(data) and error is None,error=error,
         limitation='Successful partition is structural consistency, not semantic decoding. Does not prove all ASV/SAV variants, live equivalence, or individual saved fields. No asset edits.')
(root/'asv-block-survey.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
