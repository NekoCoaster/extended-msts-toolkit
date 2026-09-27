"""Bounded reconstruction of the native LINE_VOLTAGE display gate; no native calls."""
import argparse,json,math,struct,shutil
from pathlib import Path
from read_live import Reader,K

def capture(r):
    t=r.f(0x80acd4)
    if r.u(0x7b6438)!=3:raise ValueError('Electric player required')
    train=r.u(0x7c2ac0);lead=r.u(train+0x6a);wrapper=r.u(train+0x72);controller=r.u(wrapper+8)
    enabled=r.u(controller+0x258);route=r.u(0x7b8d3c);voltage=r.f(route+0x58)
    car=lead;seen=set();rows=[];passed=False
    epsilon=r.f(0x40bb2e)
    if enabled:
        while car:
            if car in seen or len(seen)>=256:raise ValueError('Cycle or traversal cap; result unavailable')
            seen.add(car);flags80=r.read(car+0x80,1)[0];flags84=r.u(car+0x84)
            row=dict(car=car,flags80=flags80,flags84=flags84,qualifies=False)
            if flags80 & 0xc and flags84 & 0x80080:
                obj=r.u(car+0x10);value=r.u(obj+0x8c);row.update(object=obj,tagged_value=value)
                if value & 0x20000000:row.update(qualifies=True,reason='tag bit')
                else:
                    raw=r.f(value+4);low=r.f(car+0x1cc);high=r.f(car+0x1d0)
                    extended=raw-epsilon;rounded=struct.unpack('<f',struct.pack('<f',extended))[0]
                    passed_compare=math.isnan(extended) or math.isnan(low) or extended<low or math.isnan(high) or rounded<high
                    row.update(raw=raw,adjusted=extended,adjusted_float32=rounded,bound_1cc=low,bound_1d0=high,qualifies=passed_compare,reason='native less-than/unordered tests')
            rows.append(row)
            if row['qualifies']:passed=True;break
            car=r.u(car+0xa8)
    stable=r.u(0x7b6438)==3 and r.u(0x7c2ac0)==train and r.u(train+0x6a)==lead and r.u(wrapper+8)==controller
    return dict(time=t,time_after=r.f(0x80acd4),paused=r.u(0x7be0f4),train=train,lead=lead,controller=controller,stable=stable,gate_enabled=enabled,route_voltage=voltage,pantograph_control=r.u(controller+0x264),gate_passed=passed if enabled else None,derived_display_voltage=voltage if not enabled or passed else 0,car_checks=rows,limitations='Reconstructed display rule, not direct cab object value or physics power. External reads are non-atomic; near-boundary x87 precision may differ. No native calls.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Invalid name')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        d=dict(image_sha256=r.sha,snapshot=capture(r));(out/'voltage.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
        for n in ('read_electric_voltage.py','read_live.py'):shutil.copy2(root/n,out/n)
        print(json.dumps(d))
    finally:K.CloseHandle(r.h)
