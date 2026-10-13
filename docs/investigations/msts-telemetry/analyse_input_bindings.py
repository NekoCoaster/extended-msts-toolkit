"""Inventory native binding structure, not executed input commands."""
import collections,hashlib,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent;p=root/'captures/input-bindings-paused-01/input.json';d=json.loads(p.read_text())['snapshot']
keyboards=[x for x in d['devices'] if x.get('kind')==1];bindings=[b for k in keyboards for b in k['bindings']];listeners=[l for b in bindings for l in b['listeners']]
repo=Path('C:/codex/repo/NEMT');paths=['runtime/crawl_controls.h','runtime/editor_keyboard.h','docs/technical/physics.md','docs/technical/editors.md']
provenance=dict(repository=str(repo),commit=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip(),
    files={n:hashlib.sha256((repo/n).read_bytes()).hexdigest() for n in paths},
    status=subprocess.check_output(['git','-C',str(repo),'status','--porcelain','--',*paths],text=True))
out=dict(source=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),time=d['time'],paused=d['paused'],mode=d['mode'],
    device_kinds=[x.get('kind') for x in d['devices']],keyboards=[dict(count=k['count'],bitset_bytes=len(bytes.fromhex(k['bits'])),held_indices=k['held_indices'],stable_bits=k['stable_bits'],stable_device=k['stable_device']) for k in keyboards],
    retained_bindings=len(bindings),bindings_with_action=sum(bool(b['action']) for b in bindings),unique_actions=len({b['action'] for b in bindings if b['action']}),
    listener_references=len(listeners),unique_listeners=len({l['address'] for l in listeners}),unique_targets=len({l.get('target',l.get('callback')) for l in listeners}),callback_references=sum(bool(l['mask']&0x100) for l in listeners),destination_references=sum(not(l['mask']&0x100) for l in listeners),
    binding_reread_changes=sum(not b['stable_binding'] for b in bindings),action_reread_changes=sum(not b.get('stable_action',True) for b in bindings),listener_reread_changes=sum(not l['stable'] for l in listeners),
    stable_list=d['stable_list'],provenance=provenance,limitations='Paused zero-held snapshot does not validate key presses/releases or dispatch. Native layout reused from pinned NEMT source; helper bytes match current image. Counts can include several references to the same action/listener. No UI input or global OS keyboard read.')
(root/'input-bindings-summary.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='provenance'},indent=2))
