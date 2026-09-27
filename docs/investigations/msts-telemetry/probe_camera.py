"""Bounded read-only camera snapshot; no UI actions or native function calls."""
import argparse,json,shutil,datetime,math
from pathlib import Path
from read_live import Reader,K

def capture(r):
    start=r.f(0x80acd4); view=r.u(0x7c2a88); render=r.u(0x829224)
    result={'simulation_time_start':start,'view_pointer':view,'render_pointer':render}
    if view:
        mode=r.u(view+0x11c); tracking=r.u(view+0x110)
        result.update(mode_raw=mode,tracking_raw=tracking,debug_tracking_label=('TRACKING ON' if tracking else 'TRACKING OFF') if mode in (1,2,3) else 'NOT TRACKING')
    if render:
        basis=[list(r.unpack(render+off,'3f')) for off in (0xc,0x18,0x24)]
        position=list(r.unpack(render+0x30,'3f'))
        result.update(render_basis=basis,render_position=position,basis_norms=[math.sqrt(sum(v*v for v in row)) for row in basis],basis_pair_dots=[sum(a*b for a,b in zip(basis[i],basis[j])) for i,j in ((0,1),(0,2),(1,2))])
    result.update(pointers_stable=view==r.u(0x7c2a88) and render==r.u(0x829224),simulation_time_end=r.f(0x80acd4),pause_raw=r.u(0x7be0f4))
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--pid',type=int,required=True);a.add_argument('--name',required=True);args=a.parse_args()
    if Path(args.name).name!=args.name:raise ValueError('Capture name must be one path component')
    out=Path(__file__).resolve().parent/'captures'/args.name;out.mkdir(exist_ok=False)
    r=Reader(args.pid)
    try:
        payload={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':args.pid,'image_sha256':r.sha,'snapshot':capture(r)}
        (out/'camera.json').write_text(json.dumps(payload,indent=2)+'\n');shutil.copy2(__file__,out/'probe_camera.py');print(json.dumps(payload))
    finally:K.CloseHandle(r.h)
