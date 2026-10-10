"""Read-only installed CVF scan for names from the verified extension table."""
import hashlib
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parent
names_path = root / 'captures/extended-cab-names-20261010-01/names.json'
names = {entry['name']: entry['enum_hex'] for entry in json.loads(names_path.read_text())['entries']}
files, matches, skipped = [], [], []
for path in sorted(Path('C:/MSTS/TRAINS/TRAINSET').rglob('*.cvf')):
    raw = path.read_bytes()
    provenance = dict(file=str(path), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
    files.append(provenance)
    try:
        text = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8-sig')
    except UnicodeError as e:
        skipped.append(dict(**provenance, reason=str(e)))
        continue
    if 'SIMISA' not in text[:40]:
        skipped.append(dict(**provenance, reason='No recognized text signature'))
        continue
    for match in re.finditer(r'\bType\s*\(\s*"?([A-Za-z0-9_]+)"?', text, re.I):
        name = match[1].upper()
        if name in names:
            matches.append(dict(file=str(path), line=text.count('\n', 0, match.start())+1,
                                name=name, enum_hex=names[name]))
report = dict(files_scanned=len(files), files=files, matches=matches, skipped=skipped,
              names_source=names_path.relative_to(root).as_posix(),
              names_sha256=hashlib.sha256(names_path.read_bytes()).hexdigest(),
              limits='Text Type declarations only; not a complete grammar parser. Comments may match. '
                     'No claim about other installations, inactive files, runtime loading or display support.')
(root/'extended-cab-fixture-scan-20261010.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(dict(files_scanned=len(files), matches=matches, skipped=skipped)))
