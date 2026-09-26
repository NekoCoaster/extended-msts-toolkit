"""Read-only save-related installed file and executable-string reconnaissance."""
import hashlib,json,re
from pathlib import Path
from binary_fields import PE
root=Path(__file__).resolve().parent;install=Path('C:/MSTS');pe=PE()
files={ext:sorted(str(p) for p in install.rglob('*'+ext)) for ext in ['.sav','.asv']}
selected=install/'ROUTES/USA2/ACTIVITIES/evegrain.asv';data=selected.read_bytes()
strings=[]
raw=pe.read(0x75b400,0x300)
for m in re.finditer(rb'(?:[\x20-\x7e]\x00){4,}',raw):
    strings.append(dict(address=hex(0x75b400+m.start()),text=m.group().decode('utf-16le')))
out=dict(image_sha256=hashlib.sha256(pe.data).hexdigest(),installed_counts={ext:len(v) for ext,v in files.items()},
         save_files=files['.sav'],selected_asset=dict(path=str(selected),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),prefix64_hex=data[:64].hex()),
         native_string_window=strings,limitations='Extensions/strings are discovery leads only, not proof of save-state schema. No native save/load invocation or file modification.')
(root/'save-surface-survey.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
