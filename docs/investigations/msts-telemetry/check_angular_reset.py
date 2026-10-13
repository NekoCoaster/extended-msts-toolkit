"""Read-only reset-vector check and archived angular-state counts."""
import argparse,hashlib,json
from pathlib import Path
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);a=p.parse_args()
root=Path(__file__).resolve().parent;r=Reader(a.pid)
try:
    out=dict(sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),reset_vector_address='0083db48',reset_vector=list(r.unpack(0x83db48,'fff')),captures={})
finally:K.CloseHandle(r.h)
for name in ('vehicle-motion-ai-01','vehicle-motion-restart-01'):
    path=root/'captures'/name/'samples.jsonl';groups={}
    for line in path.read_text(encoding='utf-8').splitlines():
        for t in json.loads(line).get('snapshot',{}).get('trains',[]):
            g=groups.setdefault(str(t['id']),dict(observations=0,nonzero_angular_momentum=0,nonzero_angular_velocity=0))
            for c in t['cars']:
                g['observations']+=1
                g['nonzero_angular_momentum']+=any(v!=0 for v in c['angular_momentum'])
                g['nonzero_angular_velocity']+=any(v!=0 for v in c['angular_velocity'])
    out['captures'][name]=dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(),trains=groups)
out['limitations']='Current live reset vector plus archived state counts,not an execution trace at each reset. All samples counted here,including paused and flagged unstable reads;finite-difference eligible subset is separate. No writes or native calls.'
dest=root/'angular-reset-provenance.json'
if dest.exists():raise FileExistsError('Preserve prior provenance;choose a new artifact before recapture')
dest.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out))
