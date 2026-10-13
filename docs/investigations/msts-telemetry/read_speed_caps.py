"""Read-only snapshot and independent finite-value reproduction of native 005a33af."""
import argparse, datetime, hashlib, json, math
from pathlib import Path
from read_services import ServiceReader, K

def capture(r):
    def scalar(address):
        return dict(address=address, bits=r.u(address), value=r.f(address))
    start=r.f(0x80acd4)
    route=r.u(0x809b48)
    globals_={name:scalar(addr) for name,addr in [('override',0x809878),('fallback',route+0x64),('flag20_cap',route+0x5c)]}
    rows=[]
    for service in r.registry()['entries']:
        if 'error' in service: raise ValueError(service['error'])
        s=service['address'];flags=service['flags_raw']
        fields={hex(off):scalar(s+off) for off in [0x220,0x224,0x228,0x22c]}
        if not all(math.isfinite(v['value']) for v in [*globals_.values(),*fields.values()]):
            raise ValueError('Non-finite input: native unordered comparison not modeled')
        source='override' if not globals_['override']['bits']&0x80000000 else 'fallback'
        selected=globals_[source]['value'];steps=[dict(source=source,value=selected)]
        candidates=[]
        if flags&0x20:candidates.append(('flag20_cap',globals_['flag20_cap']))
        if flags&0x10:candidates.append(('0x224',fields['0x224']))
        candidates.extend((key,fields[key]) for key in ['0x22c','0x228'])
        for key,v in candidates:
            eligible=key=='flag20_cap' or not v['bits']&0x80000000
            lowers=eligible and v['value']<selected
            steps.append(dict(source=key,value=v['value'],eligible=eligible,lowers=lowers))
            if lowers:selected=v['value'];source=key
        rows.append(dict(service_id=service['service_id'],address=s,is_player=service['is_player'],flags=flags,update_gate=r.u(s+0x144),fields=fields,reproduced=selected,limiting_source=source,matches=selected==fields['0x220']['value'],steps=steps))
    end=r.f(0x80acd4)
    return dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=start,sim_time_after=end,same_sim_time=start==end,paused=r.u(0x7be0f4),globals=globals_,services=rows)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
    try:
        result=capture(r)
        (out/'snapshot.json').write_text(json.dumps(result,indent=2,allow_nan=False))
        sources={}
        for name in ['read_speed_caps.py','read_services.py','read_live.py']:
            data=(root/name).read_bytes();(out/name).write_bytes(data);sources[name]=hashlib.sha256(data).hexdigest()
        (out/'metadata.json').write_text(json.dumps(dict(pid=a.pid,sha256=r.sha,access='QUERY_LIMITED_INFORMATION | VM_READ',sources=sources),indent=2))
        print(json.dumps(result,allow_nan=False))
    finally:K.CloseHandle(r.h)
