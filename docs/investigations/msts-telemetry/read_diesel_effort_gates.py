"""Read diesel effort gate inputs without claiming a derived output force."""
import argparse,hashlib,json,struct
from pathlib import Path
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args();root=Path(__file__).resolve().parent
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
 t=r.u(0x7c2ac0);lead=r.u(t+0x6a);driver=r.u(t+0x72);ctl=r.u(driver+8);ed=r.u(lead+0x29a)
 if r.u(driver)!=2 or r.u(lead+0x98)!=t:raise ValueError('Not matched player diesel')
 fields={'engine_flags296':(lead+0x296,'I'),'throttle':(ctl+0x8c,'f'),'reverser':(ctl+0xc8,'f'),'controller370':(ctl+0x370,'I'),'traction_current':(lead+0x2c2,'f'),'effort_cache496':(lead+0x496,'f'),'brake_cylinder':(lead+0x230,'f'),'engine_type14a':(ed+0x14a,'I'),'force_scale102':(ed+0x102,'f'),'current_scale1da':(ed+0x1da,'f'),'brake_cutoff63c':(ed+0x63c,'f'),'brake_cutoff_threshold640':(ed+0x640,'f'),'emergency_action':(lead+0x53e,'I'),'emergency_definition':(lead+0x576,'I')}
 raw={k:r.read(addr,4) for k,(addr,typ) in fields.items()};values={k:struct.unpack('<'+fields[k][1],b)[0] for k,b in raw.items()};md=values['emergency_definition']
 if md!=ed+0xbe4:raise ValueError('Unexpected emergency definition')
 cut=r.u(md+0x20);report=dict(pid=a.pid,sha256=r.sha,day=r.f(0x80acd4),paused=r.u(0x7be0f4),train=t,lead=lead,controller=ctl,definition=ed,values=values,emergency_applies_cuts_power=cut,cut_gate_conjunction=bool(values['emergency_action'] and cut and values['controller370']),fields_stable=all(r.read(fields[k][0],4)==b for k,b in raw.items()),identity_stable=r.u(t+0x6a)==lead and r.u(t+0x72)==driver and r.u(driver+8)==ctl and r.u(lead+0x29a)==ed,sources={},limitation='Stored inputs at reported pause state;conjunction reflects one traced branch,not invocation or earlier rollback cause. Sequential reads are not atomic;do not project observations backward.')
 for n in ['read_diesel_effort_gates.py','read_live.py']:
  b=(root/n).read_bytes();(out/n).write_bytes(b);report['sources'][n]=hashlib.sha256(b).hexdigest()
 (out/'gates.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
finally:K.CloseHandle(r.h)
