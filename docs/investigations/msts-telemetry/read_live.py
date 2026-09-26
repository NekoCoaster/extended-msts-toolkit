"""Standalone MSTS research reader. Only QUERY_LIMITED_INFORMATION | VM_READ.
No injection, debugger, remote calls, writes, suspension, or NEMT dependency.
Offsets are evidence from NEMT runtime at 5cd5896, not a portable ABI.
"""
import argparse, ctypes as C, ctypes.wintypes as W, datetime, hashlib, json, math
from pathlib import Path
import struct, time

K = C.WinDLL('kernel32', use_last_error=True)
K.OpenProcess.argtypes = [W.DWORD, W.BOOL, W.DWORD]; K.OpenProcess.restype = W.HANDLE
K.ReadProcessMemory.argtypes = [W.HANDLE, C.c_void_p, C.c_void_p, C.c_size_t, C.POINTER(C.c_size_t)]
K.ReadProcessMemory.restype = W.BOOL
K.CloseHandle.argtypes = [W.HANDLE]
K.QueryFullProcessImageNameW.argtypes = [W.HANDLE, W.DWORD, W.LPWSTR, C.POINTER(W.DWORD)]

class Reader:
    def __init__(self, pid):
        self.h = K.OpenProcess(0x1000 | 0x10, False, pid)
        if not self.h: raise C.WinError(C.get_last_error())
        buf = C.create_unicode_buffer(32768); size = W.DWORD(len(buf))
        if not K.QueryFullProcessImageNameW(self.h, 0, buf, C.byref(size)): raise C.WinError(C.get_last_error())
        self.path = Path(buf.value)
        self.sha = hashlib.sha256(self.path.read_bytes()).hexdigest()
        if self.sha != '2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843':
            raise RuntimeError('Unsupported image SHA256: ' + self.sha)
        if self.read(0x400000, 2) != b'MZ': raise RuntimeError('Expected image base absent')
    def read(self, addr, size):
        if not 0x10000 <= addr <= 0xffffffff-size: raise ValueError(f'Invalid address {addr:#x}')
        buf = C.create_string_buffer(size); actual = C.c_size_t()
        if not K.ReadProcessMemory(self.h, addr, buf, size, C.byref(actual)) or actual.value != size:
            raise OSError(f'Read failed at {addr:#x} size {size}: {C.get_last_error()}')
        return buf.raw
    def unpack(self, addr, fmt): return struct.unpack('<'+fmt, self.read(addr, struct.calcsize('<'+fmt)))
    def u(self, addr): return self.unpack(addr,'I')[0]
    def f(self, addr): return self.unpack(addr,'f')[0]
    def trains(self):
        manager=self.u(0x7bdecc);root=self.u(manager+0x20);table=self.u(0x828108)
        n=self.u(root);seen=set();result=[]
        while n and n!=root:
            if n in seen or len(seen)>=256:raise ValueError('Registry bound/cycle')
            seen.add(n);nxt,prev,index=self.unpack(n,'III')
            if index>=100000:raise ValueError('Invalid train table index')
            t=self.u(table+index*8);car=self.u(t+0x62);visited=set();cars=[]
            while car:
                if car in visited or len(visited)>=256:raise ValueError('Invalid train chain')
                visited.add(car)
                if self.u(car+0x98)!=t:raise ValueError('Train ownership mismatch')
                cars.append(self.car(car));car=self.u(car+0xa8)
            result.append(dict(address=t,table_index=index,id=self.u(t+0x10),kind_byte=self.read(t+0x5a,1)[0],
                               is_player=t==self.u(0x7c2ac0),speed_raw=self.f(t+0x92),lead=self.u(t+0x6a),
                               controller_wrapper=self.u(t+0x72),service_object=self.u(t+0xe6),cars=cars))
            n=nxt
        return result
    def car(self, addr):
        h=self.read(addr,0xac); body,definition=struct.unpack_from('<I',h,0x5c)[0],struct.unpack_from('<I',h,0x94)[0]
        b=self.read(body,0x124)
        if struct.unpack_from('<I',b,0x11d)[0]!=addr: raise ValueError('Body ownership mismatch')
        vec=lambda off:list(struct.unpack_from('<3f',b,off))
        massinv=struct.unpack_from('<f',b,0xc8)[0]
        row=dict(address=addr,body=body,definition=definition,links=[struct.unpack_from('<I',h,o)[0] for o in (0xa0,0xa8)],
                 powered=self.read(definition+0x88,1)[0]==1,position=vec(0x30),right=vec(0xc),up=vec(0x18),forward=vec(0x24),
                 velocity=vec(0x88),angular_velocity=vec(0x94),momentum=vec(0x4c),angular_momentum=vec(0x58),
                 inverse_mass=massinv,mass=1/massinv if massinv>0 else None,body_flags=b[0xf2],derailed=bool(b[0xf2]&4),resting=bool(b[0xf2]&8))
        row['longitudinal_speed']=sum(v*f for v,f in zip(row['velocity'],row['forward']))
        if row['powered']:
            ed=self.u(addr+0x29a); row.update(engine_definition=ed,max_power=self.f(ed+0xfe),max_force=self.f(ed+0x102))
        row['body_pointer_stable']=self.u(addr+0x5c)==body
        return row
    def snapshot(self):
        s=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),monotonic=time.perf_counter(),
               sim_time=self.f(0x80acd4),frame_dt=self.f(0x828fb4),paused=self.u(0x7be0f4),
               train=self.u(0x7c2ac0),controller=self.u(0x7b6440),control_type=self.u(0x7b6438))
        if s['train'] and s['controller'] and s['control_type'] in (1,2,3):
            ctl=s['controller']; steam=s['control_type']==1
            s.update(throttle=self.f(ctl+(0x54 if steam else 0x8c)),reverser=self.f(ctl+(0x8c if steam else 0xc8)))
            pending=[self.u(s['train']+0x6a)]; seen=set(); cars=[]
            while pending:
                a=pending.pop(0)
                if not a or a in seen: continue
                if len(seen)>=256: raise ValueError('Consist exceeds safety bound')
                seen.add(a); car=self.car(a); cars.append(car); pending.extend(car['links'])
            byid={c['address']:c for c in cars}
            s['reciprocal_links']=all(not l or (l in byid and c['address'] in byid[l]['links']) for c in cars for l in c['links'])
            s['cars']=cars
        root=self.u(0x809f1c); s['monitor_root']=root; s['monitor_entries']=[]
        if root:
            n=self.u(root); seen=set()
            while n and n!=root:
                if n in seen or len(seen)>=256: raise ValueError('Monitor list invalid/bound exceeded')
                seen.add(n); nxt,prev,entry=self.unpack(n,'III')
                typ,a,b,c,d,obj=self.unpack(entry,'IffffI')
                # Raw names deliberately avoid inheriting unproved distance/speed semantics.
                s['monitor_entries'].append(dict(node=n,entry=entry,type=typ,f04=a,f08=b,f0c=c,f10=d,object=obj,
                                                  object_flags_1c=self.u(obj+0x1c) if obj else None))
                n=nxt
        try:s['registered_trains']=self.trains()
        except (OSError,ValueError) as e:s['registry_error']=str(e)
        s['sim_time_after']=self.f(0x80acd4)
        s['same_sim_time']=s['sim_time_after']==s['sim_time']
        s['train_pointer_stable']=s['train']==self.u(0x7c2ac0)
        return s

def main():
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--seconds',type=float,default=0)
    p.add_argument('--interval',type=float,default=.25);p.add_argument('--name',required=True);a=p.parse_args()
    if a.interval<=0 or a.seconds<0: p.error('Invalid duration/interval')
    out=Path(__file__).resolve().parent/'captures'/a.name;out.mkdir(parents=True,exist_ok=False)
    r=Reader(a.pid)
    try:
        meta=dict(pid=a.pid,exe=str(r.path),sha256=r.sha,reader_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  access='PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_VM_READ',seconds=a.seconds,interval=a.interval,
                  warning='External asynchronous reads; same clock and stable pointers are checks, not an atomic snapshot guarantee.')
        (out/'metadata.json').write_text(json.dumps(meta,indent=2))
        (out/'reader.py').write_bytes(Path(__file__).read_bytes())
        start=time.perf_counter();count=errors=0
        with (out/'samples.jsonl').open('w') as f:
            while True:
                try: s=r.snapshot()
                except (OSError,ValueError) as e: s={'error':str(e),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()};errors+=1
                f.write(json.dumps(s,allow_nan=False)+'\n'); f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(a.interval)
        print(json.dumps(dict(output=str(out),samples=count,errors=errors)))
    finally: K.CloseHandle(r.h)
if __name__=='__main__': main()
