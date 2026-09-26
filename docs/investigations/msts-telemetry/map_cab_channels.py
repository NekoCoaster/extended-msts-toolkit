"""Map exact installed-image cab enums to native dispatcher branches.

These are STATIC mappings. A routed branch is not proof of a valid live value.
"""
from binary_fields import PE
from pathlib import Path
import json,re,hashlib
R=Path(__file__).resolve().parent;p=PE()
dispatchers=[dict(cab_type=1,engine='electric',function=0x41f357,byte_map=0x4205a4,jump_table=0x4204fc,minimum=0,maximum=66,default=0x4204ef),
             dict(cab_type=2,engine='diesel',function=0x42064b,byte_map=0x42181a,jump_table=0x421772,minimum=0,maximum=66,default=0x421765),
             dict(cab_type=3,engine='steam',function=0x4218ae,byte_map=0x422ad1,jump_table=0x422a55,minimum=4,maximum=61,default=0x422a48)]
channels=[];cabdecl=json.loads((R/'inventory.json').read_text())['data_points'];declared={r['id'][4:] for r in cabdecl if r['id'].startswith('cab.') and any(isinstance(e,dict) and str(e.get('file','')).lower().endswith('.cvf') for e in r['evidence'])}
for n in range(68):
    a=0x77fce0+n*4;ptr=p.u(a);name=p.string(ptr);row=dict(enum=n,enum_hex=hex(n),name=name,name_pointer=hex(ptr),table_slot=hex(a),installed_cab_declaration=name in declared,dispatch=[])
    for d in dispatchers:
        result=dict(engine=d['engine'],cab_view_type=d['cab_type'],function=hex(d['function']))
        if n<d['minimum'] or n>d['maximum']:
            result.update(status='not routed by this base dispatcher',destination=hex(d['default']))
        else:
            index=p.read(d['byte_map']+n-d['minimum'],1)[0];dest=p.u(d['jump_table']+index*4)
            result.update(jump_index=index,destination=hex(dest),status='static branch identified; runtime availability unverified')
            if dest==d['default']:result['status']='default branch; no display update established'
            if not d['function']<=dest<d['jump_table']:
                result['status']='invalid or out-of-dispatcher table destination; not a supported branch'
                result['warning']='Raw table arithmetic only; do not execute this destination or claim telemetry support.'
                row['dispatch'].append(result)
                continue
            # The decompiler uses the remapped byte value as its switch case for electric/diesel,
            # but the actual enum for steam. Preserve source context, not inferred meanings.
            f=R/'pass01b'/f'{d["function"]:08x}.c';lines=f.read_text().splitlines();wanted=n if d['engine']=='steam' else index
            for i,line in enumerate(lines):
                m=re.fullmatch(r'(\s*)case (0x[0-9a-f]+|\d+):',line)
                if not m or int(m[2],0)!=wanted:continue
                indent=len(m[1])
                if indent!=(6 if d['engine']=='diesel' else 2):continue
                end=i+1
                while end<len(lines):
                    m2=re.match(r'(\s*)(?:case |default:)',lines[end])
                    if m2 and len(m2[1])==indent:break
                    end+=1
                result['decompiler_file']=str(f.relative_to(R));result['decompiler_line']=i+1
                result['decompiler_excerpt']='\n'.join(lines[i:end])
                result['warning']='Decompiler shared-helper control flow is malformed; enum/branch association comes from raw PE jump table and assembly, not reconstructed switch condition.'
                break
        row['dispatch'].append(result)
    channels.append(row)
meta=dict(executable=str(p.path),sha256=hashlib.sha256(p.data).hexdigest(),table='0x77fce0; 68 pointers',
          basis=['pass01b/0041c4ba.c: cab-view type dispatcher','pass01b/0041f357.asm','pass01b/0042064b.asm','pass01b/004218ae.asm','pass04/00422f06.asm'],
          warning='CabViewType mapping differs from player control-type enum. Base channels only; see EXTENDED-CAB-FINDINGS.md for extended aliases, no-update branches and range/table overlap.',channels=channels)
(R/'native-cab-map.json').write_text(json.dumps(meta,indent=2))
lines=['# Native cab channel discovery','','Static installed-binary evidence. Branches and declared names are not blanket runtime-support claims. Cab view types: electric 1, diesel 2, steam 3.','','| ID | Native name | In installed cabs | Electric / diesel / steam branch |','|---|---|---|---|']
for c in channels:lines.append(f'| {c["enum_hex"]} | {c["name"]} | {c["installed_cab_declaration"]} | '+ ' / '.join(x['destination'] for x in c['dispatch'])+' |')
(R/'NATIVE-CAB-MAP.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(channels=len(channels),not_in_installed_cabs=[x['name'] for x in channels if not x['installed_cab_declaration']],routed_excerpts=sum('decompiler_excerpt' in d for c in channels for d in c['dispatch']))))
