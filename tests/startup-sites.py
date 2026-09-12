"""Verify startup call-site bytes in user-supplied executable fixtures."""
import struct,sys
from pathlib import Path
for name in sys.argv[1:]:
 b=Path(name).read_bytes();pe=struct.unpack_from('<I',b,60)[0];count=struct.unpack_from('<H',b,pe+6)[0];table=pe+24+struct.unpack_from('<H',b,pe+20)[0]
 def offset(va):
  for i in range(count):
   _,_,rva,size,raw=struct.unpack_from('<8sIIII',b,table+i*40)
   if rva<=va-0x400000<rva+size:return raw+va-0x400000-rva
  raise AssertionError(hex(va))
 for address,target in [(0x44cceb,0x402590),(0x44cd0d,0x402590),(0x6ba175,0x6ad020)]:
  o=offset(address);assert b[o:o+5]==b'\xe8'+struct.pack('<i',target-address-5),(name,hex(address))
 print('PASS startup call sites:',Path(name).name)
