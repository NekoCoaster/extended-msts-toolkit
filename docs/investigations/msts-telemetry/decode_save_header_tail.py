"""Decode bounded scalar/header-block layout from native writer call order."""
import hashlib,json,struct
from pathlib import Path
root=Path(__file__).resolve().parent;prefix=json.loads((root/'save-header-prefix.json').read_text());p=Path(prefix['source']);data=p.read_bytes()
assert hashlib.sha256(data).hexdigest()==prefix['sha256'];at=prefix['prefix_end'];end=prefix['header_end'];fields=[]
def take(name,fmt,source):
    global at
    size=struct.calcsize('<'+fmt)
    if at+size>end:raise ValueError('Header bound')
    values=list(struct.unpack_from('<'+fmt,data,at));fields.append(dict(name=name,offset=at,format=fmt,values=values,source=source));at+=size;return values
take('system_time_components','6I','49fda3, caller local date/time arrangement;date units need helper confirmation')
take('simulation_time_components','6I','80acc4/8/c then80acb8/bc/c0:second/minute/hour/day/month/year')
take('word809ec8','I','[809ec8],unknown semantic')
take('camera_list_index','I','index helper for[7c2a88] in[7c2ac8],orFFFFFFFF')
clock=take('clock_state_raw','11I','44bytes from80acb8 via writer+50')
take('condition_words','3I','normalized nonzero of7b7094/7b709c/7b70a0')
take('weather_season','2i','7be0d8/79a3ac')
blocks=[];error=None
while at<end:
    if at+8>end:error='Truncated nested header';break
    token,size=struct.unpack_from('<II',data,at);stop=at+8+size
    if not size or stop>end:error='Nested block bound';break
    blocks.append(dict(offset=at,token=hex(token),size=size,end=stop,prefix24_hex=data[at+8:min(stop,at+32)].hex()));at=stop
out=dict(source=str(p),sha256=prefix['sha256'],fields=fields,blocks=blocks,terminal_offset=at,expected_end=end,error=error,exact_partition=at==end and error is None,
    limitations='Scalar order guided by native writer;raw clock words not independent new fields. System-time meaning requires helper proof. Nested payloads undecoded and equality of file/layout is not save/load roundtrip or live state identity.')
(root/'save-header-tail.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
