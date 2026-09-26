"""Bounded ASV SaveHeader prefix guided by current native writer argument order."""
import hashlib,json,struct
from pathlib import Path
root=Path(__file__).resolve().parent;p=Path('C:/MSTS/ROUTES/USA2/ACTIVITIES/evegrain.asv');data=p.read_bytes()
token,size=struct.unpack_from('<II',data,32);assert token==0x40495
end=40+size;at=40;fields=[]
def get(fmt,name,source):
    global at
    size=struct.calcsize('<'+fmt)
    if at+size>end:raise ValueError('Header bound')
    value=struct.unpack_from('<'+fmt,data,at)[0];fields.append(dict(name=name,offset=at,type=fmt,value=value,source=source));at+=size;return value
label_count=get('B','block_label_units','binary block framing assumption');assert label_count==0
get('I','initial_zero','0049f79f EDX=0,writer+38')
get('I','non_explore_flag','0049f7bb compares selected_context+28 to1')
for name,source in [('route_string_14','runtime route+14 or empty nonruntime'),('route_string_04','runtime route+4 or empty nonruntime'),('activity_string_04','runtime selected_context+4 or empty nonruntime'),('activity_basename','selected_context+1c basename'),('activity_string_0c','selected_context+c'),('activity_string_08','selected_context+8 or empty')]:
    count=get('H',name+'_units',source);start=at
    if count>4096 or at+count*2>end:raise ValueError('UTF16 field bound')
    value=data[at:at+count*2].decode('utf-16le');at+=count*2
    fields.append(dict(name=name,offset=start,type='UTF16',value=value,source=source))
get('i','origin_tile_x','[0079d118],writer+3c')
get('i','origin_tile_z','[0079d11c],writer+3c')
get('I','activity_context_word0','selected_context+0 orFFFFFFFF')
get('I','track_database_word22c','first[[80a10c]] node+8 object+22c')
get('I','road_database_word22c','optional first[[80a110]] node+8 object+22c orFFFFFFFF')
out=dict(source=str(p),sha256=hashlib.sha256(data).hexdigest(),header_end=end,prefix_end=at,remaining_bytes=end-at,fields=fields,
    limitations='Partial stored header only. String lengths/framing are structurally corroborated by readable labels and bounds, not full binary-writer implementation. Scalar argument sources traced; unknown words are not named revisions/IDs. Saved origin is not current origin; tail/date/camera blocks undecoded.')
(root/'save-header-prefix.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
