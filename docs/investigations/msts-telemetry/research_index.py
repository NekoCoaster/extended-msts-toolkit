"""Offline navigation over retained exports. Does not infer semantics or run MSTS.

Build in the canonical workspace; query also works in the published clone.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INDEX = ROOT / 'research-function-index.json'
ADDR = re.compile(r'(?<![0-9a-fA-F])(?:0x)?(00[4-7][0-9a-fA-F]{5})(?![0-9a-fA-F])')


def build():
    functions = {}
    files = sorted(p for p in ROOT.rglob('*.asm')
                   if re.fullmatch(r'[0-9a-fA-F]{8}', p.stem))
    for p in files:
        address = p.stem.lower()
        row = functions.setdefault(address, dict(exports=[], references=[], calls=[], thunk_targets=[]))
        b = p.read_bytes()
        row['exports'].append(dict(path=p.relative_to(ROOT).as_posix(),
                                   sha256=hashlib.sha256(b).hexdigest(),
                                   decompiled=p.with_suffix('.c').exists(),
                                   instruction_bytes=p.with_suffix('.bytes.tsv').exists()))
        lines = [line for line in b.decode('utf-8-sig').splitlines() if line.strip()]
        if len(lines) == 1:
            thunk = re.fullmatch(r'[0-9a-fA-F]{8}\s+JMP 0x([0-9a-fA-F]{8})', lines[0])
            if thunk and thunk[1].lower() not in row['thunk_targets']:
                row['thunk_targets'].append(thunk[1].lower())
        for line in lines:
            m = re.fullmatch(r'([0-9a-fA-F]{8})\s+CALL 0x([0-9a-fA-F]{8})', line)
            if m:
                edge = dict(site=m[1].lower(), target=m[2].lower())
                if edge not in row['calls']:
                    row['calls'].append(edge)
    docs = sorted(ROOT.glob('*FINDINGS.md'))
    for p in docs:
        for lineno, line in enumerate(p.read_text(encoding='utf-8-sig').splitlines(), 1):
            for address in sorted({m.lower() for m in ADDR.findall(line)}):
                if address in functions:
                    functions[address]['references'].append(dict(path=p.name, line=lineno))
    for address, row in functions.items():
        variants = {}
        for export in row['exports']:
            variants.setdefault(export['sha256'], []).append(export)
        row['assembly_variants'] = len(variants)
        # Byte-backed navigation is preferable; never call this the latest or verified version.
        row['navigation_export'] = sorted(row['exports'], key=lambda x: (
            not x['instruction_bytes'], not x['decompiled'], x['path']))[0]['path']
        row['callers'] = []
        row['callers_via_single_jump'] = []
    for address, row in functions.items():
        for edge in row['calls']:
            if edge['target'] in functions:
                functions[edge['target']]['callers'].append(dict(function=address, site=edge['site']))
                for target in functions[edge['target']]['thunk_targets']:
                    if target in functions:
                        functions[target]['callers_via_single_jump'].append(dict(function=address, site=edge['site'], thunk=edge['target']))
    data = dict(schema=1, scope='Retained named assembly exports, not whole-executable coverage',
                limitations='Calls are literal direct CALL targets; single-instruction JMP thunks have a separate one-hop caller index. Edges are the union of retained variants, not one asserted build. No indirect edges or execution proof. Variants are retained; navigation choice is not a freshness or correctness claim. Documentation references are lexical leads, not semantic assertions. Raw exports are local-only in the published clone.',
                counts=dict(functions=len(functions), exports=len(files), findings=len(docs),
                            variant_functions=sum(r['assembly_variants'] > 1 for r in functions.values())),
                functions=dict(sorted(functions.items())))
    if not files:
        raise SystemExit('No local exports: refusing to overwrite the index in a publication-only clone')
    INDEX.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(data['counts']))


def query(term, limit):
    data = json.loads(INDEX.read_text(encoding='utf-8'))
    address = term.lower().removeprefix('0x')
    if address in data['functions']:
        row = data['functions'][address]
        print(json.dumps(dict(address=address, navigation_export=row['navigation_export'],
                              assembly_variants=row['assembly_variants'], export_count=len(row['exports']),
                              references=row['references'][:limit], calls=row['calls'][:limit],
                              callers=row['callers'][:limit], thunk_targets=row['thunk_targets'],
                              callers_via_single_jump=row['callers_via_single_jump'][:limit],
                              limits='Lists capped by --limit; use the JSON for all variants and edges.'), indent=2))
    else:
        matches = []
        for address, row in data['functions'].items():
            refs = [r for r in row['references'] if term.lower() in r['path'].lower()]
            if refs:
                matches.append(dict(address=address, navigation_export=row['navigation_export'], reference=refs[0]))
        print(json.dumps(dict(matches=matches[:limit], total=len(matches)), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', nargs='?')
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--limit', type=int, default=12)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error('--limit must be positive')
    if args.build:
        build()
    elif args.query:
        query(args.query, args.limit)
    else:
        parser.error('Supply --build or an address/topic (e.g. 005a3941 or STATION)')
