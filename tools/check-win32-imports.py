"""Audit a PE32 binary for accidental modern-Windows runtime dependencies."""
from __future__ import annotations
from pathlib import Path
import struct,sys

if len(sys.argv) != 2:
    raise SystemExit('Usage: python tools/check-win32-imports.py path/to/file.exe')
p=Path(sys.argv[1]); data=p.read_bytes()
if data[:2] != b'MZ': raise SystemExit(f'{p}: not a PE file')
pe=struct.unpack_from('<I',data,0x3C)[0]
if data[pe:pe+4] != b'PE\0\0': raise SystemExit(f'{p}: invalid PE signature')
coff=pe+4
machine,nsec,_,_,_,opt_size,_=struct.unpack_from('<HHIIIHH',data,coff)
opt=coff+20
magic=struct.unpack_from('<H',data,opt)[0]
if magic != 0x10B: raise SystemExit(f'{p}: expected PE32/x86, got optional-header magic 0x{magic:04x}')
# PE32 data directory starts at optional header + 96, import entry is index 1.
import_rva,import_size=struct.unpack_from('<II',data,opt+96+8)
sec=opt+opt_size
sections=[]
for i in range(nsec):
    o=sec+i*40
    name=data[o:o+8].split(b'\0',1)[0].decode('ascii','replace')
    vsize,va,raw_size,raw=struct.unpack_from('<IIII',data,o+8)
    sections.append((name,va,max(vsize,raw_size),raw))

def rva_off(rva:int)->int:
    for _,va,size,raw in sections:
        if va <= rva < va+size:
            return raw+(rva-va)
    if rva < len(data): return rva
    raise ValueError(f'RVA 0x{rva:x} is not mapped')

def cstr(off:int)->str:
    end=data.index(0,off)
    return data[off:end].decode('ascii','replace')

imports={}
if import_rva:
    o=rva_off(import_rva)
    while True:
        orig,stamp,chain,name_rva,first=struct.unpack_from('<IIIII',data,o)
        if not (orig or stamp or chain or name_rva or first): break
        dll=cstr(rva_off(name_rva)).lower(); thunk=orig or first; names=[]
        t=rva_off(thunk)
        while True:
            val=struct.unpack_from('<I',data,t)[0]; t+=4
            if val==0: break
            if val & 0x80000000: names.append(f'#{val & 0xffff}')
            else: names.append(cstr(rva_off(val)+2))
        imports[dll]=names; o+=20

for dll,names in sorted(imports.items()):
    print(f'{dll}: {len(names)} imports')

bad_dll_prefixes=('api-ms-win-','ext-ms-win-')
bad_dlls={'ucrtbase.dll'}
bad_func={
    'GetSystemCpuSetInformation','SetProcessDefaultCpuSets','GetProcessDefaultCpuSets',
    'GetTickCount64','GetCurrentProcessorNumberEx','GetLogicalProcessorInformationEx',
    'InitializeCriticalSectionEx','CreateFile2','GetFileInformationByHandleEx',
}
problems=[]
for dll,names in imports.items():
    if dll in bad_dlls or dll.startswith(bad_dll_prefixes) or dll.startswith('vcruntime'):
        problems.append(f'modern runtime DLL import: {dll}')
    for name in names:
        if name in bad_func: problems.append(f'modern API imported directly: {dll}!{name}')
if machine != 0x14C: problems.append(f'not x86/i386 (machine=0x{machine:04x})')
if problems:
    raise SystemExit('\n'.join(f'ERROR: {x}' for x in problems))
print(f'{p}: PE32/x86 import audit OK')
