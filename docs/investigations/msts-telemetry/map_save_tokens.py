"""Map exact native Save* labels to token table pairs; no schema inference."""
import hashlib,json,struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
root=Path(__file__).resolve().parent;pe=PE();survey=json.loads((root/'save-surface-survey.json').read_text());r=Reader(7160);rows=[]
try:
    for item in survey['native_string_window']:
        if not item['text'].startswith('Save'):continue
        address=int(item['address'],16);needle=struct.pack('<I',address);pos=0;matches=[]
        while True:
            pos=pe.data.find(needle,pos)
            if pos<0:break
            va=pe.va(pos)
            if va is not None:
                pair=pe.read(va,8);matches.append(dict(entry=hex(va),token=hex(struct.unpack_from('<I',pair,4)[0]),disk_live_equal=r.read(va,8)==pair))
            pos+=1
        rows.append(dict(label=item['text'],address=item['address'],pairs=matches))
    result=dict(image_sha256=r.sha,labels=rows,limitation='Table labels/tokens only; writer payload layout and runtime applicability require native consumers. No saved activity created or loaded.')
    (root/'save-token-map.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
finally:K.CloseHandle(r.h)
