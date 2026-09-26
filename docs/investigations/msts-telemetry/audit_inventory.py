"""Local evidence/metadata audit. Existence and hashes are not semantic validation."""
import json,hashlib,collections
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'inventory.json').read_text());rows=data['data_points']
required=['id','meaning','applicability','value_type','units','extraction','evidence','evidence_status','update_or_lifecycle','limitations']
empty=[dict(id=r.get('id'),field=k) for r in rows for k in required if not r.get(k)]
ids=collections.Counter(r['id'] for r in rows);missing={};paths=set();unrecognized=[]
for r in rows:
    for e in r['evidence']:
        name=e if isinstance(e,str) else e.get('file') if isinstance(e,dict) else None
        if name is None:
            # Native cab routing dictionaries are structured evidence, not path references.
            if not isinstance(e,dict):unrecognized.append(dict(id=r['id'],evidence=e))
            continue
        p=Path(name);p=p if p.is_absolute() else root/p;paths.add(str(p))
        if not p.is_file():missing.setdefault(name,[]).append(r['id'])
sources=json.loads((root/'source-manifest.json').read_text());drift=[]
for name,meta in sources.items():
    p=Path(name)
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=meta['sha256']:drift.append(name)
result=dict(inventory_sha256=hashlib.sha256((root/'inventory.json').read_bytes()).hexdigest(),candidate_count=len(rows),unique_ids=len(ids),duplicate_ids=[k for k,v in ids.items() if v>1],empty_required_fields=empty,evidence_paths_checked=len(paths),missing_evidence=missing,unrecognized_evidence=unrecognized,source_files_checked=len(sources),source_hash_mismatches=drift,limitations='Local path/structure/hash audit only. Does not verify meanings, offsets, units, update cadence, coverage or runtime behavior. Published clone intentionally omits raw evidence; run in canonical workspace.')
(root/'inventory-audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
raise SystemExit(bool(empty or missing or drift or unrecognized or result['duplicate_ids']))
