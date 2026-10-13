"""Resolve type1 pending audio records only; other payload types remain opaque."""
import argparse,datetime,hashlib,json,shutil,struct
from pathlib import Path
from read_live import Reader,K
from read_audio_streams import capture

def string(r,address):
    raw=bytearray()
    for i in range(1024):
        unit=r.read(address+i*2,2)
        if unit==b'\0\0':return raw.decode('utf-16le')
        raw.extend(unit)
    raise ValueError('UTF16 research bound')

def enrich(r,snapshot):
    samples={};nodes=[]
    for stream in snapshot['streams']:
        for node in stream.get('queue_nodes',[]):
            raw=bytes.fromhex(node['raw']);kind,b1,b2,b3,ref,nxt=struct.unpack('<BBBBII',raw)
            row=dict(receiver=stream['receiver'],stream_index=stream['index'],address=node['address'],
                     kind=kind,byte1=b1,byte2=b2,byte3=b3,payload=ref,next=nxt)
            nodes.append(row)
            try:
                row['stable_node']=r.read(node['address'],12)==raw
                if kind!=1 or not row['stable_node']:continue
                if ref in samples:continue
                item=dict(address=ref);samples[ref]=item
                head=r.read(ref,0x18);path_pair=struct.unpack_from('<I',head,8)[0]
                pair=r.read(path_pair,8);directory,name=struct.unpack('<II',pair)
                item.update(raw=head.hex(),reference_count=struct.unpack_from('<I',head,4)[0],
                            path_pair=path_pair,directory=string(r,directory),name=string(r,name),
                            retained_parameter=struct.unpack_from('<I',head,0xc)[0],
                            loaded_resource=struct.unpack_from('<I',head,0x14)[0],
                            stable_header=r.read(ref,0x18)==head,stable_pair=r.read(path_pair,8)==pair)
            except (OSError,ValueError,UnicodeError) as error:
                row['error']=str(error)
    return dict(nodes=nodes,samples=list(samples.values()),
        limitation='Only type1 payloads decoded. Type2 nested structure not traversed. Prior bounded snapshot may omit nodes. Loaded path labels are not independently verified filesystem identities or current playback. No file opened using process strings.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Invalid capture name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        s=capture(r);pending=enrich(r,s)
        result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),image_sha256=r.sha,
                    snapshot=s,pending=pending,time_after=r.f(0x80acd4),paused_after=r.u(0x7be0f4))
        (out/'pending.json').write_text(json.dumps(result,indent=2),encoding='utf-8');hashes={}
        for name in ['read_audio_pending.py','read_audio_streams.py','read_event_receivers.py','read_live.py']:
            shutil.copy2(root/name,out/name);hashes[name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
        (out/'probe-hashes.json').write_text(json.dumps(hashes,indent=2))
        print(json.dumps(dict(time=result['time_after'],paused=result['paused_after'],nodes=len(pending['nodes']),sample_objects=len(pending['samples']),errors=sum('error' in x for x in pending['nodes']))))
    finally:K.CloseHandle(r.h)
