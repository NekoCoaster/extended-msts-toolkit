"""Compare live station records with installed declarations; timestamps remain hypotheses."""
import hashlib,json,re,struct
from pathlib import Path
root=Path(__file__).resolve().parent
capture=json.loads((root/'captures/maryland-records-paused-01/records.json').read_text(encoding='utf-8'))
eff=json.loads((root/'captures/maryland-efficiency-paused-01/efficiency.json').read_text(encoding='utf-8'))
activity=Path('C:/MSTS/ROUTES/USA1/ACTIVITIES/morningmaryland.act');service=Path('C:/MSTS/ROUTES/USA1/SERVICES/MarylandPlayerService.srv')
raw=activity.read_bytes();text=raw.decode('utf-16') if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else raw.decode('utf-8-sig')
section=text.split('Player_Service_Definition',1)[1].split('NextServiceUID',1)[0]
values=lambda key:[float(x) for x in re.findall(r'\b'+key+r'\s*\(\s*([-+\d.]+)',section)]
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
records=next(x for x in capture['services'] if x['id']==0);rows=[]
for i,r in enumerate(records['records']):
    words=r['raw_words'];floats=[struct.unpack('<f',struct.pack('<I',x))[0] for x in words]
    rows.append(dict(index=i,platform=r['track_item_id'],platform_matches=r['track_item_id']==values('PlatformStartID')[i],skip_count=words[7]&65535,skip_matches=(words[7]&65535)==values('SkipCount')[i],efficiency=r['efficiency_override'],efficiency_float32_matches=r['efficiency_override']==f32(values('Efficiency')[i]),declared_distance=values('DistanceDownPath')[i],live_distance=r['distance_candidate'],distance_delta=r['distance_candidate']-values('DistanceDownPath')[i],timestamp_candidates=dict(record04=floats[1],record08=floats[2],record0c=floats[3],declared_arrival=values('ArrivalTime')[i],declared_departure=values('DepartTime')[i])))
result=dict(sim_time=capture['sim_time'],selected_is_first=records['selected']==records['records'][0]['address'],player_efficiency=next(x for x in eff['services'] if x['id']==0),records=rows,assets=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (activity,service)],limitations='Static declaration comparison and one paused state. Matching numeric timestamps alone do not establish scheduled/actual semantics. Distance is not an exact asset copy; writer/recomputation unresolved. No selected-record transition observed.')
(root/'maryland-record-comparison.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
