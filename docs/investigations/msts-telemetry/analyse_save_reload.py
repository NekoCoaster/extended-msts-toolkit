"""Reproduce the retained native save/reload comparison without touching the game."""
import collections,hashlib,json,struct
from pathlib import Path
root=Path(__file__).resolve().parent
def js(name):return json.loads((root/name).read_text())
a=js('captures/before-save-01/samples.jsonl');b=js('captures/after-reload-briefing-01/samples.jsonl')
p=js('captures/save-object-sources-paused-01/sources.json');q=js('captures/after-reload-object-sources-01/sources.json')
pm={c['id']:c['address'] for t in p['trains'] for c in t['cars']};qm={c['id']:c['address'] for t in q['trains'] for c in t['cars']}
assert pm.keys()==qm.keys()
aa={c['address']:c for c in a['cars']};bb={c['address']:c for c in b['cars']}
checks={}
for field in ['position','right','up','forward','velocity','angular_velocity','momentum','angular_momentum','mass','body_flags','derailed','resting']:
    differences=[]
    for k in sorted(pm):
        av=aa[pm[k]][field];bv=bb[qm[k]][field]
        if av!=bv:differences.append(dict(id=k,before=av,after=bv))
    checks[field]=dict(equal_count=len(pm)-len(differences),differences=differences)
rows=[json.loads(l) for l in (root/'captures/reload-transition-01/samples.jsonl').read_text().splitlines()]
meta=js('captures/save-generated-01/metadata.json')
data=(root/'captures/save-generated-01'/Path(meta['source']).name).read_bytes()
assert hashlib.sha256(data).hexdigest()==meta['sha256']
names={int(pair['token'],16):r['label'] for r in js('save-token-map.json')['labels'] for pair in r['pairs']}
at=32;blocks=[];train_check=None
while at<len(data):
    token,size=struct.unpack_from('<II',data,at);end=at+8+size
    assert size>=1 and end<=len(data)
    block=dict(offset=at,token=hex(token),label=names.get(token),payload_bytes=size,end=end)
    if token==0x4049e:
        pos=at+9;assert data[at+8]==0;children=[]
        while pos<end:
            t,n=struct.unpack_from('<II',data,pos);stop=pos+8+n;assert n>=1 and stop<=end
            child=dict(offset=pos,token=hex(t),label=names.get(t),payload_bytes=n,end=stop);children.append(child)
            if t==0x404a4:
                assert data[pos+8]==0
                raw=data[pos+9:pos+9+0xe2]
                ids=list(struct.unpack_from('<4I',data,pos+9+0xe2))
                expected=[v['saved_word'] for v in p['trains'][0]['references']]
                train_check=dict(raw_bytes=len(raw),raw_matches_retained_pre_save_source=raw.hex()==p['trains'][0]['raw']['hex'],saved_car_reference_ids=ids,retained_source_ids=expected,reference_ids_match=ids==expected)
            pos=stop
        assert pos==end;block['children']=children
    blocks.append(block);at=end
structure=dict(**meta,blocks=blocks,exact_partition=at==len(data),train_check=train_check,
    limitation='Top-level/object structural partition plus one train raw range/reference comparison; other payloads not decoded.')
(root/'generated-save-structure.json').write_text(json.dumps(structure,indent=2))
summary=dict(before_clock=a['sim_time'],after_clock=b['sim_time'],clock_difference=b['sim_time']-a['sim_time'],before_train=a['train'],after_train=b['train'],train_ids=[p['trains'][0]['id'],q['trains'][0]['id']],same_car_id_set=True,changed_car_addresses=sum(pm[k]!=qm[k] for k in pm),car_count=len(pm),reciprocal_links=[a['reciprocal_links'],b['reciprocal_links']],controls={k:[a[k],b[k]] for k in ['throttle','reverser','control_type']},field_comparisons=checks,transition_samples=len(rows),transition_errors=collections.Counter(s['error'] for s in rows if 'error' in s),transition_registry_errors=collections.Counter(s['registry_error'] for s in rows if 'registry_error' in s),
    limitation='Before-save paused snapshot versus post-load briefing, not an instantaneous round trip. Brief unpaused time may occur around UI/load; differences need not be restoration defects. One run does not prove ID uniqueness or general load fidelity.')
(root/'save-reload-comparison.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(dict(train_check=train_check,car_count=len(pm),changed_addresses=summary['changed_car_addresses'],equal_counts={k:v['equal_count'] for k,v in checks.items()},transition_registry_errors=summary['transition_registry_errors']),indent=2))
