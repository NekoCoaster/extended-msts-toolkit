"""Bounded read-only wheel/animation research snapshot; no native calls or writes."""
import argparse
import datetime
import hashlib
import json
import math
import struct
from pathlib import Path
from read_physical_registry import PhysicalRegistryReader
from read_live import K


def finite(r, address):
    value = r.f(address)
    if not math.isfinite(value):
        raise ValueError(f'Nonfinite scalar at {address:#x}')
    return value


def shape_state(r, shape):
    if not shape:
        return dict(available=False, reason='shape_null')
    kind = r.unpack(shape+8, 'H')[0]
    table = r.u(shape)
    if kind != 5 or table != 0x828be0:
        return dict(available=False, reason='unsupported_shape', address=shape, kind=kind, table=table)
    if r.u(table+0x2c) != 0x6a5fd0:
        return dict(available=False, reason='setter_changed', address=shape)
    descriptor = r.u(shape+0x8c)
    if not descriptor:
        return dict(available=False, reason='descriptor_null', address=shape)
    raw = r.read(shape+0x90,8)
    previous,current = struct.unpack('<ff',raw)
    if not all(math.isfinite(x) for x in (previous,current)):
        raise ValueError('Nonfinite animation time')
    return dict(available=True,address=shape,descriptor=descriptor,
                current_animation_seconds=current,processed_animation_seconds=previous,
                equal_at_read=current==previous,raw_times=raw.hex(),
                raw_times_after=r.read(shape+0x90,8).hex(),
                identity_stable=(r.u(shape)==table and r.unpack(shape+8,'H')[0]==kind
                                 and r.u(shape+0x8c)==descriptor and r.u(table+0x2c)==0x6a5fd0))


def vehicle_state(r, obj):
    car = obj['address']
    definition = obj['physics']['definition']
    engine = obj['native_kind']==0x4000e and obj['physics']['powered']
    identity = (r.u(car+0x50),r.u(car+0x98),r.u(car+0x94),r.u(car+4))
    expected = (obj['object_id'],obj['owner'],definition,obj['table_index'])
    if identity!=expected or not obj['stable'] or not obj['reciprocal_list_links']:
        raise ValueError('Vehicle identity changed before wheel read')
    shape = r.u(car+0x10)
    row = dict(address=car,object_id=identity[0],owner=identity[1],native_kind=obj['native_kind'],
               ordinary_wheel_rate=finite(r,car+0x1b0),wheel_radius=finite(r,definition+0x448),
               driver=None,shape=shape_state(r,shape))
    if engine:
        ed = r.u(car+0x29a)
        if not ed:
            raise ValueError('Engine definition unavailable')
        row['driver']=dict(definition=ed,rotation_rate=finite(r,car+0x2b2),
                           adhesion_force_limit=finite(r,car+0x2aa),phase=finite(r,car+0x1dc),
                           wheel_radius=finite(r,ed+0x112),num_wheels=r.unpack(ed+0x11a,'i')[0],
                           definition_stable=r.u(car+0x29a)==ed)
    row['identity_stable']=(identity==(r.u(car+0x50),r.u(car+0x98),r.u(car+0x94),r.u(car+4))
                            and r.u(car+0x10)==shape)
    return row


def sample(r):
    manager = r.u(0x7bdecc)
    if not manager:
        return dict(available=False,reason='manager_null',vehicles=None)
    registry = r.physical_registry()
    if registry['manager']!=manager or not registry['roots_stable']:
        return dict(available=False,reason='registry_changed',vehicles=None)
    owners={t['address']:dict(train_id=t['id'],is_player=t['is_player']) for t in registry['trains']}
    rows=[]
    for obj in registry['objects']:
        if obj['native_kind'] not in (0x4000d,0x4000e):
            continue
        try:
            row=vehicle_state(r,obj)
            row['train']=owners.get(obj['owner'])
        except (OSError,ValueError) as error:
            row=dict(address=obj['address'],object_id=obj.get('object_id'),error=str(error))
        rows.append(row)
    return dict(available=True,manager=manager,vehicles=rows,
                manager_stable=r.u(0x7bdecc)==manager,stored_count=registry['stored_count'],
                limitation='Sequential reads,not atomic. Stable identity/equal clocks do not prove field freshness,visibility or physical wheel angle. Train linkage is optional;no complete detached/static coverage claim.')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--pid',type=int,required=True)
    p.add_argument('--name',required=True)
    a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid capture name')
    root=Path(__file__).resolve().parent
    out=root/'captures'/a.name
    out.mkdir(exist_ok=False)
    r=PhysicalRegistryReader(a.pid)
    try:
        data=dict(pid=a.pid,sha256=r.sha,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4))
        try:
            data['sample']=sample(r)
        except (OSError,ValueError) as error:
            data['sample']=dict(available=False,reason='read_error',error=str(error),vehicles=None)
        data['sim_time_after']=r.f(0x80acd4)
        data['sources']={}
        for name in ('read_live.py','read_physical_registry.py','read_wheel_animation.py'):
            raw=(root/name).read_bytes()
            (out/name).write_bytes(raw)
            data['sources'][name]=hashlib.sha256(raw).hexdigest()
        (out/'wheel-animation.json').write_text(json.dumps(data,indent=2,allow_nan=False))
        print(json.dumps(dict(output=str(out),available=data['sample']['available'],
                              count=len(data['sample']['vehicles'] or []),reason=data['sample'].get('reason'))))
    finally:
        K.CloseHandle(r.h)
