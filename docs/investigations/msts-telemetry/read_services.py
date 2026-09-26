"""Read-only per-train service/driver candidate probe. No AI-control inference."""
import argparse,json,datetime,hashlib,time
from pathlib import Path
from read_live import Reader,K

class ServiceReader(Reader):
    def wide(self,p,limit=256):
        data=bytearray()
        for i in range(limit):
            b=self.read(p+2*i,2)
            if b==b'\0\0':return data.decode('utf-16le',errors='replace')
            data.extend(b)
        raise ValueError('String exceeded bound')
    def registry(self):
        root=self.u(0x809af8);n=self.u(root);seen=set();rows=[]
        addresses=[0x809890]
        while n!=root:
            if not n or n in seen or len(seen)>=256:raise ValueError('Service list bound/cycle')
            seen.add(n);addresses.append(self.u(n+8));n=self.u(n)
        for s in addresses:
            row=dict(address=s,is_player=s==0x809890)
            try:
                row.update(service_id=self.u(s+0x40),train_id=self.u(s+0x44),train=self.u(s+0x158),physicalized_raw=self.u(s+0x134),flags_raw=self.u(s),speed=self.f(s+0x138),target_speed=self.f(s+0x13c),acceleration=self.f(s+0x140),efficiency_candidate=self.f(s+0x208))
                row['strings']={name:self.wide(self.u(s+off)) for off,name in [(8,'service_key'),(12,'display_name'),(16,'train_config'),(20,'path_id')]}
                row['stop_state_words']={hex(off):self.u(s+off) for off in [0x1dc,0x1e0,0x1e4,0x1e8,0x214]}
                row['update_candidate_words']={hex(off):self.u(s+off) for off in [0x144,0x148,0x154]}
                row['update_candidate_floats']={hex(off):self.f(s+off) for off in [0x24,0x14c,0x150]}
            except (OSError,ValueError) as e:row['error']=str(e)
            rows.append(row)
        return dict(sentinel=root,entries=rows)
    def services(self):
        result=[]
        for train in self.trains():
            t=train['address'];s=train['service_object']
            row={k:train[k] for k in ['address','id','is_player','speed_raw','service_object','controller_wrapper']}
            row['car_count']=len(train['cars']);row['derailed_count']=sum(c['derailed'] for c in train['cars'])
            try:
                row['service_train_backlink']=self.u(s+0x158)
                row['backlink_matches']=row['service_train_backlink']==t
                row['flags_raw']=self.u(s)
                row['candidate_floats']={hex(off):self.f(s+off) for off in [0x2c,0x138,0x13c,0x140,0x1ec,0x1f0,0x1f8,0x208,0x210,0x220,0x22c]}
                row['candidate_words']={hex(off):self.u(s+off) for off in [0x18,0x20,0x34,0x38,0x44,0x48,0x12c,0x130,0x154,0x1d0,0x1e0,0x1e4,0x1e8,0x214]}
                row['service_pointer_stable']=self.u(t+0xe6)==s
            except (OSError,ValueError) as e:row['error']=str(e)
            result.append(row)
        return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);p.add_argument('--seconds',type=float,default=0);p.add_argument('--interval',type=float,default=.5);a=p.parse_args()
    if a.seconds<0 or a.interval<=0:p.error('Invalid timing')
    root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=ServiceReader(a.pid)
    try:
        meta=dict(pid=a.pid,sha256=r.sha,access='QUERY_LIMITED_INFORMATION | VM_READ',warning='Offset-labeled candidates; see native evidence before assigning semantic labels.',sources={})
        for name in ['read_services.py','read_live.py']:
            data=(root/name).read_bytes();(out/name).write_bytes(data);meta['sources'][name]=hashlib.sha256(data).hexdigest()
        (out/'metadata.json').write_text(json.dumps(meta,indent=2));start=time.perf_counter();count=0
        with (out/'services.jsonl').open('w') as f:
            while True:
                sample=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4))
                try:
                    sample['trains']=r.services()
                    sample['service_registry']=r.registry()
                except (OSError,ValueError) as e:sample['error']=str(e)
                sample['sim_time_after']=r.f(0x80acd4);sample['same_sim_time']=sample['sim_time']==sample['sim_time_after']
                f.write(json.dumps(sample,allow_nan=False)+'\n');f.flush();count+=1
                if time.perf_counter()-start>=a.seconds:break
                time.sleep(a.interval)
        print(json.dumps(dict(output=str(out),samples=count,last=sample)))
    finally:K.CloseHandle(r.h)
