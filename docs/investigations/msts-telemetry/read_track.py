"""Read-only track-position investigation; field names reflect current evidence."""
import argparse,json,datetime,struct
from pathlib import Path
from read_live import Reader,K

class TrackReader(Reader):
    def track(self,p):
        b=self.read(p,0x68);u=lambda o:struct.unpack_from('<I',b,o)[0];f=lambda o:struct.unpack_from('<f',b,o)[0]
        node=u(0);section=u(8)
        row=dict(address=p,node=node,section_index=u(4),section=section,direction=u(12),node_distance=f(16),section_distance=f(20),angles_candidate=[f(o) for o in [24,28,32]],position_candidate=[f(o) for o in [72,76,80]],raw_hex=b.hex())
        if section:
            row['section_origin_tile']=list(self.unpack(section+0x18,'ii'))
            row['section_origin_offset']=list(self.unpack(section+0x20,'fff'))
            row['section_definition_index']=self.unpack(section,'H')[0]
            table=self.u(0x80a118)
            if row['section_definition_index']>=self.u(table+0x10):raise ValueError('Geometry definition index exceeds native table count')
            geometry=self.u(table+0xc)+row['section_definition_index']*0x18
            row['geometry_definition']=dict(address=geometry,raw_hex=self.read(geometry,0x18).hex(),length=self.f(geometry),radius_candidate=self.f(geometry+4),curve_angle_candidate=self.f(geometry+8),configured_width=self.f(geometry+12),skew_angle=self.f(geometry+16),flags_raw=self.u(geometry+20))
            row['section_angles_candidate']=list(self.unpack(section+0x2c,'fff'))
        if node:
            row['node_length']=self.f(node+0x28);row['node_section_count']=self.u(node+0x1c)
            row['section_pointer_matches']=section==self.u(node+0x18)+u(4)*0x40
        return row
    def tracks(self):
        before=self.unpack(0x79d118,'ii');result=[]
        for train in self.trains():
            row=dict(train=train['id'],is_player=train['is_player'],service=train['service_object'],cars=[])
            for car in train['cars']:
                c=dict(address=car['address'],body=car['body'],body_position=car['position'],derailed=car['derailed'])
                try:c['track']=self.track(car['address']+0x128)
                except (OSError,ValueError) as e:c['error']=str(e)
                row['cars'].append(c)
            try:row['service_track']=self.track(train['service_object']+0x4c)
            except (OSError,ValueError) as e:row['service_error']=str(e)
            result.append(row)
        return dict(origin_tile=list(before),origin_stable=before==self.unpack(0x79d118,'ii'),trains=result)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pid',required=True,type=int);p.add_argument('--name',required=True);a=p.parse_args();root=Path(__file__).resolve().parent;out=root/'captures'/a.name;out.mkdir(exist_ok=False);r=TrackReader(a.pid)
    try:
        result=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sim_time=r.f(0x80acd4),paused=r.u(0x7be0f4),sha256=r.sha,tracks=r.tracks())
        result['sim_time_after']=r.f(0x80acd4)
        for name in ['read_track.py','read_live.py']:(out/name).write_bytes((root/name).read_bytes())
        (out/'tracks.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(output=str(out),origin=result['tracks']['origin_tile'],examples=[dict(train=t['train'],first=t['cars'][0]) for t in result['tracks']['trains']])))
    finally:K.CloseHandle(r.h)
