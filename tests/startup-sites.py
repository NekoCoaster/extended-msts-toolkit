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
 for address,target in [(0x44cceb,0x402590),(0x44cd0d,0x402590),(0x6ba175,0x6ad020),(0x490e1d,0x401c53),(0x49105d,0x4014d3),(0x4900e7,0x4014d3),(0x566cc2,0x4023e2),(0x566d21,0x4023e2),(0x60c996,0x6ae6f0)]:
  o=offset(address);assert b[o:o+5]==b'\xe8'+struct.pack('<i',target-address-5),(name,hex(address))
 for address in [0x44cd01,0x44cd23]:
  o=offset(address);assert b[o:o+5]==bytes.fromhex('8b00ff5038')
 print('PASS startup call sites:',Path(name).name)
