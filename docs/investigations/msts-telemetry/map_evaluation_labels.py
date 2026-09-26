"""Read specific evaluation labels directly from PE resources; never load DLL code."""
import json,struct,hashlib
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K

def labels(path,ids):
    p=PE(path);pe=struct.unpack_from('<I',p.data,0x3c)[0]
    rva=struct.unpack_from('<I',p.data,pe+24+112)[0];root=p.raw(p.base+rva)
    def entries(off):
        count=sum(struct.unpack_from('<HH',p.data,root+off+12))
        return [struct.unpack_from('<II',p.data,root+off+16+i*8) for i in range(count)]
    result={}
    for typ,o in entries(0):
        if typ!=6:continue
        for block,b in entries(o&0x7fffffff):
            if block not in {x//16+1 for x in ids}:continue
            for lang,l in entries(b&0x7fffffff):
                va,size=struct.unpack_from('<II',p.data,root+(l&0x7fffffff));data=p.read(p.base+va,size);pos=0
                for i in range(16):
                    count=struct.unpack_from('<H',data,pos)[0];pos+=2
                    text=data[pos:pos+count*2].decode('utf-16le');pos+=count*2;sid=(block-1)*16+i
                    if sid in ids:result.setdefault(sid,[]).append(dict(language_id=lang,text=text))
    return result

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--pid',required=True,type=int);args=a.parse_args()
    p=PE();dll=Path('C:/MSTS/string.dll');rows=[];r=Reader(args.pid)
    try:
        for code in (2,4,8,16,32,64):
            index=p.read(0x43d75c+code-2,1)[0];target=p.u(0x43d740+index*4)
            assert p.read(target,1)==b'\xb9'
            sid=p.u(target+1)
            assert r.read(0x43d75c+code-2,1)==bytes([index]) and r.u(0x43d740+index*4)==target and r.read(target,5)==p.read(target,5)
            rows.append(dict(code=code,branch=hex(target),resource_id=sid,labels=labels(dll,{sid})[sid]))
        data=dict(image_sha256=r.sha,resource_path=str(dll),resource_sha256=hashlib.sha256(dll.read_bytes()).hexdigest(),rows=rows,display_unit_labels=labels(dll,{0x443,0x444}),live_dispatch_bytes_match=True,limitations='Installed English resources and selected switch bytes only; no proof of new event emission or all code producers.')
        Path(__file__).with_name('evaluation-label-map.json').write_text(json.dumps(data,indent=2),encoding='utf-8');print(json.dumps(data))
    finally:K.CloseHandle(r.h)
