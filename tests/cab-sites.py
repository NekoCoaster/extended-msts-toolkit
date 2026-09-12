"""Verify cab adapter's call and frame assumptions against local game fixtures."""
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
 for a,t in [(0x44de2c,0x450e3e),(0x44de88,0x450e3e),(0x44dee1,0x450e3e),(0x44df3c,0x450e3e),(0x44fe41,0x403c01),(0x41b76c,0x40259f)]:
  assert read(a,5)==b'\xe8'+struct.pack('<i',t-a-5),(name,hex(a))
 for a in [0x44dd35,0x44fe01]:assert read(a,3)==bytes.fromhex('558bec')
 for a,t in [(0x403c01,0x44dd35),(0x40259f,0x44fe01),(0x40172b,0x4b7dd8)]:
  assert read(a,5)==b'\xe9'+struct.pack('<i',t-a-5),(name,hex(a))
 assert read(0x450e94,3)==bytes.fromhex('c20400')
 print('PASS cab call chain, frame prologues, mode thunk and rotation ABI:',Path(name).name)
