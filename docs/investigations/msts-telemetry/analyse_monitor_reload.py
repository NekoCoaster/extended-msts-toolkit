"""Offline monitor comparison from retained source snapshots; never accesses MSTS."""
import json,struct,hashlib
from pathlib import Path
root=Path(__file__).resolve().parent
paths=[root/'captures/save-object-sources-paused-01/sources.json',root/'captures/after-reload-object-sources-01/sources.json']
a,b=[json.loads(p.read_text(encoding='utf-8')) for p in paths]
def cars(x):return {c['id']:c for t in x['trains'] for c in t['cars'] if 'subobjects' in c}
aa,bb=cars(a),cars(b);assert aa.keys()==bb.keys();rows=[]
for ident in sorted(aa):
 c,d=aa[ident],bb[ident];x={s['offset']:s for s in c['subobjects']};y={s['offset']:s for s in d['subobjects']};assert x.keys()==y.keys()
 for off in x:
  left,right=x[off],y[off];u,v=bytes.fromhex(left['raw']['hex']),bytes.fromhex(right['raw']['hex']);assert len(u)==len(v)==0x3c
  delta=[hex(i+4) for i in range(0,0x38,4) if u[i:i+4]!=v[i:i+4]]
  enable=lambda obj:struct.unpack_from('<I',bytes.fromhex(obj['engine_raw']['hex']),int(off,16)-0x292)[0]
  rows.append(dict(vehicle_id=ident,slot=off,enable_before=enable(c),enable_after=enable(d),changed_nonpointer_words=delta,changed_values=[dict(offset=h,before_u32=struct.unpack_from("<I",u,int(h,16)-4)[0],after_u32=struct.unpack_from("<I",v,int(h,16)-4)[0],before_f32=struct.unpack_from("<f",u,int(h,16)-4)[0],after_f32=struct.unpack_from("<f",v,int(h,16)-4)[0]) for h in delta],definition_index_before=left['saved_definition_index'],definition_index_after=right['saved_definition_index'],definition_pointer_changed=left['definition_pointer']!=right['definition_pointer'],source_checks_stable=all([left['raw']['stable'],right['raw']['stable'],left['stable'],right['stable'],c['engine_raw']['stable'],d['engine_raw']['stable']])))
out=dict(sources=[dict(path=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths],clocks=[a['dayclock'],b['dayclock']],paused=[a['paused'],b['paused']],rows=rows,limits='Historical single player reload fixture;not instantaneous. Compares four saved slots only,excluding raw pointer bytes from value comparison and comparing rebuilt definition indexes instead. Not a controlled active countdown/intervention restoration test;no AI or overspeed-slot restoration proof.')
(root/'monitor-reload-comparison-20261010.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
