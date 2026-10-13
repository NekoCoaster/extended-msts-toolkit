"""Read-only PE address mapping and bounded native field-table inspection."""
from pathlib import Path
import struct,hashlib,json,argparse
class PE:
    def __init__(self,path='C:/MSTS/train.exe'):
        self.path=Path(path);self.data=self.path.read_bytes();pe=struct.unpack_from('<I',self.data,0x3c)[0]
        assert self.data[pe:pe+4]==b'PE\0\0'
        count=struct.unpack_from('<H',self.data,pe+6)[0];optsize=struct.unpack_from('<H',self.data,pe+20)[0]
        self.base=struct.unpack_from('<I',self.data,pe+24+28)[0];self.sections=[]
        for i in range(count):
            off=pe+24+optsize+i*40;vs,rva,rs,raw=struct.unpack_from('<IIII',self.data,off+8)
            self.sections.append((self.data[off:off+8].rstrip(b'\0').decode(),rva,vs,raw,rs))
    def va(self,raw):
        for name,rva,vs,start,size in self.sections:
            if start<=raw<start+size:return self.base+rva+raw-start
        return None
    def raw(self,va):
        rva=va-self.base
        for name,start,vs,raw,size in self.sections:
            if start<=rva<start+size:return raw+rva-start
        raise ValueError(f'Not backed by disk: {va:#x}')
    def read(self,va,size):
        off=self.raw(va);return self.data[off:off+size]
    def u(self,va):return struct.unpack('<I',self.read(va,4))[0]
    def string(self,va,wide=True,limit=256):
        step=2 if wide else 1;out=bytearray()
        for i in range(limit):
            b=self.read(va+i*step,step)
            if b==b'\0'*step:break
            out.extend(b)
        return out.decode('utf-16le' if wide else 'ascii',errors='replace')
    def find(self,text):
        hits=[]
        for enc in ('ascii','utf-16le'):
            value=text.encode(enc);pos=0
            while True:
                pos=self.data.find(value,pos)
                if pos<0:break
                hits.append(dict(encoding=enc,raw=hex(pos),va=hex(self.va(pos)) if self.va(pos) else None));pos+=len(value)
        return hits
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('text',nargs='+');a=p.parse_args();pe=PE()
    print(json.dumps({x:pe.find(x) for x in a.text},indent=2))
