"""Check timing instruction sites in local, undistributed game fixtures."""
import struct,sys
from pathlib import Path
for name in sys.argv[1:]:
 b=Path(name).read_bytes();pe=struct.unpack_from('<I',b,60)[0]
 count=struct.unpack_from('<H',b,pe+6)[0];table=pe+24+struct.unpack_from('<H',b,pe+20)[0]
 def read(va,n):
  for i in range(count):
   _,_,rva,size,raw=struct.unpack_from('<8sIIII',b,table+i*40)
   if rva<=va-0x400000<rva+size:
    o=raw+va-0x400000-rva;return b[o:o+n]
  raise AssertionError(hex(va))
 for a,t in [(0x6ba183,0x6ad0f0),(0x48fdd6,0x403661)]:
  assert read(a,5)==b'\xe8'+struct.pack('<i',t-a-5),(name,hex(a))
 assert read(0x403661,5)==b'\xe9'+struct.pack('<i',0x4b7b20-0x403661-5)
 for a,h in [(0x645af0,'558bec83ec10'),(0x645b13,'d945fcd84018'),(0x645b22,'d945fcd8421c')]:
  assert read(a,len(bytes.fromhex(h)))==bytes.fromhex(h),(name,hex(a))
 print('PASS timing sites:',Path(name).name)
