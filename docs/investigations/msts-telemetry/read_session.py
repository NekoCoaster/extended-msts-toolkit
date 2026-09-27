"""Loaded activity header metadata read from proven singleton and header layout."""
import argparse,json,datetime
from pathlib import Path
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args();root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
try:
    base=0x809810
    d=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=r.sha,sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),activity_base=base,header_base=base+4,
           weather_raw=r.u(base+0x30),season_raw=r.u(base+0x34),start_time=list(r.unpack(base+0x38,'III')),duration=list(r.unpack(base+0x70,'II')),start_seconds=r.f(base+0x7c))
    for name in ['read_session.py','read_live.py']:(out/name).write_bytes((root/name).read_bytes())
    (out/'session.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
finally:K.CloseHandle(r.h)
