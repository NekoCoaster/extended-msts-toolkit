"""Bounded passive sky vertex/shader series; no native calls or process writes."""
import argparse,datetime,hashlib,json,math,struct,time
from pathlib import Path
from read_live import Reader,K

def sample(r):
    row=dict(monotonic=time.perf_counter(),sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),delta=r.f(0x828fb4),objects=[])
    env=r.u(0x7b6d60);sky=r.u(env)
    lc,la=r.u(sky),r.u(sky+8);sc,sa=r.u(sky+0x180),r.u(sky+0x184)
    if lc>32 or sc>32:raise ValueError('Sky array bounds')
    for kind,count,base,stride,shader_offset,draw_offset in [('layer',lc,la,0x1ac,0x24,0x190),('satellite',sc,sa,0x1cd,0x45,0x1b1)]:
        for i in range(count):
            address=base+i*stride;shader=address+shader_offset;draw=address+draw_offset
            header=r.read(draw+4,8);n,vertices=struct.unpack('<II',header)
            if n>4096:raise ValueError('Vertex bound')
            raw=r.read(vertices,n*40) if n else b''
            sh=r.read(shader,20);frames,duration,clock,index,fp=struct.unpack('<IffII',sh)
            if frames>256:raise ValueError('Shader frame count bound')
            frame_available=bool(frames and index<frames)
            frame_raw=r.read(fp+index*32,32).hex() if frame_available else None
            row['objects'].append(dict(kind=kind,index=i,address=address,vertex_count=n,vertex_pointer=vertices,
                shader_header=sh.hex(),frame_raw=frame_raw,frame_available=frame_available,frames=frames,frame_duration=duration,clock_raw=clock,selected_frame=index,
                vertices=[dict(index=j,position=list(struct.unpack_from('<fff',raw,j*40)),diffuse=struct.unpack_from('<I',raw,j*40+24)[0],
                               secondary=struct.unpack_from('<I',raw,j*40+28)[0],uv=list(struct.unpack_from('<ff',raw,j*40+32))) for j in range(n)],
                header_stable=header==r.read(draw+4,8),shader_stable=sh==r.read(shader,20)))
    row.update(environment=env,sky=sky,structure_stable=env==r.u(0x7b6d60) and sky==r.u(env) and (lc,la,sc,sa)==(r.u(sky),r.u(sky+8),r.u(sky+0x180),r.u(sky+0x184)),
               sim_time_after=r.f(0x80acd4),paused_after=r.u(0x7be0f4),monotonic_after=time.perf_counter())
    return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=30);p.add_argument('--interval',type=float,default=.5);a=p.parse_args()
    if Path(a.name).name!=a.name or a.name in ('.','..') or not all(math.isfinite(x) for x in (a.seconds,a.interval)) or not 0<=a.seconds<=120 or not .1<=a.interval<=5:p.error('Invalid bounds')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=Reader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),seconds=a.seconds,interval=a.interval,sources={},limitations='Sequential external reads;headers do not make vertex payload atomic. Retained buffers may belong to inactive objects. Sampling is not proof of draw submission.')
        for name in ('capture_sky_vertices.py','read_live.py'):
            b=(root/name).read_bytes();(out/name).write_bytes(b);meta['sources'][name]=hashlib.sha256(b).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w',encoding='utf-8') as f:
            while True:
                begin=time.perf_counter()
                try:line=json.dumps(sample(r),allow_nan=False)
                except (OSError,ValueError) as e:line=json.dumps(dict(error=str(e),monotonic=begin));errors+=1
                f.write(line+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(max(0,a.interval-(time.perf_counter()-begin)))
        print(json.dumps(dict(samples=count,errors=errors,output=str(out))))
    finally:K.CloseHandle(r.h)
if __name__=='__main__':main()
