"""Bounded type2 pending child rings, rooted at the wrapper's +4 field."""
import argparse,copy,datetime,hashlib,json,shutil,struct
from pathlib import Path
from read_live import Reader,K
from read_audio_streams import capture
from read_audio_pending import enrich

def expand(r,snapshot):
    expanded=copy.deepcopy(snapshot);groups=[]
    for stream in expanded['streams']:
        children=[]
        for node in list(stream.get('queue_nodes',[])):
            raw=bytes.fromhex(node['raw'])
            if raw[0]!=2:continue
            wrapper=node['address'];pointer=struct.unpack_from('<I',raw,4)[0]
            group=dict(receiver=stream['receiver'],stream_index=stream['index'],label=stream['label'],
                       associations=stream['associations'],wrapper=wrapper,first_child=pointer,children=[])
            groups.append(group);seen=set()
            try:
                if r.read(wrapper,12)!=raw:raise ValueError('Wrapper changed before traversal')
                while pointer!=wrapper:
                    if not pointer:raise ValueError('Unexpected null before wrapper return')
                    if pointer in seen:raise ValueError('Child cycle not returning to wrapper')
                    if len(seen)>=128:raise ValueError('Child research bound')
                    seen.add(pointer);child=r.read(pointer,12)
                    if child[0]!=1:raise ValueError('Unexpected nested record type')
                    nxt=struct.unpack_from('<I',child,8)[0]
                    entry=dict(address=pointer,next=nxt,raw=child.hex())
                    group['children'].append(entry);children.append(entry);pointer=nxt
                group['returned_to_wrapper']=True
                group['stable_wrapper']=r.read(wrapper,12)==raw
                group['stable_children']=all(r.read(n['address'],12)==bytes.fromhex(n['raw']) for n in group['children'])
            except (OSError,ValueError) as error:
                group['error']=str(error)
        stream.setdefault('queue_nodes',[]).extend(children)
    return groups,enrich(r,expanded)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Invalid name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        snapshot=capture(r);groups,pending=expand(r,snapshot)
        pending['limitation']='Includes bounded type2 child rings returning to their wrapper. Top-level chain may remain incomplete. Node/sample identities are not current playback or proof of audibility.'
        result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),image_sha256=r.sha,snapshot=snapshot,
                    nested_groups=groups,pending=pending,time_after=r.f(0x80acd4),paused_after=r.u(0x7be0f4))
        (out/'nested.json').write_text(json.dumps(result,indent=2),encoding='utf-8');hashes={}
        for name in ['read_audio_nested.py','read_audio_pending.py','read_audio_streams.py','read_event_receivers.py','read_live.py']:
            shutil.copy2(root/name,out/name);hashes[name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
        (out/'probe-hashes.json').write_text(json.dumps(hashes,indent=2))
        print(json.dumps(dict(time=result['time_after'],paused=result['paused_after'],groups=len(groups),children=sum(len(g['children']) for g in groups),group_errors=sum('error' in g for g in groups),samples=len(pending['samples']))))
    finally:K.CloseHandle(r.h)
