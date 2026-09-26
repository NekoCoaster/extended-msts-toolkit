"""Bounded read-only car motion/evaluation inputs; no native invocation."""
import argparse,json,math,shutil,struct
from pathlib import Path
from read_live import Reader,K

def capture(r):
    start=r.f(0x80acd4);reference=r.u(0x80aa1c);definition=r.u(reference+0x94)
    ceiling=r.f(definition+0x7cc);scale=r.f(definition+0x7d0)
    negative=r.f(0x770564);positive=r.f(0x753e38)
    def sign(x):return -1 if x<negative else (1 if x>positive else 0)
    trains=r.trains()
    for train in trains:
        service=train['service_object'];service_definition=r.u(service+0x18) if service else 0
        train['service_definition']=service_definition
        train['service_definition_a0']=r.f(service_definition+0xa0) if service_definition else None
        for car in train['cars']:
            a=car['address'];b=car['body'];d=car['definition']
            force=list(r.unpack(b+0xa0,'fff'));acceleration=r.f(a+0x1c0);velocity=r.f(a+0x1bc)
            threshold=abs(acceleration)*scale if abs(acceleration)<=ceiling else 1.0
            threshold=struct.unpack('<f',struct.pack('<f',threshold))[0]
            eligibility=r.read(d+0x88,1)[0];passenger_value=r.f(d+0xc08);durability=r.f(a+0x28e)
            car.update(stored_velocity=velocity,stored_acceleration=acceleration,comparison_value=durability,
                definition_kind=eligibility,passenger_value_c08=passenger_value,force_vector=force,
                rebuilt_signed_acceleration=math.sqrt(sum(x*x for x in force))*car['inverse_mass']*sign(sum(x*y for x,y in zip(force,car['forward']))),
                rebuilt_signed_velocity=math.sqrt(sum(x*x for x in car['velocity']))*sign(sum(x*y for x,y in zip(car['velocity'],car['forward']))),
                evaluation_threshold=threshold,evaluation_kind='freight' if eligibility==2 else ('passenger' if eligibility==3 or passenger_value>0 else None),
                comparison_true=durability<threshold,car_flags84=r.u(a+0x84),body_pointer_stable_after=r.u(a+0x5c)==b)
    return dict(sim_time=start,reference_car=reference,reference_definition=definition,ceiling=ceiling,scale=scale,
                sign_negative=negative,sign_positive=positive,trains=trains,sim_time_after=r.f(0x80acd4),paused=r.u(0x7be0f4))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args()
    if Path(a.name).name!=a.name:raise ValueError('Name must be one component')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        d=dict(image_sha256=r.sha,snapshot=capture(r));(out/'snapshot.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
        for n in ('probe_vehicle_evaluation.py','read_live.py'):shutil.copy2(root/n,out/n)
        s=d['snapshot'];print(json.dumps({k:v for k,v in s.items() if k!='trains'}|{'trains':[{k:v for k,v in t.items() if k!='cars'}|{'cars':len(t['cars']),'acceleration_range':[min(c['stored_acceleration'] for c in t['cars']),max(c['stored_acceleration'] for c in t['cars'])],'comparison_values':sorted(set(c['comparison_value'] for c in t['cars'])),'qualifying':sum(c['comparison_true'] and c['evaluation_kind'] is not None for c in t['cars'])} for t in s['trains']]}))
    finally:K.CloseHandle(r.h)
