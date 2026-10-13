"""Read-only signal-aspect and diesel-cab source validation.
Native references: 0x5c01c2, 0x5c12c3, 0x5c1457, 0x46634a, 0x42064b.
No remote calls: emulate bounded native selection by external reads.
"""
from read_live import Reader,K
from pathlib import Path
import argparse,json,hashlib,time,datetime

class DetailReader(Reader):
    def signal_heads(self,iterator):
        node,direction,first,last=iterator
        if not node:return []
        if last<first or last-first>256:raise ValueError('Signal-head iterator exceeds bound')
        table=self.u(node+0x20);heads=[]
        for i in range(first,last+1):
            h=self.u(table+i*4)
            if self.u(h)!=0 or self.read(h+0x20,1)[0]!=direction:continue
            definition=self.u(h+0x14);aspect=self.read(h+0x21,1)[0]
            row=dict(address=h,index=i,definition=definition,function_type=self.u(definition+4),
                     flags=self.u(h+0x1c),direction=direction,aspect=aspect)
            if aspect<8:
                aspects=self.u(definition+0x50)
                row['aspect_speed']=self.f(aspects+aspect*12+4)
                row['aspect_flags']=self.u(aspects+aspect*12+8)
            heads.append(row)
        return heads
    def details(self):
        s=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=self.f(0x80acd4),paused=self.u(0x7be0f4))
        iterator=self.unpack(0x809ac4,'IIII')
        try:
            heads=self.signal_heads(iterator);normal=[h for h in heads if h['function_type']==0]
            speed=[h for h in heads if h['function_type']==1]
            # Native 0x5c01c2 chooses maximum aspect within each function type.
            s['next_signal']=dict(iterator=list(iterator),distance=self.f(0x809ad4),heads=heads,
                                  selected_normal=max(normal,key=lambda h:h['aspect']) if normal else None,
                                  selected_speed=max(speed,key=lambda h:h['aspect']) if speed else None)
        except (OSError,ValueError) as e:s['signal_error']=str(e)
        t=self.u(0x7c2ac0);ctl=self.u(0x7b6440);typ=self.u(0x7b6438);lead=self.u(t+0x6a)
        s['player']=dict(train=t,lead=lead,control_type=typ,speed=self.f(t+0x92),acceleration_candidate=self.f(t+0x96))
        if typ==2:
            ed=self.u(lead+0x29a);bc=self.f(lead+0x230)
            if self.unpack(ed+0x622,'H')[0]&4:bc=max(bc,self.f(lead+0x486))
            s['diesel_cab']=dict(throttle=self.f(ctl+0x8c),reverser=self.f(ctl+0xc8),
                                main_res_psi=self.f(lead+0x412),eq_res_psi=self.f(lead+0x436),brake_cyl_psi=bc,brake_pipe_psi=self.f(lead+0x238),
                                current_traction_amps=self.f(lead+0x2c2),dynamic_braking_raw=self.f(lead+0x472),current_dynamic_amps=self.f(lead+0x476),
                                fuel_raw=self.f(lead+0x2ce),engine_rotation_raw=self.f(lead+0x2d2))
            s['diesel_cab']['ammeter_amps']=(s['diesel_cab']['current_traction_amps'] if s['diesel_cab']['dynamic_braking_raw']<=0 else -s['diesel_cab']['current_dynamic_amps'])
        s['sim_time_after']=self.f(0x80acd4);s['same_sim_time']=s['sim_time']==s['sim_time_after']
        s['iterator_stable']=iterator==self.unpack(0x809ac4,'IIII')
        return s

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',type=int,required=True);p.add_argument('--name',required=True)
    p.add_argument('--seconds',type=float,default=0);p.add_argument('--interval',type=float,default=.25);a=p.parse_args()
    if a.seconds<0 or a.interval<=0:p.error('Invalid duration/interval')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False)
    r=DetailReader(a.pid)
    try:
        meta=dict(pid=a.pid,exe=str(r.path),sha256=r.sha,access='QUERY_LIMITED_INFORMATION | VM_READ',seconds=a.seconds,interval=a.interval,
                  warning='Research fields partly static-traced; raw fields are unvalidated; async external reads are not atomic.',sources={})
        for name in ['read_signals_cab.py','read_live.py']:
            data=(root/name).read_bytes();(out/name).write_bytes(data);meta['sources'][name]=hashlib.sha256(data).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2));count=errors=0;start=time.perf_counter()
        with (out/'details.jsonl').open('w') as f:
            while True:
                try:s=r.details()
                except (OSError,ValueError) as e:s=dict(error=str(e),utc=datetime.datetime.now(datetime.timezone.utc).isoformat());errors+=1
                f.write(json.dumps(s,allow_nan=False)+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(a.interval)
        print(json.dumps(dict(output=str(out),samples=count,errors=errors,last=s)))
    finally:K.CloseHandle(r.h)
