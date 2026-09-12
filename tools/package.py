"""Validate and package the adjacent NEMT directory without local game access."""
from pathlib import Path
import hashlib,json,re,zipfile
root=Path(__file__).resolve().parents[1]
def release_file(p):return p.is_file() and not any(x in {'.git','work','__pycache__'} for x in p.relative_to(root).parts)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
integrity=json.loads((root/'runtime/integrity.json').read_text(encoding='utf-8'))
assert digest(root/'runtime/DINPUT.dll')==integrity['DINPUT.dll'],'DLL integrity mismatch; rebuild first'
for p in root.rglob('*.md'):
 for link in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  if '://' not in link and not link.startswith('#'):
   assert (p.parent/link.split('#')[0]).exists(),(p,link)
files=sorted((p for p in root.rglob('*') if release_file(p) and p.name!='SHA256SUMS.txt'),key=lambda p:p.relative_to(root).as_posix())
assert not any(p.suffix.lower() in {'.exe','.bak','.pyc','.pub'} or p.name in {'MstsCrawl.dll','DINPUT.def','known_hosts'} for p in files)
assert not any(re.search(r'-----BEGIN [A-Z ]+'+r'PRIVATE KEY-----',p.read_text(encoding='utf-8',errors='ignore')) for p in files)
(root/'SHA256SUMS.txt').write_text(''.join(digest(p)+'  '+p.relative_to(root).as_posix()+'\n' for p in files),encoding='utf-8',newline='')
archive=root.parent/'NEMT.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(root.rglob('*'),key=lambda p:p.relative_to(root).as_posix()):
  if release_file(p):
   info=zipfile.ZipInfo('NEMT/'+p.relative_to(root).as_posix(),(2026,1,1,0,0,0))
   info.create_system=3;info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644 << 16
   z.writestr(info,p.read_bytes(),compresslevel=9)
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for p in root.rglob('*'):
  if release_file(p):assert z.read('NEMT/'+p.relative_to(root).as_posix())==p.read_bytes()
archive.with_suffix('.zip.sha256').write_text(digest(archive)+'  NEMT.zip\n',encoding='utf-8',newline='')
print(json.dumps({'archive':str(archive),'zipBytes':archive.stat().st_size,'dllBytes':(root/'runtime/DINPUT.dll').stat().st_size,'files':len(files)+1},indent=2))
