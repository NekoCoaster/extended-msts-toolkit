"""Corroborate loaded Default ExtraParameters; never evaluate asset expressions."""
import argparse,hashlib,json,re,struct
from pathlib import Path
from read_live import Reader,K
from binary_fields import PE
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);a=p.parse_args()
asset=Path('C:/MSTS/TRAINS/TRAINSET/DEFAULT/default.wag');data=asset.read_bytes();text=data.decode('utf-16') if data[:2] in (b'\xff\xfe',b'\xfe\xff') else data.decode('utf-8-sig')
block=text.split('ExtraParameters (',1)[1].split('\n\t)',1)[0];values=re.findall(r'"([^"\r\n]*)"',block)
if len(values)!=25:raise ValueError('Expected25 quoted Default parameters')
r=Reader(a.pid)
try:
    start=r.f(0x80acd4);obj=r.u(0x80aa1c);definition=r.u(obj+0x94);rows=[]
    pe=PE();token=pe.u(0x795664);selector=pe.read(0x617120+token-0x40164,1)[0];target=pe.u(0x6170d8+selector*4)
    assert token==0x4017b and target==0x616a70
    assert r.u(0x795664)==token and r.read(0x617120+token-0x40164,1)==bytes([selector]) and r.u(0x6170d8+selector*4)==target
    name=r.read(definition+8,64).decode('utf-16le',errors='replace').split('\0')[0]
    for i,value in enumerate(values):
        expr,_,label=value.partition('#');entry=dict(index=i,offset=hex(0x770+i*4),source_expression=expr.strip(),source_comment=label.strip(),loaded_float=r.f(definition+0x770+i*4))
        if i in (23,24):
            expected=struct.unpack('<f',struct.pack('<f',float(expr.strip())))[0];entry.update(expected_float32=expected,exact_match=entry['loaded_float']==expected)
        rows.append(entry)
    d=dict(image_sha256=r.sha,asset_path=str(asset),asset_sha256=hashlib.sha256(data).hexdigest(),sim_time=start,simulation_object=obj,default_definition=definition,loaded_name=name,parameters=rows,sim_time_after=r.f(0x80acd4),paused=r.u(0x7be0f4),limitations='Only indices23/24 numerically compared; other expressions/comments retained as configuration provenance, not validated runtime semantics. No asset expression execution.')
    d['parser_dispatch']=dict(token=hex(token),selector=selector,target=hex(target),live_selected_data_match=True)
    Path(__file__).with_name('default-parameters-map.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in d.items() if k!='parameters'}|{'thresholds':rows[23:]}))
finally:K.CloseHandle(r.h)
