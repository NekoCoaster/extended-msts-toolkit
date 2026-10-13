"""Map manually reviewed native steam debug consumers; retain exact labels."""
import json
from pathlib import Path
from binary_fields import PE
root=Path(__file__).resolve().parent;p=PE();asm=(root/'pass82/0060997a.asm').read_text()
spec=[
('water_mass',0x2ce,0x771cd4,'lb',None),
('generation_rate',0x316,0x771bcc,'unresolved rate unit',None),
('usage_rate',0x312,0x771b94,'unresolved rate unit',None),
('cylinder_rate',0x31a,0x771b54,'unresolved rate unit',None),
('exhaust_usage_rate',0x31e,0x771b08,'unresolved rate unit',None),
('wheel_omega',0x2b2,0x771ad8,'angular speed; unit unresolved',None),
('smoke_colour',0x32a,0x771aa8,'native scalar; range unresolved',None),
('smoke_release_rate',0x332,0x771a68,'unresolved rate unit',None),
('priming',0x336,0x771a14,'native scalar; unit unresolved',None),
('blowback',0x33a,0x7719b0,'native scalar; unit unresolved',None),
('critical_blowback',0x296,0x7719d8,'boolean',0x20),
('tender_water_capacity',0x1de,0x77195c,'lb','definition'),
('tender_coal_mass',0x2e2,0x77190c,'lb',None),
('tender_coal_capacity',0x1e2,0x77190c,'lb','definition'),
('coal_burn_rate_raw',0x32e,0x7718c0,'rate timebase unresolved',None),
('energy_output',0x306,0x77188c,'native energy/output unit unresolved',None),
('wheel_slip',0x84,0x77185c,'boolean',1),
('usage_exceeds_exhaust_limit',0x296,0x771814,'boolean',0x100),
('maximum_steam_rate',0x4ae,0x771798,'unresolved rate unit',None)]
rows=[]
for name,offset,label,unit,extra in spec:
 assert f'0x{offset:x}]' in asm and f'PUSH 0x{label:x}' in asm
 rows.append(dict(name=name,offset=offset,base='engine_definition' if extra=='definition' else 'lead',mask=extra if isinstance(extra,int) else None,units=unit,label_address=hex(label),label=p.string(label)))
(root/'steam-debug-fields.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(len(rows))
