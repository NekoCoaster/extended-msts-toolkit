"""Decode native header list entries after verifying enclosing bounds."""
import hashlib,json,struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
root=Path(__file__).resolve().parent;tail=json.loads((root/'save-header-tail.json').read_text());data=Path(tail['source']).read_bytes();assert hashlib.sha256(data).hexdigest()==tail['sha256']
pe=PE();r=Reader(7160);labels={}
try:
    for token in [0x404c9,0x404c8,0x404cb,0x404ca,0x40068,0x4026f]:
        needle=struct.pack('<I',token);pos=0;found=[]
        while True:
            pos=pe.data.find(needle,pos)
            if pos<0:break
            try:
                entry=pe.va(pos-4);text=pe.string(pe.u(entry))
                if text and text.isascii() and text.replace('_','').isalnum():found.append(dict(entry=hex(entry),label=text,disk_live_equal=r.read(entry,8)==pe.read(entry,8)))
            except (ValueError,OSError,struct.error):pass
            pos+=1
        labels[hex(token)]=found
finally:K.CloseHandle(r.h)
rows=[]
for block in tail['blocks']:
    at=block['offset']+8;end=block['end'];assert data[at]==0;at+=1;entries=[]
    def string():
        global at
        if at+2>end:raise ValueError('String header bound')
        n=struct.unpack_from('<H',data,at)[0];at+=2
        if at+n*2>end:raise ValueError('String payload bound')
        value=data[at:at+n*2].decode('utf-16le');at+=n*2;return value
    if block['token'] in ['0x404c9','0x404c8','0x404cb']:
        while at<end:
            start=at;token,size=struct.unpack_from('<II',data,at);child_end=at+8+size;at+=8
            if token!=0x4026f or child_end>end or data[at]!=0:raise ValueError('Child token/bound/label')
            at+=1;name=string();value=struct.unpack_from('<I',data,at)[0];at+=4
            if at!=child_end:raise ValueError('Child payload remainder')
            entries.append(dict(offset=start,name=name,word=value))
    elif block['token']=='0x404ca':
        name=string();value=struct.unpack_from('<I',data,at)[0];at+=4;entries.append(dict(name=name,word=value))
    else:
        value=struct.unpack_from('<I',data,at)[0];at+=4;entries.append(dict(word=value))
    if at!=end:raise ValueError('Block remainder')
    rows.append(dict(token=block['token'],entries=entries))
out=dict(source=tail['source'],sha256=tail['sha256'],labels=labels,blocks=rows,
         limitation='Stored names and raw words only;numeric words are not assigned checksum/version/ID semantics. Writer omits services without loaded+130resource. Not a complete installed-resource inventory or current saved-game snapshot.')
(root/'save-header-lists.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
