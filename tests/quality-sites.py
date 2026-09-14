"""Verify opt-in audio and red-signal sites in local executable fixtures."""
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
 for a,h in [(0x538302,'81caa0000000'),(0x586293,'558bec83ec08'),(0x58643c,'6a02ba240000008b0dc8497b00')]:
  assert read(a,len(bytes.fromhex(h)))==bytes.fromhex(h),(name,hex(a))
 assert read(0x586449,5)==b'\xe8'+struct.pack('<i',0x58ea72-0x586449-5)
 for a,target in [(0x4013c5,0x5864ee),(0x403ecc,0x5aeeb3)]:
  assert read(a,5)==b'\xe9'+struct.pack('<i',target-a-5)
 for a,h in [(0x447e61,'558bec83ec1c'),(0x44c54d,'558bec83ec14')]:
  assert read(a,6)==bytes.fromhex(h)
 print('PASS background sound and red-signal sites:',Path(name).name)
