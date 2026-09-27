"""Read-only bounded per-receiver stream states. Does not query/call audio APIs."""
import argparse, datetime, hashlib, json, shutil, struct
from pathlib import Path
from read_live import Reader, K
from read_event_receivers import capture as receivers

def capture(r):
    context = receivers(r)
    rows = []
    for owner in context['receivers']:
        obj, definition = owner['object'], owner['definition']
        states = owner['stream_state']
        definitions = r.u(definition + 0x14)
        for index in range(owner['stream_count']):
            row = dict(receiver=obj, handle=owner['handle'], label=owner.get('definition_label'),
                       associations=owner['car_associations'], index=index)
            rows.append(row)
            try:
                state_address = states + index * 0x1c
                config_address = definitions + index * 0x20
                state = r.read(state_address, 0x1c)
                config = r.read(config_address, 0x20)
                backend, queue = struct.unpack_from('<II', state)
                row.update(state_address=state_address, definition_address=config_address,
                           state_raw=state.hex(), definition_raw=config.hex(), backend=backend,
                           queue_head=queue, cached_scalars=list(struct.unpack_from('<ff',state,8)),
                           trigger_enable_words=list(struct.unpack_from('<II',state,0x10)),
                           volume_factor=struct.unpack_from('<f',state,0x18)[0],
                           trigger_count=struct.unpack_from('<I',config)[0])
                nodes=[]; seen=set(); node=queue
                row['queue_nodes']=nodes
                while node:
                    if node in seen:
                        row['queue_traversal_stop']=dict(reason='cycle',address=node);break
                    if len(seen)>=256:
                        row['queue_traversal_stop']=dict(reason='research_bound',address=node);break
                    seen.add(node)
                    raw=r.read(node,12); nxt=struct.unpack_from('<I',raw,8)[0]
                    nodes.append(dict(address=node,next=nxt,raw=raw.hex()));node=nxt
                row['queue_complete']=node==0
                if backend:
                    raw=r.read(backend,0x98)
                    row.update(backend_raw=raw.hex(),backend_flags=struct.unpack_from('<I',raw,4)[0],
                               native_bit2_predicate=bool(struct.unpack_from('<I',raw,4)[0]&2),
                               buffer_interface=struct.unpack_from('<I',raw,0x30)[0],
                               spatial_interface=struct.unpack_from('<I',raw,0x74)[0],
                               lock_before=struct.unpack_from('<I',raw,0x78)[0],
                               lock_after=r.u(backend+0x78))
                else:
                    row['native_bit2_predicate']=False
                row['stable_state']=r.read(state_address,0x1c)==state
                row['stable_definition']=r.read(config_address,0x20)==config
                row['stable_queue_links']=all(r.u(n['address']+8)==n['next'] for n in nodes)
                row['stable_owner']=r.u(obj+0x10)==definition and r.u(obj+0x14)==states and r.u(definition+0x14)==definitions and r.u(definition+0x10)==owner['stream_count']
            except (OSError,ValueError) as error:
                row['error']=str(error)
    return dict(context=context,streams=rows,time_after=r.f(0x80acd4),paused_after=r.u(0x7be0f4),
                limitations='Sequential read-only snapshot, not atomic; lock observations do not acquire a lock or exclude ABA. Native bit2 predicate is not proof of audibility. Queue nodes preserve unknown payloads without interpretation. No audio API calls.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Invalid name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False)
    r=Reader(a.pid)
    try:
        result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),image_sha256=r.sha,snapshot=capture(r))
        (out/'streams.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        hashes={}
        for name in ['read_audio_streams.py','read_event_receivers.py','read_live.py']:
            shutil.copy2(root/name,out/name);hashes[name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
        (out/'probe-hashes.json').write_text(json.dumps(hashes,indent=2))
        s=result['snapshot'];rows=s['streams']
        print(json.dumps(dict(time=s['context']['time'],time_after=s['time_after'],paused=s['paused_after'],receivers=len(s['context']['receivers']),streams=len(rows),errors=sum('error' in x for x in rows),queue_nodes=sum(len(x.get('queue_nodes',[])) for x in rows),native_bit2=sum(x.get('native_bit2_predicate',False) for x in rows))))
    finally:K.CloseHandle(r.h)
