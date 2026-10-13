"""Read caller gates for the tested diesel monitor path; no writes."""
import argparse,json
from pathlib import Path
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);a=p.parse_args()
if Path(a.name).name!=a.name or a.name in ('.','..'):p.error('Invalid name')
r=Reader(a.pid);root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False)
try:
 train=r.u(0x7c2ac0);lead=r.u(train+0x6a);owner=r.u(train+0x72);kind=r.u(owner);controller=r.u(owner+8)
 if kind!=2:raise ValueError('Expected diesel controller kind2')
 values=dict(vigilance_global_790d88=r.u(0x790d88),aws_global_790d8c=r.u(0x790d8c),controller_1ec=r.u(controller+0x1ec),controller_180=r.u(controller+0x180))
 report=dict(pid=a.pid,sha256=r.sha,day=r.f(0x80acd4),paused=r.u(0x7be0f4),train=train,lead=lead,controller=controller,controller_kind=kind,values=values,context_stable=r.u(0x7c2ac0)==train and r.u(train+0x6a)==lead and r.u(train+0x72)==owner and r.u(owner+8)==controller,limitation='Post-run paused gates only;not a running trace of these gates. Global semantic names not established.')
 for n in ('read_monitor_caller_gates.py','read_live.py'):(out/n).write_bytes((root/n).read_bytes())
 (out/'gates.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
finally:K.CloseHandle(r.h)
