"""Inspect full SIMIS leaf lengths and parser balance without modifying source assets."""
import json,re,hashlib,collections
from pathlib import Path
root=Path(__file__).resolve().parent
token=re.compile(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()]+')
manifest=json.loads((root/'source-manifest.json').read_text());issues=[];long_leaves={};mixed={};counts=collections.Counter()
for name,meta in manifest.items():
    p=Path(name);raw=p.read_bytes();text=raw.decode('utf-16') if raw[:2] in [b'\xff\xfe',b'\xfe\xff'] else raw.decode('utf-8-sig',errors='replace')
    tokens=list(token.finditer(text));stack=[];i=0
    while i<len(tokens):
        m=tokens[i];t=m.group();line=text.count('\n',0,m.start())+1
        if t==')':
            if not stack:issues.append(dict(file=name,line=line,error='unmatched closing parenthesis'))
            else:
                node=stack.pop();path=node['path'];key=p.suffix.lower()+':'+'.'.join(path)
                if not node['skip']:
                    if node['children']==0:
                        counts['leaves']+=1
                        if len(node['atoms'])>20 and p.suffix.lower()!='.cvf':long_leaves.setdefault(key,[]).append(dict(file=name,line=node['line'],token_count=len(node['atoms']),example=node['atoms'][:24]))
                    elif node['atoms'] and p.suffix.lower()!='.cvf':mixed.setdefault(key,[]).append(dict(file=name,line=node['line'],direct_atoms=node['atoms'][:24],child_nodes=node['children']))
            i+=1;continue
        if t=='(':
            issues.append(dict(file=name,line=line,error='opening parenthesis without name'));i+=1;continue
        if i+1<len(tokens) and tokens[i+1].group()=='(':
            path=(stack[-1]['path'] if stack else [])+[t]
            skip=(stack[-1]['skip'] if stack else False) or t.lower() in ['comment','_skip']
            if stack:stack[-1]['children']+=1
            stack.append(dict(path=path,line=line,skip=skip,atoms=[],children=0));i+=2;continue
        if stack:stack[-1]['atoms'].append(t)
        i+=1
    for n in stack:issues.append(dict(file=name,line=n['line'],error='unclosed node',path=n['path']))
report=dict(source_files=len(manifest),balance_issues=issues,leaf_instances=counts['leaves'],omitted_long_leaf_paths=long_leaves,mixed_node_atom_paths=mixed,limitations='Diagnostic tokenizer shares lexical assumptions with catalogue builder. Balanced text is not proof of complete SIMIS grammar, supported token semantics or telemetry availability. Mixed parent atoms need semantic review, not automatic new fields.')
(root/'config-coverage-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(dict(files=len(manifest),balance_issues=len(issues),long_leaf_paths=len(long_leaves),mixed_paths=len(mixed),long_keys=list(long_leaves),issue_examples=issues[:4])))
