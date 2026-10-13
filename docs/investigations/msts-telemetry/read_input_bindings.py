"""Bounded native input list and keyboard binding snapshot; never polls OS keys."""
import argparse,datetime,hashlib,json,shutil,struct
from pathlib import Path
from read_live import Reader,K

def capture(r):
    root=r.u(0x8299a0);first=r.u(root);node=first;seen=set();devices=[];links=[]
    mode=r.u(0x829980);time=r.f(0x80acd4)
    while node!=root:
        if not node or node in seen or len(seen)>=32:raise ValueError('Device list cycle/bound')
        seen.add(node);nxt,prev,address=r.unpack(node,'III');links.append((node,nxt,address))
        raw=r.read(address,28);v=struct.unpack('<7I',raw);input_object=v[1]
        row=dict(address=address,node=node,raw=raw.hex(),input_object=input_object,key_offset=v[4],table_end=v[5],table=v[6]);devices.append(row)
        node=nxt
        if not input_object:continue
        row['kind']=r.read(input_object+0x2d,1)[0]
        if row['kind']!=1:continue
        count=v[5]-v[4]
        if not 0<count<=256 or v[5]>65535:raise ValueError('Keyboard count research bound')
        bits_address=r.u(input_object+0x24);bits=r.read(bits_address,(count+7)//8)
        row.update(count=count,bits_address=bits_address,bits=bits.hex(),held_indices=[i for i in range(count) if bits[i//8]&(1<<(i%8))],bindings=[])
        budget=4096
        for index in range(count):
            binding=v[6]+(v[4]+index)*16;visited=set()
            while binding:
                if binding in visited or budget<=0:raise ValueError('Binding cycle/bound')
                visited.add(binding);budget-=1
                b=r.read(binding,16);action,link,mods,flags=struct.unpack('<4I',b)
                entry=dict(index=index,address=binding,raw=b.hex(),action=action,next=link,modifier_word=mods,flags=flags,listeners=[])
                if action:
                    ar=r.read(action,24);av=struct.unpack('<6I',ar);entry['action_raw']=ar.hex();entry['action_flags']=av[4]
                    handler=av[1];handlers=set()
                    while handler:
                        if handler in handlers or budget<=0:raise ValueError('Listener cycle/bound')
                        handlers.add(handler);budget-=1;hr=r.read(handler,20);hv=struct.unpack('<5I',hr)
                        entry['listeners'].append(dict(address=handler,target=hv[0],target_kind='callback' if hv[3]&0x100 else 'value_destination',context=hv[1],next=hv[2],mask=hv[3],flags=hv[4],raw=hr.hex(),stable=r.read(handler,20)==hr));handler=hv[2]
                    entry['stable_action']=r.read(action,24)==ar
                entry['stable_binding']=r.read(binding,16)==b
                if action or link or mods or flags:row['bindings'].append(entry)
                binding=link
        row['stable_bits']=r.read(bits_address,len(bits))==bits
        row['stable_device']=r.read(address,28)==raw and r.u(input_object+0x24)==bits_address
    return dict(time=time,time_after=r.f(0x80acd4),paused=r.u(0x7be0f4),mode=mode,mode_after=r.u(0x829980),root=root,devices=devices,
                stable_list=r.u(0x8299a0)==root and r.u(root)==first and all(r.u(n)==nxt and r.u(n+8)==obj for n,nxt,obj in links),
                limitations='Read-only current native input state, not OS-wide key capture or an input-event log. Non-atomic; stable rereads do not exclude ABA. Nonkeyboard devices retain header only. Mode/flags and callback contexts do not establish command execution.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Invalid name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),image_sha256=r.sha,snapshot=capture(r))
        (out/'input.json').write_text(json.dumps(result,indent=2));hashes={}
        for name in ['read_input_bindings.py','read_live.py']:
            shutil.copy2(root/name,out/name);hashes[name]=hashlib.sha256((out/name).read_bytes()).hexdigest()
        (out/'probe-hashes.json').write_text(json.dumps(hashes,indent=2))
        s=result['snapshot'];print(json.dumps(dict(time=s['time'],paused=s['paused'],mode=s['mode'],devices=len(s['devices']),keyboards=[dict(count=x['count'],held=x['held_indices'],bindings=len(x['bindings'])) for x in s['devices'] if x.get('kind')==1],stable_list=s['stable_list'])))
    finally:K.CloseHandle(r.h)
