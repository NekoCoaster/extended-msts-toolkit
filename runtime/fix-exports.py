"""Give TCC's seven x86 stdcall exports the names imported by DirectInput clients."""
from pathlib import Path
import struct,sys
p=Path(sys.argv[1]);b=bytearray(p.read_bytes());pe=struct.unpack_from('<I',b,60)[0];optional=pe+24
assert struct.unpack_from('<H',b,pe+4)[0]==0x14c
count=struct.unpack_from('<H',b,pe+6)[0];sections=optional+struct.unpack_from('<H',b,pe+20)[0]
table=[struct.unpack_from('<IIII',b,sections+i*40+8) for i in range(count)]
def offset(rva):return next(raw+rva-va for size,va,rawsize,raw in table if va<=rva<va+max(size,rawsize))
directory=offset(struct.unpack_from('<I',b,optional+96)[0]);n=struct.unpack_from('<I',b,directory+24)[0]
assert n==7
names=offset(struct.unpack_from('<I',b,directory+32)[0]);result=[]
for i in range(n):
 start=offset(struct.unpack_from('<I',b,names+i*4)[0]);end=b.index(0,start);name=b[start:end].decode()
 clean=name.lstrip('_').split('@')[0];result.append(clean)
 b[start:end]=clean.encode()+b'\0'*(end-start-len(clean))
assert result==sorted(result)
assert set(result)=={'DirectInputCreateA','DirectInputCreateW','DirectInputCreateEx','DllCanUnloadNow','DllGetClassObject','DllRegisterServer','DllUnregisterServer'}
p.write_bytes(b);print('Verified x86 DirectInput forwarding exports:',', '.join(result))
