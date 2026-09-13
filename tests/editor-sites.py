"""Verify toolset hook instructions in supported local executable fixtures."""
import re, struct, sys
from pathlib import Path
for name in sys.argv[1:]:
    b = Path(name).read_bytes()
    pe = struct.unpack_from('<I', b, 60)[0]
    count = struct.unpack_from('<H', b, pe+6)[0]
    table = pe+24+struct.unpack_from('<H', b, pe+20)[0]
    def read(va, n):
        for i in range(count):
            _, _, rva, size, raw = struct.unpack_from('<8sIIII', b, table+i*40)
            if rva <= va-0x400000 < rva+size:
                o = raw+va-0x400000-rva
                return b[o:o+n]
        raise AssertionError(hex(va))
    for a, h in [(0x696c00,'a154998200'), (0x55521c,'558bec83ec10'),
                 (0x44390a,'ff15b4dd8400'), (0x6bae0e,'8b7c24188b07'), (0x6bb236,'8b4c24388b01')]:
        assert read(a,len(bytes.fromhex(h))) == bytes.fromhex(h), (name,hex(a))
    for a in [0x4999b0,0x6764b3,0x451d4f]:
        assert read(a,5) == b'\xe8'+struct.pack('<i',0x6bad60-a-5), (name,hex(a))
    for a,t in [(0x44a8e6,0x6b6390),(0x44a8ba,0x40171c),(0x48ff6b,0x4040fc)]:
        assert read(a,5) == b'\xe8'+struct.pack('<i',t-a-5), (name,hex(a))
    for axis, target in [('x',0x770560),('y',0x77055c)]:
        source=(Path(__file__).resolve().parents[1]/'runtime/editor_picking.h').read_text()
        sites=re.search(r'editor_pick_'+axis+r'_sites\[\]=\{([^}]+)\}',source)[1]
        for a in (int(x,16) for x in sites.split(',')):
            assert read(a,6)==b'\xd8\x3d'+struct.pack('<I',target), (name,hex(a))
    for a in [0x521315,0x51cd5f,0x67360d,0x672f34,0x6413e6]:
        assert read(a,3) == bytes.fromhex('558bec'), (name,hex(a))
    print('PASS editor frame calls, window procedure, snapping and renderer/camera/map entries:',name)
