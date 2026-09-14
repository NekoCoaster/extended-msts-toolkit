"""Verify diagnostic IAT names/ordinals in both supported local EXE fixtures."""
import struct,sys
from pathlib import Path
expected={0x84d9a8:('dsound.dll',1),0x84d944:('ddraw.dll','DirectDrawCreateEx'),0x84db68:('kernel32.dll','LoadLibraryA'),0x84de90:('user32.dll','MessageBoxA')}
for name in sys.argv[1:]:
 b=Path(name).read_bytes();pe=struct.unpack_from('<I',b,60)[0];n=struct.unpack_from('<H',b,pe+6)[0];opt=pe+24;ss=opt+struct.unpack_from('<H',b,pe+20)[0]
 sections=[struct.unpack_from('<IIII',b,ss+i*40+8) for i in range(n)]
 def off(r):
  for vs,va,sz,raw in sections:
   if va<=r<va+max(vs,sz):return raw+r-va
  raise ValueError(r)
 def text(r):
  p=off(r);return b[p:b.index(b'\0',p)].decode()
 p=off(struct.unpack_from('<I',b,opt+104)[0]);found={}
 while True:
  oft,_,_,dll,iat=struct.unpack_from('<IIIII',b,p);p+=20
  if not dll:break
  i=0
  while True:
   v=struct.unpack_from('<I',b,off(oft or iat)+i*4)[0]
   if not v:break
   address=0x400000+iat+i*4
   if address in expected:found[address]=(text(dll).lower(),v&65535 if v&0x80000000 else text(v+2))
   i+=1
 assert found==expected,(name,found)
 print('PASS deep diagnostic import slots:',Path(name).name)
