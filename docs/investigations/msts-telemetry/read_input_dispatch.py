"""Read native dispatch context and device method identities; never call them."""
import argparse,datetime,hashlib,json,shutil,struct
from pathlib import Path
from read_live import Reader,K
from read_input_bindings import capture

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Invalid name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        snapshot=capture(r);devices=[]
        for d in snapshot['devices']:
            obj=d['input_object'];vtable=r.u(obj)
            item=dict(kind=d.get('kind'),input=obj,vtable=vtable,update_method=r.u(vtable+8),next_event_method=r.u(vtable+0xc),stable_vtable=r.u(obj)==vtable)
            devices.append(item)
            if d.get('kind')==1:
                header=r.read(obj+0xc,16);buffer,capacity,cursor,count=struct.unpack('<4I',header)
                if not 0<=cursor<=count<=capacity<=4096:raise ValueError('Input buffer count/cursor research bound')
                item.update(buffer=buffer,capacity=capacity,cursor=cursor,count=count,events=[])
                if count:
                    data=r.read(buffer,count*16)
                    item['events']=[dict(index=i,words=list(struct.unpack_from('<4I',data,i*16))) for i in range(count)]
                item['stable_buffer_header']=r.read(obj+0xc,16)==header
        raw=r.read(0x6bae0e,6);patch=dict(address=0x6bae0e,bytes=raw.hex())
        if raw[0]==0xe9:
            target=(0x6bae0e+5+struct.unpack_from('<i',raw,1)[0])&0xffffffff
            code=r.read(target,64);patch.update(target=target,target_first64=code.hex(),target_sha256=hashlib.sha256(code).hexdigest())
        actions={}
        for d in snapshot['devices']:
            for b in d.get('bindings',[]):
                if not b['action']:continue
                ar=bytes.fromhex(b['action_raw'])
                actions[b['action']]=dict(address=b['action'],event_value=struct.unpack_from('<I',ar,0xc)[0],
                    filter_word=struct.unpack_from('<H',ar,0x10)[0],state_flags=struct.unpack_from('<H',ar,0x12)[0])
                for listener in b['listeners']:
                    listener['target_kind']='callback' if listener['mask']&0x100 else 'value_destination'
        globals={hex(addr):r.u(addr) for addr in [0x829980,0x829990,0x8299ac,0x8299cc]}
        result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),image_sha256=r.sha,snapshot=snapshot,device_methods=devices,
                    actions=list(actions.values()),dispatch_globals=globals,live_entry_patch=patch,
                    limitations='Read-only method/patch identities. Target code fingerprint is not a semantic audit. Existing live detour prevents claiming complete native dispatch equivalence. No callbacks or destination pointers invoked/written.')
        (out/'dispatch.json').write_text(json.dumps(result,indent=2));hashes={}
        for name in ['read_input_dispatch.py','read_input_bindings.py','read_live.py']:
            shutil.copy2(root/name,out/name);hashes[name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
        (out/'probe-hashes.json').write_text(json.dumps(hashes,indent=2))
        print(json.dumps(dict(device_methods=devices,actions=result['actions'],globals=globals,entry_patch=patch)))
    finally:K.CloseHandle(r.h)
