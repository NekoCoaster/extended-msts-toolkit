"""Verify startup-only movie hook sites in supported local fixtures."""
import struct,sys
from pathlib import Path
for name in sys.argv[1:]:
 b=Path(name).read_bytes()
 # Supported fixtures map .text VA minus image base to raw file offset.
 def read(va,n):return b[va-0x400000:va-0x400000+n]
 for a,target in [(0x52fc29,0x52fc32),(0x52fbbe,0x403247)]:
  assert read(a,5)==b'\xe8'+struct.pack('<i',target-a-5),(name,hex(a))
 assert read(0x52fc32,9)==bytes.fromhex('558bec81ec68010000')
 print('PASS startup movie hook sites:',Path(name).name)
