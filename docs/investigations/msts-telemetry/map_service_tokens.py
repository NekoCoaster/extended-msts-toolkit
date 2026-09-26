"""Find native token label pairs and retain installed test-activity provenance."""
import hashlib,json,struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
pe=PE();r=Reader(7160);entries=[]
try:
    for token in (0x40407,0x40408,0x40409,0x4040a,0x4040b,0x4040d,0x4040f,0x40410,0x40411,0x40412):
        needle=struct.pack('<I',token);pos=0;hits=[]
        while True:
            pos=pe.data.find(needle,pos)
            if pos<0:break
            try:
                va=pe.va(pos-4);pointer=pe.u(va);label=pe.string(pointer)
                if label and label.isascii() and label.replace('_','').isalnum():hits.append(dict(entry=hex(va),label=label,disk_live_equal=r.read(va,8)==pe.read(va,8)))
            except (ValueError,OSError,struct.error):pass
            pos+=1
        entries.append(dict(token=hex(token),candidates=hits))
    files=[]
    for name in ('C:/MSTS/ROUTES/USA1/ACTIVITIES/morningmaryland.act','C:/MSTS/ROUTES/USA2/SERVICES/evegrain.srv'):
        p=Path(name);files.append(dict(path=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    result=dict(image_sha256=r.sha,tokens=entries,assets=files,limitations='Label-pointer/token pairs checked disk/live; parser destinations require assembly evidence. Activity is a future test candidate, not a completed live validation.')
    Path(__file__).with_name('service-token-map.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
finally:K.CloseHandle(r.h)
