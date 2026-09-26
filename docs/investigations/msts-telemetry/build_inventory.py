"""Evidence-first discovery inventory. No ranking or keep/drop decisions."""
import re,json,hashlib,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
GAME=Path('C:/MSTS')
rows=[];sources={}
def source(p):
    p=Path(p);key=str(p);sources[key]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size};return key
def read(p):
    data=p.read_bytes();return data.decode('utf-16') if data[:2] in (b'\xff\xfe',b'\xfe\xff') else data.decode('utf-8-sig',errors='replace')
def add(id,meaning,applies,typ,unit,method,evidence,status,cadence,limits):
    rows.append(dict(id=id,meaning=meaning,applicability=applies,value_type=typ,units=unit,extraction=method,evidence=evidence,
                     evidence_status=status,update_or_lifecycle=cadence,limitations=limits))
common='MSTS Bin image SHA256 2a1b52aa40a521df1e68b8df1610fe1e2e54caf4c581911481457e06c8187843 only; external samples are asynchronous; IDs/pointers can be reused after unload.'
ev=['captures/initial-briefing/samples.jsonl','captures/first-running/samples.jsonl','captures/registry-paused/registry.json','captures/ai-running-01/samples.jsonl']
spec=[
('simulation.time','Simulation time value; observed near activity seconds since midnight','session','float32','seconds','[0x80acd4]'),
('simulation.step','Simulation frame delta','session','float32','seconds','[0x828fb4]'),
('simulation.paused','Pause state','session','uint32','boolean-like','[0x7be0f4]'),
('train.registry','Currently registered train identities; future unspawned services excluded','player and registered AI','list','IDs','manager=[0x7bdecc]; sentinel=[manager+0x20]; node+8 indexes [0x828108] with stride 8; entry points to train'),
('train.identity','Native train identifier','player and registered AI','uint32','opaque ID','train+0x10'),
('train.kind_raw','Native train kind byte; player observed 3 and AI 1','player and registered AI','uint8','raw enum','train+0x5a'),
('train.is_player','Train matches selected player global','player and registered AI','bool','boolean','train == [0x7c2ac0]'),
('train.speed','Native signed train speed; compare with per-body speed','player and registered AI','float32','m/s (corroborated by cab conversion)','train+0x92'),
('train.first_car','First car pointer','player and registered AI','pointer32','identity','train+0x62'),
('train.last_car','Last car pointer','player and registered AI','pointer32','identity','train+0x66'),
('train.lead_car','Lead/controlled car pointer','player and registered AI','pointer32','identity','train+0x6a'),
('train.service_pointer','Associated service/runtime object; fields not decoded yet','player and registered AI','pointer32','identity','train+0xe6'),
('car.identity','Vehicle instance address','player and registered AI','pointer32','session identity','bounded consist traversal'),
('car.train_owner','Owning train','player and registered AI','pointer32','identity','car+0x98'),
('car.links','Connections at both ends','player and registered AI','two pointer32','identity','car+0xa0; car+0xa8; verify reciprocity'),
('car.definition','Shared vehicle definition','player and registered AI','pointer32','identity','car+0x94'),
('car.asset_directory','Trainset directory/name string','player and registered AI','UTF-16 string','text','[car+0x94]+0xad0; bounded read'),
('car.powered','Definition identifies powered vehicle','player and registered AI','bool','boolean','byte [[car+0x94]+0x88] == 1'),
('car.body_pointer','Current integration body pointer','player and registered AI','pointer32','identity','car+0x5c; verify body+0x11d owner; reread each sample'),
('body.position','Simulation physics position vector; world/tile origin mapping unresolved','player and registered AI','3 float32','metres; origin unresolved','body+0x30'),
('body.right','Orientation right basis','player and registered AI','3 float32','unit vector','body+0x0c'),
('body.up','Orientation up basis','player and registered AI','3 float32','unit vector','body+0x18'),
('body.forward','Orientation forward basis','player and registered AI','3 float32','unit vector','body+0x24'),
('body.velocity','Linear velocity vector','player and registered AI','3 float32','m/s','body+0x88'),
('body.angular_velocity','Angular velocity','player and registered AI','3 float32','rad/s; inherited mapping','body+0x94'),
('body.momentum','Linear momentum','player and registered AI','3 float32','kg m/s; inherited mapping','body+0x4c'),
('body.angular_momentum','Angular momentum','player and registered AI','3 float32','kg m^2/s; inherited mapping','body+0x58'),
('body.inverse_mass','Inverse mass','player and registered AI','float32','1/kg','body+0xc8'),
('body.flags_raw','Body flags including physical derailment and resting','player and registered AI','uint8','bitfield','body+0xf2'),
('body.derailed','Physical derailment flag','player and registered AI','bool','boolean','body+0xf2 & 4'),
('body.resting','Resting flag','player and registered AI','bool','boolean','body+0xf2 & 8'),
('engine.definition','Engine definition','powered player and AI vehicles','pointer32','identity','car+0x29a'),
('engine.max_power','Configured maximum power','powered player and AI vehicles','float32','W','[car+0x29a]+0xfe'),
('engine.max_force','Configured maximum force','powered player and AI vehicles','float32','N','[car+0x29a]+0x102'),
('player.control_type','Steam/diesel/electric controller type','player','uint32','1/2/3','[0x7b6438]'),
('player.throttle','Throttle/regulator fraction','player','float32','fraction','[0x7b6440]+0x8c diesel/electric; +0x54 steam'),
('player.reverser','Signed reverser setting','player','float32','signed value','[0x7b6440]+0xc8 diesel/electric; +0x8c steam'),
('monitor.event_type','Upcoming track-monitor element type','player; AI equivalent not located','uint32','native enum','[[node+8]+0] in circular list [0x809f1c]; labels at 0x79f898'),
('monitor.distance','Distance to upcoming element','player; AI equivalent not located','float32','metres candidate','entry+0x04; native debug label Dist'),
('monitor.radius','Radius associated with element','player; AI equivalent not located','float32','metres candidate','entry+0x08; native debug label Rad'),
('monitor.gradient','Gradient associated with element','player; AI equivalent not located','float32','slope ratio candidate','entry+0x0c; native debug label Grad'),
('monitor.desired_velocity','Desired velocity associated with element, not necessarily posted limit','player; AI equivalent not located','float32','m/s candidate','entry+0x10; native debug label Des Vel'),
('monitor.object','Referenced route/signal object identity','player; AI equivalent not located','pointer32','identity','entry+0x14'),
('signal.flags_raw','Referenced signal flags; full aspect mapping unresolved','signals referenced by monitor','uint32','bitfield','object+0x1c; only interpret for signal entry types'),
]
for id,meaning,applies,typ,unit,method in spec:
    limits=common
    if id.startswith(('monitor.','signal.')):
        applies='native forward-profile/signal references; current service context and caching unresolved'
        limits+=' Clean AI pass changed UI Stop to Clear without these raw desired-velocity/flag fields mirroring it. Do not export as current signal aspect or assume this global profile is always current player state.'
    if id in ('player.control_type','player.throttle','player.reverser'):
        limits+=' Diesel live validation and steam regulator/cutoff transitions are recorded; electric offsets remain inherited candidates.'
    add(id,meaning,applies,typ,unit,method,ev,'readable in live captures; semantics partly inherited/static','per sample; actual internal producer cadence not fully measured',limits)
for id,meaning,unit,method in [
('car.mass','Vehicle mass','kg','1 / inverse_mass, rejecting zero/nonfinite values'),
('car.longitudinal_speed','Speed projected along body axis','m/s','dot(body.velocity, body.forward)'),
('train.car_count','Number of connected vehicles','count','count validated reciprocal graph'),
('train.total_mass','Connected consist mass','kg','sum validated car masses'),
('car.speed_magnitude','Total 3D speed','m/s','norm(body.velocity)'),
('car.acceleration','Sampled acceleration','m/s^2','velocity difference / advancing simulation time; reject pause, tile and identity discontinuities'),
('car.heading_pitch_roll','Orientation angles','radians/degrees','derive basis with explicit coordinate conventions and singularity handling'),
('train.relative_motion','Relative train separation and closing speed','m; m/s','positions and velocities after proving common coordinate origin'),
('train.lifecycle_events','Spawn/despawn, coupling/splitting and player selection changes','events','diff validated registry/ownership snapshots; guard pointer reuse'),
('car.wheel_rotation_estimate','Rolling wheel speed estimate','rad/s','longitudinal speed / wheel radius; not proof of actual wheel slip or visual phase'),
]:add(id,meaning,'player and registered AI','derived',unit,method,ev,'derived candidate; not all computations implemented','sample cadence; finite differences need stable simulation delta',common)

# Parse balanced SIMIS textual nodes, preserving file location and actual examples.
tok=re.compile(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()]+')
def nodes(text):
    tokens=tok.findall(text);i=0
    def sequence(end=False):
        nonlocal i
        result=[]
        while i<len(tokens):
            t=tokens[i];i+=1
            if t==')':break
            if t=='(':
                result.append(('__anonymous__',sequence(True)));continue
            if i<len(tokens) and tokens[i]=='(':
                i+=1;result.append((t,sequence(True)))
            else:result.append(t)
        return result
    return sequence()
def walk(tree,path=()):
    for x in tree:
        if isinstance(x,tuple):
            k,children=x
            if k.lower() in ('_skip','comment','__anonymous__'):continue
            yield path+(k,),children
            yield from walk(children,path+(k,))

cab={};param={};scanned=[];leaf_paths=set();mixed_paths=set()
files=list((GAME/'TRAINS/TRAINSET').rglob('*.cvf'))
files+=list((GAME/'TRAINS/TRAINSET').rglob('*.eng'))+list((GAME/'TRAINS/TRAINSET').rglob('*.wag'))
files+=[GAME/'ROUTES/USA2/ACTIVITIES/evegrain.act']
files+=list((GAME/'ROUTES/USA2/SERVICES').glob('EveGrain*.srv'))+list((GAME/'ROUTES/USA2/TRAFFIC').glob('EveGrain*.trf'))+list((GAME/'ROUTES/USA2/PATHS').glob('EveGrain*.pat'))
for p in files:
    text=read(p)
    if 'SIMISA' not in text[:40]:continue
    scanned.append(source(p))
    tree=nodes(text)
    if p.suffix.lower()=='.cvf':
        for path,children in walk(tree):
            local={x[0].lower():x[1] for x in children if isinstance(x,tuple)}
            if 'type' not in local or not local['type']:continue
            t=local['type'][0]
            if not isinstance(t,str):continue
            cab.setdefault(t,[]).append(dict(file=str(p),control=path[-1],units=local.get('units'),range=local.get('scalerange')))
    else:
        for path,children in walk(tree):
            atoms=[x for x in children if isinstance(x,str)]
            key=p.suffix.lower()+':'+'.'.join(path)
            mixed=any(isinstance(x,tuple) for x in children)
            if mixed and not atoms:continue
            (mixed_paths if mixed else leaf_paths).add(key)
            sample=dict(file=str(p),path=' / '.join(path),example=atoms,syntax='direct atoms beside child nodes' if mixed else 'leaf atoms')
            if key not in param:param[key]=[]
            if len(param[key])<3:param[key].append(sample)
            elif sample['syntax'] not in {e['syntax'] for e in param[key]}:
                param[key][-1]=sample
for name,examples in sorted(cab.items()):
    add('cab.'+name,name.replace('_',' ').lower()+' native cab input/display channel','player where cab/engine supports it; AI unknown','native channel dependent',
        sorted({str(e['units']) for e in examples if e['units']}) or ['not declared in sampled CVF controls; native units unresolved'],'CVF Type declares channel; trace native cab dispatchers 0x41f357 / 0x42064b / 0x4218ae to actual producers',examples,
        'installed asset declaration; raw field/meaning not yet fully traced','cab render/update; underlying simulation producer may differ','Asset declaration alone does not prove live population, accuracy, units or AI availability. Duplicate displays share channels.')
for key,examples in sorted(param.items()):
    add('config.'+key,key.split(':',1)[1]+' configured value','asset/service/activity dependent; bind by actual runtime identity','SIMIS direct node tokens','as written in source; infer no units',
        'Read installed SIMIS asset; attach configuration metadata to runtime entity',examples,'static configuration extracted; not a live changing value','asset load or reload','Dynamic counterpart, defaulting and parser semantics require separate tracing. Not every config token has a changing telemetry counterpart.')
native=json.loads((ROOT/'native-cab-map.json').read_text())
byid={r['id']:r for r in rows}
for channel in native['channels']:
    key='cab.'+channel['name']
    if key not in byid:
        add(key,channel['name'].replace('_',' ').lower()+' native cab channel name','player where native renderer supports it; AI unverified','channel dependent','unresolved','Native name table at 0x77fce0; exact-image dispatcher jump tables',[], 'native name and routing mapped; live availability unverified','cab update; producer cadence unmeasured','Name existence does not establish a supported or populated value; extended channels remain to inspect.')
        byid[key]=rows[-1]
    row=byid[key]
    row['native_enum']=channel['enum'];row['native_dispatch']=channel['dispatch']
    row['evidence'].append('native-cab-map.json')
    row['extraction']='Native cab dispatchers mapped per engine; inspect native_dispatch for exact branch and source excerpt'
    row['evidence_status']='native name and static dispatcher mapping; runtime support depends on channel and engine'
diesel_sources={
    'MAIN_RES':('lead+0x412','PSI'),
    'EQ_RES':('lead+0x436','PSI'),
    'BRAKE_PIPE':('lead+0x238','PSI'),
    'BRAKE_CYL':('lead+0x230; if uint16 [[lead+0x29a]+0x622] & 4, max with float lead+0x486','PSI'),
    'AMMETER':('lead+0x2c2 traction amps; when lead+0x472 > 0 use negative lead+0x476 dynamic amps; multiply by 1000 only for non-AMPS cab branch (MILLIAMPS)','amps'),
    'LOAD_METER':('same diesel producer as AMMETER; cab unit conversion applies','cab unit dependent'),
}
for name,(method,unit) in diesel_sources.items():
    row=byid['cab.'+name]
    row['diesel_live_source']=dict(method=method,units=unit,lead='[player_train+0x6a]',applicability='player diesel lead; AI population unverified')
    row['evidence'].append('captures/detail-clear-paused/details.jsonl')
    row['evidence_status']='native diesel producer traced; paused pressures matched cab display; dynamic transitions recorded separately'
signal_specs=[
('signal.next_iterator','Player next-signal track iterator','4 uint32','node/direction/index bounds','0x809ac4..0x809ad0'),
('signal.next_distance','Distance to player next signal','float32','metres','[0x809ad4]'),
('signal.head_identity','Directional signal head identity','pointer32','session identity','table=[iterator.node+0x20]; table[index*4], inclusive iterator bounds; require head+0 == 0 and byte head+0x20 == direction'),
('signal.function_type','Signal head function selector','uint32','0 normal, 1 speed','[[head+0x14]+4]'),
('signal.aspect','Live aspect of directional head; select maximum aspect among normal heads for monitor','uint8','native aspect enum','head+0x21; native 0x5c01c2, 0x5c12c3'),
('signal.aspect_speed','Speed associated with current signal aspect','float32','m/s candidate; -1 sentinel observed','definition=[head+0x14]; aspect_table=[definition+0x50]; aspect_table+aspect*12+4'),
('signal.aspect_flags','Flags associated with aspect definition','uint32','bitfield','aspect_table+aspect*12+8'),
]
for key,meaning,typ,unit,method in signal_specs:
    add(key,meaning,'player next-signal context; independent AI iterator not located',typ,unit,method,['pass07/0046634a.c','pass08/005c01c2.c','pass08/005c1457.c','captures/detail-clear-paused/details.jsonl','captures/signal-transition-01/details.jsonl','pass09-byte-verification.json'],'native source traced; same-head aspect 0 to 7 observed with UI Stop to Clear','head state live; iterator refresh conditions and cadence need validation',common+' Bounds and direction must be validated. Do not interpret cached forward-profile flags as aspect. Only Stop/Clear transition tested; other aspect semantics and AI iterators remain unverified.')
payload_extra=len(signal_specs)
service_fields=json.loads((ROOT/'service-fields.json').read_text())
for name,meaning,typ,unit,method in service_fields:
    add('service.'+name,meaning,'player and loaded AI services; AI driver fields differ from player controls',typ,unit,method,['captures/service-registry-paused-01/services.jsonl','pass10/005a7a5f.c','pass10/005a8ecb.c','pass11/005a41c2.c','pass11/005a5c9a.c','pass12/005a33af.c'],'native code traced and paused values readable; lifecycle and changing driver transitions not yet validated','service lifetime; physics instantiation is separate; per-field producer cadence unmeasured',common+' Null train pointer does not mean missing service. Physical-instance flag is AI-specific: observed player has flag zero despite valid train. Stop-state semantic labels remain candidates. Service strings corroborated against installed SRV files.')
payload_extra+=len(service_fields)
for row in rows:
    if row['id']=='service.flags_raw':
        row['evidence'].extend(['SPEED-CAP-FINDINGS.md','pass47/005a5eb1.asm','pass50/00614c8e.asm','captures/service-class-paused-01/snapshot.json'])
        row['extraction'] += '; class bit0x4 means freight found at initialization; bit0x2 default non-freight, not passenger occupancy;0x10 posted cap enabled;0x20 conditional route cap enabled'
        row['limitations'] += ' Class is traced at initialization and corroborated on the paused freight player; non-freight runtime and post-coupling reclassification untested.'
    if row['id'] in {'service.posted_speed_cap','service.additional_speed_cap','service.effective_speed_limit'}:
        row['evidence'].extend(['SPEED-CAP-FINDINGS.md','captures/speed-caps-paused-01/snapshot.json','pass45/004f5862.asm','pass46/004faf10.asm','pass46-byte-verification.json'])
        row['evidence_status']='native setters and effective selection traced; all three paused service caps reproduced exactly; posted-limit crossing transition not captured'
        row['limitations'] += ' Speedpost byte, not float payload, feeds traced cap conversion. Direction and applicability gates matter. Inactive service can retain a numerical cap. Additional cap has multiple producer contexts; no universal temporary/permanent label.'
    if row['id'] in {'service.registry','service.train_pointer','service.physicalized_raw','service.flags_raw','service.speed','service.target_speed','service.acceleration'}:
        row['evidence'].extend(['captures/scheduled-traffic-01/lifecycle.jsonl','scheduled-traffic-01-summary.json','AI-LIFECYCLE-FINDINGS.md'])
        row['evidence_status']='native source traced; physical disappearance and later scheduled offscreen activation observed; inactive AI retains stale speed; gate-off trigger and earlier position outlier remain unproven'
        row['limitations'] += ' First AI retained positive speed after its update gate disabled and track position froze. Positive speed alone does not establish movement; physical absence does not establish service deletion. See SERVICE-UPDATE-FINDINGS.md.'
    if row['id'] in {'service.scheduled_start','service.update_active','service.integration_interval','service.last_update_time','service.travel_sign_selector'}:
        row['evidence'].extend(['pass28/005ae0f8.asm','pass28/005ae731.asm','pass29/005a662e.asm','pass29/005ae68e.asm','pass28-byte-verification.json','pass29-byte-verification.json','captures/service-schedule-paused-01/services.jsonl','SERVICE-UPDATE-FINDINGS.md'])
        row['evidence_status']='native scheduler semantics traced and bytes verified; paused active/inactive AI corroborated; exact gate transition not captured'
        row['limitations'] += ' Last-update time uses a different observed base for player; midnight behavior untested. Inactive alone does not distinguish not-yet-started from finished. Motion sign is not cab reverser.'
track_fields=json.loads((ROOT/'track-fields.json').read_text())
for name,meaning,applies,typ,unit,method in track_fields:
    add('track.'+name,meaning,applies,typ,unit,method,['captures/track-paused-01/tracks.json','pass13/005b277e.c','pass14/005b3fad.asm','pass14-byte-verification.json'],'native traversal/conversion traced; paused player and AI records readable; moving boundary validation pending','track traversal; origin can shift globally; sample origin before and after',common+' Track reference and physics body centre differ. No latitude/longitude conversion proven. Read signed tiles, bounded section indexes and stable origin; derivative fields require continuity checks.')
payload_extra+=len(track_fields)
geometry_ids={'geometry_length','geometry_radius','geometry_curve_angle','geometry_width','geometry_skew','geometry_flags_raw','section_angles','curvature_magnitude','straight_grade_candidate'}
for row in rows:
    if row['id'] in {'track.'+key for key in geometry_ids}:
        row['evidence'].extend(['pass31/005caf51.asm','pass31-byte-verification.json','pass30-byte-verification.json','captures/geometry-typed-paused-01/lifecycle.jsonl','geometry-summary.json','TRACK-GEOMETRY-FINDINGS.md'])
        row['evidence_status']='native geometry parser/traversal traced and bytes verified; four definitions matched installed assets; grade remains a scoped derived candidate'
        row['limitations'] += ' Geometry definitions are loaded configuration joined to runtime location, not independent physics measurements. Skew and flag transitions untested; width is not established rail gauge. Curvature is nominal magnitude; travel-relative sign and curved grade remain unresolved.'
topology_fields=json.loads((ROOT/'topology-fields.json').read_text())
for name,meaning,typ,unit,method in topology_fields:
    add('topology.'+name,meaning,'shared route infrastructure linked to player and AI; connected component only',typ,unit,method,['pass32/005b2fc5.asm','pass32-byte-verification.json','captures/topology-route-map-paused-01/topology.json','topology-summary.json','TRACK-TOPOLOGY-FINDINGS.md'],'native traversal traced; 726-node graph read; 718 derived route IDs uniquely matched; switch transitions untested','route load/unload; junction selection may change independently of train sampling',common+' Pointer graph is not stable route identity. Layout differs by kind. Disconnected runtime components not enumerated. Selected branch is not reservation, occupancy, authorization or proof of blade animation. Ambiguous route IDs must remain unavailable.')
infrastructure_fields=json.loads((ROOT/'infrastructure-fields.json').read_text())
for name,meaning,typ,unit,method in infrastructure_fields:
    add('infrastructure.'+name,meaning,'route-wide; presence and signal associations join to player/AI services',typ,unit,method,['captures/infrastructure-paused-01/infrastructure.json','infrastructure-summary.json','pass35/005b9443.asm','pass35/005d04d3.asm','pass35/005c4ecf.asm','pass35-byte-verification.json','INFRASTRUCTURE-FINDINGS.md'],'native traversal/release traced; complete 732-node route match; paused presence and associations readable','route and service lifecycles; dynamic acquisition/release cadence untested',common+' Presence is not a track-block occupancy boolean or proof of physical simulation. Signal association acquisition and reservation semantics remain unverified. Null association is not a clear aspect or movement permission. All-node coverage verified only for current loaded route.')
for row in rows:
    if row['id']=='topology.route_node_id_candidate':
        row['extraction']='Registry index+1 in database node table; all 732 IDs corroborated against current TDB kinds, pins and vector geometry. Preserve route-build provenance.'
        row['evidence'].append('infrastructure-summary.json')
        row['evidence_status']='all 732 registry-derived route IDs validated in current route; earlier geometry ambiguity resolved'
        row['limitations']=common+' This is index-derived identity for the tested route, not a native embedded ID field; validate after route edits/reload.'
interaction_specs=[
('train.definition_mass_sum','Stored sum of connected vehicle definition masses','physical player/AI trains','float32','kg; both sampled definitions matched source tonnes*1000','train+0x9a=sum(definition+0x444), producer00608800','paused23-car player sum and two installed definitions matched exactly; changing load/AI untested'),
('train.definition_length_sum','Stored sum of connected vehicle definition lengths','physical player/AI trains','float32','metres; both sampled definitions matched third Size component','train+0xaa=sum(definition+0x400), producer00608800','paused23-car player sum and two installed definitions matched exactly; coupling changes untested'),
('sound.region_count','Allocated per-train sound-region table count','session and physical trains','uint32','record count','[0x7c2e88]; allocation0060806f uses count*12','native allocation traced; paused count10'),
('sound.region_handles','Per-region pair of opaque sound handles','physical player/AI trains','two uint32','opaque handle identities; zero absent','[[train+0xea]+0xc]+region_index*12, offsets0/4; bound by[7c2e88]','native allocation/release traced; only default player handles nonzero in paused capture'),
('sound.region_last_interaction_tick','Most recent sound-region interaction timer tick','physical player/AI trains','uint32','Windows timeGetTime milliseconds, wraps32bits; not simulation time','region record+8; written by004ef178; consumed by00608800','native writer/expiry traced; all paused timestamps0, changing timestamp untested'),
('pickup.eligibility_flags','Pickup proximity and speed eligibility flags','route pickup; physical player/AI trains','uint32','bitfield','kind2 item+0x2c; bits8/0x10 reset by004dcc65 and set by004dcc7f','native traced; paused route pickup flags0'),
('pickup.candidate_vehicle','Last vehicle selected by pickup eligibility scan','physical player/AI vehicles','pointer32','session vehicle identity','kind2 item+0x34; use only with eligibility flags and valid vehicle lifetime','native writer traced; paused value null; nonnull transition untested'),
('hazard.state_candidate','Hazard current-state candidate','loaded route hazard; physical player/AI interactions','uint32','raw enum','kind4 linked world object+0xac; compared with9 by004d3a19','native consumer traced; live world object unavailable'),
('hazard.requested_state','Hazard requested state','loaded route hazard; physical player/AI interactions','uint32','raw enum; observed code writes5/7/9','kind4 linked world object+0xb0; written by004d3a19','native writer traced; live world object unavailable'),
('hazard.trigger_latch','Hazard trigger latch candidate','loaded route hazard; physical player/AI interactions','uint8','boolean-like','kind4 linked world object+0xcc; gates and records trigger handling','native read/write traced; reset and live transition unverified'),
('crossing.request_state','Aggregated crossing request; animation meaning unverified','route crossing; player and AI services','uint32','raw enum 0..4','kind7 item+8 indexes [828108] stride8; linked object+0x90','native traced; no linked crossing objects in paused capture'),
('crossing.flags_raw','Crossing flags including player warning logic','route crossing; some player-only bits','uint32','bitfield','linked crossing object+0x84; bits8/0x10 used by004d7e0c','native traced; no linked crossing objects in paused capture'),
('sound.region_item_index','Region index used by sound interaction handler','route metadata for physical player/AI','uint32','region index','kind10 item+0x2a; unaligned','1030 paused item reads; playback not validated'),
('sound.reference_distance_candidate','Sound-region reference distance candidate','physical player and AI trains','float32','distance candidate; units unverified','[[train+0xea]+0]','native consumer traced; paused player readable'),
('sound.nearest_distance_candidate','Nearest sound-region boundary distance candidate','physical player and AI trains','float32','distance candidate; units unverified','[[train+0xea]+4]','native minimum-selection writer traced; paused player readable'),
('sound.selected_region','Selected sound-region index','physical player and AI trains','uint32','region index','[[train+0xea]+8]','native selection writer traced; paused player readable')]
for key,meaning,applies,typ,unit,method,status in interaction_specs:
    add(key,meaning,applies,typ,unit,method,['TRACK-INTERACTION-FINDINGS.md','captures/track-interactions-paused-01/snapshot.json','pass51/004d7e0c.asm','pass51/004ef178.asm','pass51-byte-verification.json','pass52-byte-verification.json'],status,'interaction dispatch; exact refresh/reset cadence unmeasured',common+' Null world linkage means unavailable, not inactive. Request enum is not verified barrier animation; sound selection is not audible playback. Physical AI sound state and all transitions remain unvalidated.')
payload_extra+=len(interaction_specs)
for row in rows:
    if row['id'] in {'train.definition_mass_sum','train.definition_length_sum'}:
        row['evidence']=['CONSIST-AGGREGATE-FINDINGS.md','captures/consist-totals-paused-01/snapshot.json','consist-asset-summary.json','pass56/00608800.asm','pass57/0060820c.asm','pass57-byte-verification.json','pass58-byte-verification.json']
        row['update_or_lifecycle']='callback0x10 registered by0060820c; pause/resume experiment shows repeated running updates via same-function+d6 accumulator at0.1s sampling; exact callback rate unresolved'
        row['evidence'].extend(['UPDATE-CADENCE-FINDINGS.md','update-cadence-summary.json','captures/update-cadence-01/samples.jsonl'])
        row['limitations']=common+' Definition totals differ in provenance from physics-body mass sums; dynamic load/fuel inclusion unproven. Empty car chain skips recalculation. No physical AI or coupling transition validated.'
    if row['id'].startswith('sound.'):
        row['evidence'].extend(['pass56/0060806f.asm','pass56/00608800.asm','pass56/00609713.asm','pass56-byte-verification.json','captures/sound-table-paused-01/snapshot.json'])
        row['limitations'] += ' Nearest distance resets to the train length sum; not always a measured boundary. Region0 and selected region bypass timestamp expiry; others expire after unsigned tick age exceeds10000ms only when consumer executes. Handles are opaque, not proof of playback.'
    if row['id']=='service.flags_raw':
        row['extraction'] += ';00608800 also recomputes class from physical cars, so initialization is not the only writer'
        row['evidence'].extend(['pass56/00608800.asm','pass56-byte-verification.json'])
for row in rows:
    if row['id'].startswith(('pickup.','hazard.')):
        row['evidence'].extend(['captures/pickup-hazard-paused-01/snapshot.json','pass53/004dcc7f.asm','pass53/004d3a19.asm','pass54/004dcc65.asm','pass53-byte-verification.json','pass54-byte-verification.json'])
        row['limitations'] += ' Pickup candidate pointer can outlive eligibility bits; resource transfer is unproven. Hazard state numbers are not animation names; no loaded hazard was sampled.'
track_item_fields=json.loads((ROOT/'track-item-fields.json').read_text())
for name,meaning,typ,unit,method in track_item_fields:
    add('track_item.'+name,meaning,'shared route metadata joined to player/AI track context; subtype-specific',typ,unit,method,['captures/track-items-paused-01/items.json','track-item-summary.json','pass36-byte-verification.json','pass37-byte-verification.json','TRACK-ITEM-FINDINGS.md'],'native serializer traced; all present platform/siding/speedpost payloads matched installed asset values within stated tolerances','loaded configuration; runtime updates and reload lifecycle not validated',common+' This is stored item data, not automatically active gameplay state. EmptyItem lacks assumed common payload. Interpret speedpost subtype before units; paired item is not a service ID. Passenger updates and effective restrictions untested.')
for row in rows:
    if row['id']=='track_item.speedpost_byte_value':
        row['evidence'].extend(['SPEED-CAP-FINDINGS.md','pass45/004f5862.asm','pass46-byte-verification.json'])
        row['evidence_status'] += '; native restriction conversion traced, crossing transition untested'
    if row['id']=='infrastructure.item_kind':
        row['units']='0 signal, 2 pickup, 3 platform, 4 HazzardItem, 6 siding, 7 level crossing, 8 speedpost, 9 empty, 10 sound region; other kinds unobserved'
        row['evidence'].extend(['track-item-summary.json','pass36/005b5475.asm'])
        row['evidence_status']='all 2970 live item indexes matched TDB subtype names; native serializer supports observed mapping'
environment_fields=json.loads((ROOT/'environment-fields.json').read_text())
for name,meaning,typ,unit,method in environment_fields:
    add('environment.'+name,meaning,'current rendered environment; shared scene state, not independent per-train weather',typ,unit,method,['captures/environment-paused-01/environment.json','pass15/0053314d.c','pass16/004902e2.asm','../msts-precipitation/SPECIFICATION.md','../msts-precipitation/terrain-research/TERRAIN-SHADER-SPEC.md'],'inherited native research plus current paused read; scene transitions not tested in this phase','render/environment lifecycle; paused samples may retain last rendered state',common+' Null subsystems must be represented as absent. Density is not rainfall intensity. Particle position units depend on state; counts are not proof of visible draw count. Wind and lighting are render values, not validated train-force or adhesion inputs.')
payload_extra+=len(environment_fields)
activity_fields=json.loads((ROOT/'activity-fields.json').read_text())
for name,meaning,typ,unit,method in activity_fields:
    add('activity.'+name,meaning,'loaded activity; observed player location objectives, other event kinds untested',typ,unit,method,['captures/activity-events-paused-01/activity.json','pass19/0059c477.asm','pass20/0059d037.asm','pass21/0059c2ed.asm','pass23/005902ef.c','C:/MSTS/ROUTES/USA2/ACTIVITIES/evegrain.act'],'three loaded location events corroborated against ACT file; runtime trigger/state transitions untested','activity load and event evaluation; field-specific cadence unmeasured',common+' Parse category before reading subtype extension. Event state labels remain tentative. Presence of success outcome does not mean activity succeeded. Existing activity-end patches can affect observed failure behavior.')
for row in rows:
    if row['id'].startswith('activity.'):
        row['evidence'].extend(['ACTIVITY-EVALUATOR-FINDINGS.md','captures/activity-evaluator-paused-02/activity.json','pass64-byte-verification.json','pass65-byte-verification.json','pass66-byte-verification.json'])
        row['evidence_status']='loaded definitions matched ACT; native trigger gate/latch/outcome handling traced and byte-verified; actual firing transitions untested'
        row['update_or_lifecycle']='event evaluation and outcome processing for mutable states; loaded metadata for definitions; runtime firing cadence unmeasured'
event_condition_fields=[
    ('time_event_clock','Clock read by time-event condition','float32','native time units; approximately elapsed activity seconds in one sample, producer unresolved','[0x80acd0];0059b24c compares event+0x6e strictly below this value'),
    ('event.horizontal_distance','Horizontal distance from first player car to location trigger','derived float','metres','Convert event tile/offset using current origin and2048m tiles; subtract first car+0x170 X/Z; sqrt horizontal squared distance'),
    ('event.location_condition','Reconstructed location-event spatial and optional stop predicate','derived boolean','true/false for finite ordinary inputs','distance squared < radius squared AND (TriggerOnStop=0 OR abs(player train+0x92)<double[0x7706d8])')]
for name,meaning,typ,units,method in event_condition_fields:
    add('activity.'+name,meaning,'player activity; location condition uses first player car, not AI',typ,units,method,['ACTIVITY-EVALUATOR-FINDINGS.md','captures/event-conditions-paused-01/conditions.json','pass66/0059b146.asm','pass67/0059e3ca.asm','pass67-byte-verification.json','pass68-byte-verification.json'],'native consumers traced; finite paused reconstruction consistent with clear latches far outside radii; no firing transition','time-event evaluation or derived on sampling; producer cadence and reset for clock unresolved',common+' Reconstructed condition is not a native invocation or proof of firing. Activation gate, latch, reversal and activity-stop flag also matter. Origin/near-boundary/nonfinite behavior unvalidated; no full x87 emulation.')
for row in rows:
    if row['id']=='activity.time_event_clock':
        row.update(meaning='Elapsed clock accumulator used by time-event conditions',units='seconds since clock setter reset; independent float accumulator',extraction='[0x80acd0]; native00645af0 adds dt;00645d12 resets to0; current additions patched by NEMT UnlockFPS',evidence_status='native producer/reset traced; current live timing adapters match NEMT source pattern; one paused sample')
        row['evidence'].extend(['CLOCK-FINDINGS.md','captures/clock-paused-01/clock.json','captures/clock-paused-01/live-clock-patches.json','pass70-byte-verification.json','pass71-byte-verification.json'])
        row['limitations']+=' Native clock additions are patched in this installation; no stock timing drift validation. Distinct accumulator must not be replaced by day-time minus start-time.'
for name,meaning,method,units in [('internal_calendar','Internal clock day/month/year','uint32 at0x80acb8/0x80acbc/0x80acc0','day/month/year; intended activity-date provenance unverified'),('clock_components','Internal clock second/minute/hour','uint32 at0x80acc4/0x80acc8/0x80accc','second/minute/hour')]:
    add('session.'+name,meaning,'shared session clock','uint32[3]',units,method,['CLOCK-FINDINGS.md','captures/clock-paused-01/clock.json','pass70/00645af0.asm','pass70/00645d12.asm','pass71-byte-verification.json'],'native clock update/setter traced and paused values read; current clock additions patched','clock update and initialization; midnight/reload transitions untested',common+' Internal calendar is not established as narrative activity date. Leap/calendar validity and source initialization remain unresolved. Live timing differs from original disk instructions.')
payload_extra+=len(activity_fields)
vehicle_fields=json.loads((ROOT/'vehicle-system-fields.json').read_text())
for name,meaning,typ,unit,method in vehicle_fields:
    add(name,meaning,'physical player and AI vehicles; current detailed sample covers player only',typ,unit,method,['captures/vehicle-systems-running-01/vehicles.json','pass24/00635dfb.c','pass25/006171f8.asm','pass26/0062c679.c','pass26/0062d335.c'],'static source tracing plus stopped-player values during running simulation; independent AI population untested','vehicle physics step; body buffer swaps and solver scratch state can invalidate comparisons',common+' Requested brake force can exceed configured MaxBrakeForce and is not proven actual wheel/rail force. Pressure/coupler transitions need dedicated tests; no coupling changes performed.')
payload_extra+=len(vehicle_fields)
session_fields=json.loads((ROOT/'session-fields.json').read_text())
for name,meaning,typ,unit,method in session_fields:
    add('session.'+name,meaning,'activity session',typ,unit,method,['captures/session-header-running-01/session.json','pass27/0058f066.asm','pass27/0058bf90.asm','C:/MSTS/ROUTES/USA2/ACTIVITIES/evegrain.act'],'loaded values match ACT; elapsed is derived and midnight semantics untested','header load/reset; elapsed follows advancing simulation clock',common+' Header parser receives activity+4, so raw parser-relative offsets must include that base adjustment. Do not infer calendar date from narrative briefing. Enum name mapping remains incomplete.')
payload_extra+=len(session_fields)
evaluation_fields=[
    ('speed_episode_count','Completed speed-violation episode count','uint32','episodes; collector limit40','[0x809790+0x38]'),
    ('speed_episode_duration','Total duration of closed speed-violation episodes','float32','seconds; excludes open episode and stops collecting at40','[0x809790+0x44]'),
    ('speed_episode_active','Current speed-violation episode state and retained details','structure','active flag; start seconds, location raw, adjusted peak/limit native speed, subtype raw','activity0x809810+0x398 flag; +0x388 start,+0x38c location,+0x390 adjusted peak,+0x394 limit,+0x39c subtype'),
    ('speed_episode_records','Completed speed-violation episode records','list of24-byte records','mixed start/duration seconds, location raw, adjusted speed/limit and subtype','sentinel[0x809790+0x28]; node next+0,record+8; record float0/4/8/c/10 and uint32+14')]
for name,meaning,typ,units,method in evaluation_fields:
    add('evaluation.'+name,meaning,'player activity evaluation; not AI telemetry',typ,units,method,['EVALUATION-FINDINGS.md','captures/evaluation-paused-01/evaluation.json','pass75/00586987.asm','pass75-byte-verification.json','pass73/004963b7.asm'],'native collector and storage traced; empty paused state read, no nonzero episode validation','per activity evaluation, capped at40 closed episodes; report also has teardown-only fields',common+' Collector gate can leave stale active details once capped. Closed duration excludes ongoing episode. Adjusted peak is not maximum raw train speed. Restriction precedence, tolerance, location units and subtype names need further tracing; no actual violation transition validated.')
for row in rows:
    if row['id'].startswith('evaluation.'):
        row['evidence'].extend(['captures/evaluation-paused-02/evaluation.json','pass76-byte-verification.json','pass77-byte-verification.json','pass78-byte-verification.json'])
        row['limitations']+=' Adjusted speed is max(abs(activity+0x1b8)-0.8940799832344055,0), approximately a2mph tolerance. Location comes from kind8/subtype0 distance-marker search; route units and interpolation behavior remain unvalidated.'
for name,meaning,typ,units,method in [('operational_error_count','Retained operational-error record count','uint32','records','[0x809790+0x34]'),('operational_error_records','Operational-error records with time, marker location and raw code','list of12-byte records','time seconds; marker location raw; code enum unresolved','sentinel[0x809790+0x24]; node next+0,record+8; record float time+0/location+4,uint32 code+8')]:
    add('evaluation.'+name,meaning,'player activity evaluation',''+typ,units,method,['EVALUATION-FINDINGS.md','captures/evaluation-paused-02/evaluation.json','pass76/00586226.asm','pass75/00585e59.asm','pass76-byte-verification.json'],'native append path traced; two retained records match stored count, emission not observed','appended on traced rising controller conditions; initialization/reset and global bounds unresolved',common+' Raw codes4 and8 observed, not independently named UI errors. Retained timestamps do not establish capture-time causality. Location is marker-derived with unresolved route units. No AI equivalent established.')
for row in rows:
    if row['id']=='evaluation.operational_error_records':
        row['units']='time seconds; marker location displayed as mile/km by report flag; codes2 penalty brake,4 emergency brake applied,8 penalty power cutout,16 penalty engine shutdown,32 user emergency brake,64 left station while loading'
        row['evidence'].extend(['evaluation-label-map.json','map_evaluation_labels.py','pass80-byte-verification.json'])
        row['evidence_status']='two retained records match count; native display dispatch maps codes4/8 to installed English resource labels; emission not observed'
        row['limitations']='Exact-image/installed-resource mapping only; preserve raw code. Codes4 and32 are distinct. No causal input or live emission proof. Marker interpolation and route conversion remain unvalidated. No AI equivalent established.'
for prefix,title,count_offset,list_offset in [('freight_durability','Freight durability',0x3c,0x2c),('passenger_comfort','Passenger comfort',0x40,0x30)]:
    for suffix,meaning,typ,units,method in [('count',title+' exceedance record count','uint32','records; both collectors stop if either count reaches40',f'[0x809790+{count_offset:#x}]'),('records',title+' exceedance time and marker-location records','list of8-byte records','time seconds; marker location raw',f'sentinel[0x809790+{list_offset:#x}]; node next+0,record+8; record float time+0/location+4')]:
        add('evaluation.'+prefix+'_'+suffix,meaning,'player consist evaluation; not AI telemetry',typ,units,method,['EVALUATION-FINDINGS.md','captures/evaluation-paused-03/evaluation.json','vehicle-condition-labels.json','pass75/00586666.asm','pass74/0043bc16.asm','pass74-byte-verification.json','pass75-byte-verification.json'],'native collector and installed display labels traced; empty paused lists read, no exceedance emission observed','shared30-second interval after either kind records; both disabled at either count40',common+' Sampled evaluation records, not complete event history or measured physical damage. No vehicle ID in records. Condition compares loaded Durability with a threshold derived from stored acceleration; see VEHICLE-MOTION-EVALUATION.md. Shared Default ExtraParameters indices23/24 resolved in DEFAULT-PARAMETER-FINDINGS.md. Freight branch takes precedence over passenger-bearing definition. Marker conversion and reset lifecycle unvalidated.')
for name,meaning,unit,method in [('stored_velocity','Native stored car signed speed','m/s','car+0x1bc;0062924c signed magnitude of physics velocity; derailed branch unsigned'),('stored_acceleration','Native stored car signed acceleration','m/s squared','car+0x1c0;0062924c signed force magnitude times inverse mass; derailed branch unsigned'),('loaded_durability','Durability copied from service/consist definition','native dimensionless scalar','car+0x28e copied from definition+0xa0 by005a7821/005a7a5f; token4028c Durability')]:
    add('car.'+name,meaning,'physical player and AI cars; fresh validation player only','float32',unit,method,['VEHICLE-MOTION-EVALUATION.md','vehicle-evaluation-labels.json','captures/vehicle-evaluation-paused-02/snapshot.json','pass81-byte-verification.json','pass82-byte-verification.json','pass83-byte-verification.json'],'native producers/display/parser traced;23 stopped player cars read; moving and AI behavior untested','motion physics update with branch gates; Durability copied during creation, later writers not exhaustively excluded',common+' Stored signed magnitude is not longitudinal projection or finite-difference acceleration. Derailment changes sign semantics; skip flag and body swaps matter. Durability is loaded configuration, not damage. One debug call differs live outside relevant display instructions; exact-image offsets only.')
for row in rows:
    if row['id'] in {'car.stored_velocity','car.stored_acceleration','car.loaded_durability'}:
        row['evidence'].extend(['vehicle-motion-summary.json','captures/vehicle-motion-restart-01/samples.jsonl','captures/vehicle-motion-ai-01/samples.jsonl','captures/vehicle-motion-final-paused-01/snapshot.json','pass84-byte-verification.json','pass85-byte-verification.json'])
        row['applicability']='physical player and AI cars;23 player and22 AI cars sampled in restarted preferred activity'
        row['evidence_status']='native sources traced; moving/braking player and changing-speed physical AI sampled; intact consists; no reader errors'
        row['limitations']+=' AI skip flags bypass ordinary physics writer: stored acceleration stayed0 despite changing AI speed, so it is not validated AI acceleration. AI speed has service-driven producer005a7337 and predecessor copy00636475. Same-step stable reads still showed up to0.01524m/s speed reconstruction discrepancy for player; not atomic equality proof.'
for name,meaning,offset,units in [('durability_acceleration_ceiling','Loaded shared evaluation acceleration ceiling',0x7cc,'m/s squared'),('durability_acceleration_scale','Loaded shared evaluation acceleration normalization scale',0x7d0,'reciprocal m/s squared')]:
    add('evaluation.'+name,meaning,'shared Default wagon configuration used by player evaluation; not individual AI physics','float32',units,f'[[0x80aa1c]+0x94]+{offset:#x}; Default ExtraParameters indices23/24',['DEFAULT-PARAMETER-FINDINGS.md','default-parameters-map.json','captures/default-threshold-paused-01/snapshot.json','pass87-byte-verification.json','pass88-byte-verification.json','pass89-byte-verification.json','C:/MSTS/TRAINS/TRAINSET/DEFAULT/default.wag'],'constructor/parser/consumer traced; source values exactly match loaded float32','loaded Default definition; no mutation/reload cadence test',common+' Configuration, not measured acceleration or per-car damage. Scale is a separately loaded value; do not assume reciprocal recomputation. Earlier reference_car probe label was incorrect. Full range/default overrides and nonzero evaluation events untested.')
steam_fields={f['channel']:f for f in json.loads((ROOT/'steam-cab-fields.json').read_text(encoding='utf-8'))}
for row in rows:
    if row['id'].startswith('cab.') and row['id'][4:] in steam_fields:
        field=steam_fields[row['id'][4:]]
        row['extraction']+=f"; steam-specific source: {field['base']}+{field['offset']:#x}; {field['display']}"
        row['evidence'].extend(['STEAM-CAB-FINDINGS.md','steam-cab-fields.json','steam-cab-source-audit.json','pass90-byte-verification.json','captures/steam-probe-diesel-guard-01/steam.json','steam-runtime-summary.json','captures/steam-scotsman-baseline-01/steam.json','captures/steam-scotsman-final-paused-01/steam.json'])
        row['limitations']+=' Steam offsets require player control type1 (cab-view type3 is a different enum). Positive Scotsman reads and selected control/pressure transitions are recorded in steam-runtime-summary.json; constant channels are not actuator validation. Engine-union offsets overlap diesel fields; no independent AI steam controls established.'
camera_fields=[
    ('mode','Player view mode raw enum','uint32','observed 0 cab, 1 front exterior, 2 rear exterior, 3 trackside; others unresolved','[[0x7c2a88]+0x11c]'),
    ('tracking','Player camera tracking state used by native debug display','uint32','zero/nonzero; only interpreted for mode 1, 2 or 3','[[0x7c2a88]+0x110]'),
    ('render_position','Current render-camera position','float32[3]','native local scene coordinates; origin shifts apply','[0x829224] +0x30/+0x34/+0x38'),
    ('render_basis','Current render-camera basis vectors','float32[3][3]','dimensionless native basis; axis conventions need camera-transition validation','[0x829224] +0x0c/+0x18/+0x24')]
for name,meaning,typ,units,method in camera_fields:
    add('camera.'+name,meaning,'current player view/render scene; not independent AI viewpoints',typ,units,method,['CAMERA-FINDINGS.md','camera-transition-summary.json','captures/camera-final-paused-01/consist-check.json','captures/camera-paused-01/camera.json','pass61/004918e0.asm','pass62/006c0290.asm','pass62/006b63c0.asm','pass61-byte-verification.json','pass62-byte-verification.json'],'native consumers traced; cab/front/rear/trackside/cab switches observed with matching post-input snapshots','view/render update; paused values may retain last rendered frame',common+' View-state and render-camera pointers are distinct. Other mode names, transition timing, projection lifecycle and train-relative camera attachment remain unresolved. Stable pointer/time checks do not make external reads atomic.')
firebox_evidence=['STEAM-CAB-FINDINGS.md','steam-firebox-labels.json','pass91-byte-verification.json','pass82-byte-verification.json','pass82/0060997a.asm','pass91/0041f05c.asm','captures/steam-firebox-paused-01/steam.json']
for name,meaning,unit,method,cadence in [
 ('fire_temperature','Native fire temperature','unresolved native temperature unit','steam lead+0x2c2','dynamic; producer cadence unresolved'),
 ('fire_mass','Current fire mass','lb per native debug label and asset convention','steam lead+0x2ca','dynamic; producer cadence unresolved'),
 ('ideal_fire_mass','Loaded ideal fire mass','lb','[steam lead+0x29a]+0x242','loaded locomotive definition parameter'),
 ('maximum_fire_mass','Loaded maximum fire mass','lb','[steam lead+0x29a]+0x222','loaded locomotive definition parameter')]:
    add('steam.'+name,meaning,'steam player locomotive; AI untested','float32',unit,method,firebox_evidence,'native debug labels and cab consumer traced; positive Scotsman snapshot',''+cadence,common+' Require steam control type1 before interpreting engine union. Loaded definition parameters are not independent dynamic state. Temperature units and physical producer laws remain unresolved; FIREBOX graphic is a separate compound candidate.')
steam_debug_evidence=['STEAM-DEBUG-FINDINGS.md','steam-debug-fields.json','pass82/0060997a.asm','pass82-byte-verification.json','captures/steam-debug-paused-01/steam-debug.json']
for f in json.loads((ROOT/'steam-debug-fields.json').read_text(encoding='utf-8')):
    add('steam.'+f['name'],'Native steam debug '+f['name'].replace('_',' '),'steam player locomotive; AI untested','bool' if f['mask'] else 'float32',f['units'],f"{f['base']}+{f['offset']:#x}"+(f" & {f['mask']:#x}" if f['mask'] else ''),steam_debug_evidence,'native debug label and source traced; positive paused read only','loaded definition' if f['base']=='engine_definition' else 'simulation state; producer cadence unresolved',common+' Native labels do not establish update laws, rate timebase or physical correctness. Coal-burn line has inconsistent first argument; maximum rate may be inactive/stale. See steam debug findings.')
for row in rows:
    if row['id'] in ('cab.TENDER_WATER','cab.STEAM_PR','cab.STEAMCHEST_PR','cab.STEAMHEAT_PRESSURE'):
        row['evidence'].extend(steam_debug_evidence)
        row['limitations']+=' Native steam debug labels identify tender water as lb and the three pressures as PSI; cab volume conversion does not change raw mass units.'
for row in rows:
    if row['id'] in ('steam.generation_rate','steam.usage_rate','steam.usage_exceeds_exhaust_limit','cab.STEAM_PR'):
        row['evidence'].extend(['STEAM-PRODUCER-FINDINGS.md','pass92/00604450.asm','pass93/0060384a.asm','pass93/00603340.asm','pass92-byte-verification.json','pass93-byte-verification.json'])
        row['limitations']+=' Producer tracing shows generation can retain its prior value on a low-water path. Pressure integration divides the rate difference by3600 but rate timebase is not fully verified. Exhaust warning bit0x100 compares cylinder rate with definition+216.'
update_evidence=['STEAM-PRODUCER-FINDINGS.md','pass94/0060435c.asm','pass95/00603691.asm','pass95/0060392e.asm','pass96/00607bd0.asm','pass94-byte-verification.json','pass95-byte-verification.json','pass96-byte-verification.json','captures/steam-update-paused-01/steam-debug.json']
for name,meaning,typ,unit,method in [
 ('train.engine_update_accumulator','Pending engine-update time accumulator','float32','native time unit; upstream seconds confirmation pending','train+0x8a'),
 ('train.engine_update_interval','Configured engine-update interval','float32','native time unit; 0.25 observed','train+0x8e'),
 ('steam.injector1_working','Injector 1 working branch state','uint32','0/1','steam lead+0x2ee'),
 ('steam.injector2_working','Injector 2 working branch state','uint32','0/1','steam lead+0x2f2')]:
    add(name,meaning,'player steam tested; other engines/AI untested',typ,unit,method,update_evidence,'native producer/scheduler traced; positive paused read only','engine-update scheduler; skipped branches can retain old state',common+' Injector working is distinct from control position and flow. No working transition tested. Scheduler drains accumulator only while strictly greater than interval; upstream timebase remains open.')
for row in rows:
    if row['id'] in ('steam.coal_burn_rate_raw','steam.usage_rate'):
        row['evidence'].extend(update_evidence)
        row['limitations']+=' Coal mass update subtracts interval*burn/3600; water mass subtracts interval*usage/3600*0.7. Upstream interval timebase still needs closure.'
for row in rows:
    if row['id'] in ('steam.coal_burn_rate_raw','train.engine_update_accumulator','train.engine_update_interval'):
        row['units']='lb/hour; native producer and stationary live mass balance' if row['id']=='steam.coal_burn_rate_raw' else 'seconds; current-installation cadence corroborated'
        row['evidence'].extend(['steam-cadence-summary.json','steam-cadence-mass-checks.json','captures/steam-cadence-01/samples.jsonl','captures/steam-cadence-final-paused-01/steam.json','pass97-byte-verification.json','pass98-byte-verification.json'])
        row['limitations']+=' Subsequent cadence test corroborates seconds and coal lb/hour for this player steam session; prior upstream-timebase caveat is narrowed by this runtime evidence. No stock or AI cadence claim.'
electric_fields={f['channel']:f for f in json.loads((ROOT/'electric-cab-fields.json').read_text(encoding='utf-8'))}
for row in rows:
    if row['id'].startswith('cab.') and row['id'][4:] in electric_fields:
        f=electric_fields[row['id'][4:]]
        row['extraction']+=f"; electric raw source: {f['base']}+{f['offset']:#x} ({f['type']})"
        row['evidence'].extend(['ELECTRIC-CAB-FINDINGS.md','electric-cab-fields.json','pass102-byte-verification.json','captures/electric-probe-steam-guard-01/electric.json'])
        row['limitations']+=' Electric probe requires player control type3; Acela positive reads and selected pantograph/reverser/throttle transitions are recorded in electric-runtime-summary.json; unactuated fields are not actuator validation. Cab-view type1 is a different enum. Shared source channels are not independent physical values.'
    if row['id'] in ('cab.LINE_VOLTAGE','cab.CAB_SWITCH'):
        row['evidence'].extend(['ELECTRIC-CAB-FINDINGS.md','pass102-byte-verification.json','pass103-byte-verification.json'])
        row['limitations']+=' Electric voltage helper changes the return address, bypassing the apparent float comparison; CAB_SWITCH electric mapping yields an invalid out-of-image destination, not a supported branch. See electric findings.'
for row in rows:
    if row['id'].startswith('cab.') and row['id'][4:] in electric_fields:
        row['evidence'].extend(['electric-runtime-summary.json','captures/electric-acela-baseline-01/electric.json','captures/electric-acela-pantograph-down-01/electric.json','captures/electric-acela-forward-01/electric.json','captures/electric-acela-throttle-01/electric.json','captures/electric-acela-final-paused-01/electric.json'])
    if row['id']=='cab.LINE_VOLTAGE':
        row['evidence'].extend(['pass104-byte-verification.json','pass104/0040bad4.asm','electric-runtime-summary.json'])
        row['limitations']+=' Final helper semantics are traced in electric findings; its animation-object physical meaning remains unresolved. Acela route source stays25000 with pantograph control down.'
voltage_evidence=['ELECTRIC-CAB-FINDINGS.md','electric-voltage-summary.json','pass102-byte-verification.json','pass103-byte-verification.json','pass104-byte-verification.json','captures/electric-voltage-up-paused-01/voltage.json','captures/electric-voltage-transition-01/samples.jsonl','captures/electric-voltage-restored-paused-01/voltage.json']
for name,meaning,typ,unit,method in [
 ('electric.route_voltage','Loaded route supply voltage source','float32','volts; native cab unit0x17 divides by1000','[0x7b8d3c]+0x58'),
 ('electric.voltage_gate_enabled','Native electric voltage-display gate enabled setting','uint32','zero/nonzero','electric controller+0x258'),
 ('electric.voltage_consist_condition','Consist condition used by patched native voltage display helper','derived boolean','true/false; unavailable when skipped or invalid','bounded lead then+a8 traversal; car flags80/84 and helper0040bad4 indirect value/bounds; see read_electric_voltage.py')]:
    add(name,meaning,'electric player tested; other contexts untested',typ,unit,method,voltage_evidence,'native display consumers traced; Acela pantograph-down transition and separate restored snapshot','raw route source is configuration; derived condition follows flags/animation and can lag control',common+' Not measured traction power or independent overhead contact. Derived helper result is not a direct cab value; precision and non-atomic traversal limits apply.')
for row in rows:
    if row['id']=='cab.LINE_VOLTAGE':
        row['evidence'].extend(voltage_evidence)
        row['extraction']+='; derived native display value uses loaded route voltage, gate-enable setting and bounded consist condition; see read_electric_voltage.py'
        row['limitations']+=' Acela transition observes delayed derived gate off after pantograph command; restored paused condition seen separately, not timed return latency.'
traction_evidence=['ELECTRIC-TRACTION-FINDINGS.md','pass107-byte-verification.json','pass108-byte-verification.json','pass109-byte-verification.json','pass110-byte-verification.json','electric-traction-summary.json','captures/electric-traction-paused-01/traction.json','captures/electric-traction-braked-01/traction.json','captures/electric-traction-down-running-01/traction.json','captures/electric-traction-down-idle-01/traction.json','captures/electric-traction-down-voltage-01/voltage.json','captures/electric-traction-restored-idle-01/traction.json','electric-moving-summary.json','captures/electric-moving-01/samples.jsonl','captures/electric-coasting-paused-01/traction.json','pass134-byte-verification.json','captures/shared-force-paused-01/shared-force.json','pass135-byte-verification.json','electric-powered-distribution-summary.json','captures/electric-powered-distribution-01/samples.jsonl','captures/shared-force-paired-final-01/shared-force.json']
for name,meaning,typ,unit,method in [
 ('electric.traction_calculation_gate','Sampled bit used inside electric traction calculation; not a reliable cache freshness indicator','bit','boolean','electric lead+0x296 bit0x2'),
 ('electric.cached_force_limit','Cached electric speed-dependent force calculation limit','float32','native force-like units; mapping not independently validated','electric lead+0x496'),
 ('electric.cached_throttle','Throttle copied during enabled electric force calculation','float32','native controller fraction','electric lead+0x492')]:
    add(name,meaning,'electric player; AI untested',typ,unit,method,traction_evidence,'native producers traced; stationary controls/stale-cache observations plus released-brake low-speed movement','engine update; cached fields not refreshed on gate-false branch',common+' Not delivered wheel force or overhead contact. Cached throttle remained2.5% at idle with pantograph down despite sampled gate bit true; do not use bit alone to claim freshness. Low forward movement observed to0.414m/s; cached limit changes with speed and outputs settle to zero at idle while coasting. Higher-speed/reverse behavior and optional modifier actuation untested. Shared helper tests car102 separately from definition102; current paused ramp predicate false. Downstream per-powered-car force can be altered after current calculation; see shared-force assembly findings. Rear Acela receives matching nonzero shared force/power with bit2 clear and current field0; lead current/gate semantics cannot be extended to followers.')
event_evidence=['ELECTRIC-EVENT-FINDINGS.md','pass112-byte-verification.json','pass113-byte-verification.json','pass114-byte-verification.json','pass115-byte-verification.json','captures/electric-event-values-paused-01/event-routes.json']
for name,meaning,typ,unit,offset in [
 ('event.receiver_mask_1_32','Retained receiver event bits for ordinary event IDs1..32','uint32 bitmask','event presence bits',0x20),
 ('event.receiver_mask_33_64','Retained receiver event bits for ordinary event IDs33..64','uint32 bitmask','event presence bits',0x24),
 ('event.receiver_scalar1','Receiver retained scalar variable1','float32','native scalar; producer transformations unresolved',0x28),
 ('event.receiver_scalar2','Receiver retained scalar variable2','float32','native scalar; producer transformations unresolved',0x2c),
 ('event.receiver_scalar3','Receiver retained scalar variable3','float32','native scalar; physical meaning unresolved',0x30)]:
    add(name,meaning,'two electric player receivers observed; other player and AI contexts untested',typ,unit,f'resolve lead+4b6 or+25c handle through[828108], then receiver+{offset:x}',event_evidence,'native receiver stores traced; stable paused Acela read','set by event/scalar dispatch; consumer/clearing/lifecycle untraced',common+' Event masks coalesce repeats, have no ordering/timestamps/counts and may alias out-of-range IDs. Not a complete event history. Scalar baseline zero only; units, modified producer paths and nonzero runtime transitions remain open.')
for row in rows:
    if row['id'].startswith('event.receiver_'):
        row['evidence'].extend(['pass116-byte-verification.json','pass117-byte-verification.json','electric-event-helper-table.json','captures/electric-event-throttle-paused-01/event-routes.json','captures/electric-event-source-paused-01/traction.json','captures/electric-event-idle-restored-01/event-routes.json'])
        row['evidence'].extend([f'pass{i}-byte-verification.json' for i in range(118,124)]+['event-receiver-references/references.tsv','event-class-references/references.tsv','event-update-references/references.tsv'])
    if row['id']=='event.receiver_scalar1':
        row['units']='throttle percent for tested electric producer; other producers unverified'
        row['evidence_status']='electric broadcast producer traced; both lead receiver values0->2.5->0 match throttle actuation'
        row['limitations']=common+' Nonzero electric scalar1 validated only. Receivers can retain values if broadcast filter skips their car. Other engine types, consumers and AI untested; not actual force or power.'
processing_evidence=['ELECTRIC-EVENT-FINDINGS.md','pass124-byte-verification.json','captures/electric-event-processing-paused-01/event-routes.json','captures/electric-event-processing-paused-02/event-routes.json']
for row in rows:
    if row['id'].startswith('event.receiver_'):
        row['evidence'].extend(processing_evidence)
        row['update_or_lifecycle']='receiver processing can continue while simulation paused; selected event bits cleared, scalars copied to previous fields unless flags1c bit0x200; no measured cadence'
        row['limitations']=row['limitations'].replace('consumers and AI untested','full consumer action semantics and AI untested').replace('consumers and AI','full consumer action semantics and AI')
for name,meaning,typ,unit,offset in [
 ('event.receiver_previous_scalar1','Scalar1 retained at previous completed normal receiver processing','float32','electric throttle percent in tested producer',0x3c),
 ('event.receiver_previous_scalar2','Scalar2 retained at previous completed normal receiver processing','float32','same units as receiver scalar2; unresolved',0x40),
 ('event.receiver_previous_scalar3','Scalar3 retained at previous completed normal receiver processing','float32','same units as receiver scalar3; unresolved',0x44),
 ('event.receiver_last_processing_tick','Windows tick saved by normal receiver processing','uint32','milliseconds of Windows uptime modulo2^32',0x50)]:
    add(name,meaning,'two electric player receivers observed; AI and other contexts untested',typ,unit,f'receiver+0x{offset:x}; resolve handles as read_electric_event_routes.py',processing_evidence,'native processing stores traced; paused tick advances with unchanged simulation time','normal receiver processing; skipped in flags1c bit0x200 path; not physics cadence',common+' Non-atomic reads. Scalar previous values validated at zero only. Tick is not simulation time or event timestamp; wraparound and cadence not validated. Normal pass timestamp does not prove every stream processed or sound played.')
receiver_list_evidence=['RECEIVER-LIST-FINDINGS.md','pass120-byte-verification.json','pass123-byte-verification.json','pass124-byte-verification.json','captures/receiver-list-paused-01/receivers.json','captures/receiver-list-labels-paused-01/receivers.json']
for name,meaning,typ,unit,method in [
 ('event.receiver_list','Native processing-list receiver identities and physical-car handle matches','bounded object list','handles/pointers; session scoped','sentinel=[[7c32f0]+14a]; node next+0 receiver+8; verify receiver+4 in registry'),
 ('event.receiver_definition_label','Loaded receiver definition label','UTF16 string','text; not a unique identity','[[[receiver+10]+4]+4]; bounded512 code units'),
 ('event.receiver_stream_count','Loaded definition stream count','uint32','declared streams, not audible count','[receiver+10]+10'),
 ('event.receiver_trigger_state_slots','Loaded definition indexed trigger-state allocation count','uint32','four-byte state slots, not event count','[receiver+10]+0c')]:
    add(name,meaning,'session receiver list;9 player-associated and11 unassociated observed; AI untested',typ,unit,method,receiver_list_evidence,'native traversal/allocation/label sources traced;20 live receivers with48 streams','list changes with receiver lifecycle; metadata loaded with definitions; cadence unmeasured',common+' Non-atomic. Probe bounds are not native capacities.11 unassociated receivers are not assumed AI or environmental. Duplicate labels exist; paths and owner semantics not inferred. Declared stream/state counts do not prove playback.')
distance_evidence=['RECEIVER-LIST-FINDINGS.md','pass125-byte-verification.json','pass126-byte-verification.json','receiver-distance-summary.json','captures/receiver-distance-paused-01/receivers.json']
for name,meaning,typ,unit,method in [
 ('event.receiver_position','Receiver position used by audio distance calculation','float32 vector3','native coordinates; unit/origin unverified','receiver+58/+5c/+60'),
 ('event.listener_position','Listener position used by receiver distance calculation','float32 vector3','native coordinates; unit/origin unverified','[7c32f0]+14e/+152/+156'),
 ('event.receiver_squared_distance','Stored squared receiver-to-listener separation','float32','native coordinate units squared','receiver+38; update skipped when flags1c bit4 set'),
 ('event.receiver_activation_distance_threshold','Loaded activation squared-distance threshold','float32','native coordinate units squared; compare only when activation flag8 set','[receiver+10]+1c; flags at definition+18'),
 ('event.receiver_deactivation_distance_threshold','Loaded deactivation squared-distance threshold','float32','native coordinate units squared; compare only when deactivation flag10hex set','[receiver+10]+28; flags at definition+24')]:
    add(name,meaning,'session receivers; player-associated and unassociated observed; AI untested',typ,unit,method,distance_evidence,'vector producer traced;19 non-skipped live distance comparisons,13 exact; Acela threshold/file correspondence','audio processing independent of paused simulation; thresholds are loaded configuration',common+' Not linear distance. Skip-flag receiver retains0 despite nonzero separation. Coordinate origin/units, moving accuracy and scalability selection remain unverified. Zero disabled threshold is not zero range.')
camera_receiver_evidence=['RECEIVER-LIST-FINDINGS.md','pass127-byte-verification.json','receiver-camera-summary.json','captures/receiver-external-camera-01/receivers.json','captures/receiver-cab-restored-01/receivers.json']
add('event.receiver_inactive_condition','Receiver inactive-condition bit selected by camera/distance conditions','session receiver list; player and unassociated sources tested; AI untested','bit','boolean','receiver+1c bit0x2',camera_receiver_evidence,'set/clear native writers traced;12 of20 flags change during cab/external/cab and all20 restore','audio condition processing; changes while receivers remain registered',common+' Not actual playback or audibility. Triggers may still be examined while inactive. Camera and distance changed together; separated snapshots do not measure latency.')
brake_event_evidence=['VEHICLE-SYSTEM-FINDINGS.md','pass128-byte-verification.json','pass129-byte-verification.json','pass130-byte-verification.json','captures/brake-reference-paused-01/brakes.json','pass131-byte-verification.json','brake-adjustments-summary.json','captures/brake-adjustments-01/samples.jsonl','captures/brake-adjustments-paused-02/brakes.json']
for name,meaning,typ,unit,method in [
 ('event.brake_pressure_reference','Retained cylinder-pressure reference for brake sound events','float32','PSI','car+268; producer005dcdab requires locomotive context equal player lead'),
 ('event.brake_pressure_rise_latch','Latch suppressing repeated rising-pressure sound events','uint32','boolean-like 0/1','car+26c'),
 ('event.brake_pressure_fall_latch','Latch suppressing repeated falling-pressure sound events','uint32','boolean-like 0/1','car+270'),
 ('event.brake_pressure_rise_timer','Shared rising-pressure event timer','float32','simulation time units; nominal seconds','global80a1f0'),
 ('event.brake_pressure_fall_timer','Shared falling-pressure event timer','float32','simulation time units; nominal seconds','global80a1ec')]:
    add(name,meaning,'player-gated producer; lead reference observed, follower references zero; AI unvalidated',typ,unit,method,brake_event_evidence,'native producer and caller traced; eight-car series; lead rising latch and reference transition observed','brake update path; timers decremented by train+8e, exact invocation cadence unmeasured',common+' Reference updates only beyond absolute1 PSI difference; not previous-frame pressure. Shared timers are not per-car timestamps. Inactive/unmaintained fields can retain zero; non-atomic snapshot. Rising latch observed0/1 and timer0..1.25; falling latch/timer only zero. Reference can retain an intermediate pressure missed by50ms sampling.')
brake_map=json.loads((ROOT/'brake-parameter-map.json').read_text(encoding='utf-8'))
for entry in brake_map['entries']:
    for row in rows:
        if row['id'] in ('config..eng:Wagon.'+entry['label'],'config..wag:Wagon.'+entry['label']):
            row['extraction']+=' Loaded vehicle definition: [car+94]+'+entry['definition_offset']+'; token'+entry['token']+' parser branch'+entry['parser_target']+'.'
            row['evidence']+=['brake-parameter-map.json','VEHICLE-SYSTEM-FINDINGS.md']
            row['evidence_status']+='; native token/destination mapped and Acela loaded values read'
            row['limitations']+=' Loaded parameters can be defaults and are not current reservoir pressures; branch applicability differs by brake type.'
for name,meaning,offset in [('car.auxiliary_reservoir_pressure','Current distributor auxiliary-reservoir pressure',0x224),('car.emergency_reservoir_pressure','Current distributor emergency-reservoir pressure',0x228)]:
    add(name,meaning,'eight player Acela cars observed; AI and other brake types unvalidated','float32','PSI in tested distributor model',f'car+{offset:#x}; distinguish loaded definition998/99c',['VEHICLE-SYSTEM-FINDINGS.md','brake-parameter-map.json','pass131-byte-verification.json','pass58-byte-verification.json'],'native reservoir consumers and configuration limits traced; live paused values read','brake update replenishment/application branches; independent cadence unmeasured',common+' Other brake types may reuse these fields differently. car234 supplying these reservoirs is not yet semantically named. Unit conversion and release/AI transitions untested.')
for name,meaning,typ,units,offset in [
 ('brake.train_selected_mode','Selected train brake controller mode after loaded-range lookup','uint32','native mode code',0x3f2),
 ('brake.train_selected_fraction','Within-mode train brake controller fraction','float32','mode-relative fraction; not whole-handle percent',0x3f6)]:
    add(name,meaning,'electric Acela player lead observed; AI and other types unvalidated',typ,units,f'player lead+{offset:#x}; producer005d857d, engine definition452 ranges',['VEHICLE-SYSTEM-FINDINGS.md','pass133-byte-verification.json','captures/brake-selector-paused-01/selector.json','brake-release-attempt-summary.json','captures/brake-release-01/samples.jsonl'],'native caller/selector traced; paused loaded-range reconstruction matches stored1000hex mode','brake controller update; precedes pressure updater005d8db0',common+' Discrete codes depend on native selector semantics; installed Acela labels corroborate six enabled ranges only. Continuous-curve branch unvalidated. Holding-mode fraction is distinct from raw handle value. No mode transition achieved in release attempt;1000hex holding persists, and pipe pressure does not refill after a handle decrement. Immediate command and selector reads can reflect different producer phases.')
release_evidence=['brake-release-summary.json','captures/brake-release-02/samples.jsonl','captures/brake-release-settling-01/samples.jsonl','captures/brake-released-paused-01/brakes.json']
for row in rows:
    if row['id'] in {'car.brake_cylinder_pressure','car.brake_pipe_pressure','car.brake_force_candidate','event.brake_pressure_reference','event.brake_pressure_fall_latch','event.brake_pressure_fall_timer','brake.train_selected_mode','brake.train_selected_fraction'}:
        row['evidence']+=release_evidence
        row['evidence_status']+='; subsequent Acela release-mode transition observed, eight cars settled cylinder0/pipe110 PSI; falling latch0/1 and timer0..1.5'
        row['limitations']=row['limitations'].replace('falling latch/timer only zero.','falling latch/timer subsequently observed active during release.').replace('No mode transition achieved in release attempt;1000hex holding persists, and pipe pressure does not refill after a handle decrement.','Initial release attempt stayed in holding; subsequent keyboard sequence crossed hold-lapped and release modes. Holding decrement alone does not refill pipe.')
        row['limitations']+=' Release and settling captures have a12.93s simulation gap: exact time-to-zero and physical propagation speed unmeasured. Sound reference retains0.947PSI at actual pressure0; AI remains unvalidated.'
for row in rows:
    if row['id'] in {'car.brake_cylinder_pressure','car.brake_pipe_pressure','car.brake_force_candidate','car.stored_velocity','car.stored_acceleration'}:
        row['evidence']+=['AI-SYSTEM-UPDATE-FINDINGS.md','pass137/005f9285.asm','pass137-byte-verification.json','pass138-byte-verification.json']
        row['limitations']+=' Traced engine/brake scheduler call005f947f explicitly loads player train from007c2ac0; it does not establish AI field refresh. Separate AI service motion and follower copies do not prove independent AI brake/force simulation; alternate writers remain open.'
        row['evidence']+=['ai-systems-moving-02-summary.json','captures/ai-systems-moving-02/samples.jsonl','captures/ai-systems-alert-final-01/samples.jsonl']
        row['limitations']+=' AI400005 moving observation retains zero cylinder/brake-force/stored acceleration while service speed changes; reservoir/pipe fields remain90. Includes failure-alert paused tail and flagged unstable car reads; stable subset corroborates zeros. Not proof of absent AI braking or universal stale fields.'
for row in rows:
    if row['id'] in {'service.speed','service.target_speed','service.acceleration','service.integration_interval','service.last_update_time'}:
        row['evidence']+=['AI-SYSTEM-UPDATE-FINDINGS.md','ai-acceleration-summary.json','pass139-byte-verification.json']
        row['evidence_status']+=';47 consecutive positive-sign one-second AI service integration predictions match float32 stored speed exactly'
        row['limitations']+=' Service acceleration is target-capped kinematic input, not measured per-car acceleration; target may be reached in less than the integration interval. One sequential duplicate service read disagreed; no atomicity claim. Specific cause of observed sharp negative driver input remains unresolved.'
        if row['id']=='service.acceleration':row['meaning']='AI target-capped kinematic acceleration input'
efficiency_evidence=['SERVICE-EFFICIENCY-FINDINGS.md','pass142-byte-verification.json','pass143-byte-verification.json','captures/service-efficiency-paused-01/efficiency.json']
add('service.efficiency_baseline','Baseline source for effective service efficiency','player and loaded AI services','float32','dimensionless multiplier','service+204;005a6b1d copies into208 only when selected record+34 is null',efficiency_evidence,'native source selection traced; all three paused services baseline/effective0.75','loaded service state; baseline writer/reset not yet mapped',common+' Baseline asset-parser binding unresolved. Effective208 can instead come from selected-record+24. Installed baseline clamp approximately0.005..1; override bypasses this clamp. No boundary/override transition test.')
for row in rows:
    if row['id']=='service.efficiency_candidate':
        row['evidence']+=efficiency_evidence
        row['meaning']='Effective service speed and acceleration scaling multiplier'
        row['extraction']='service+208;005a6b1d selects baseline204 or [service34]+24; baseline branch installed clamp approximately0.005..1 via004069aa return rewrite'
        row['limitations']+=' Selected-record override bypasses baseline clamps; no universal0..1 guarantee. Baseline and effective values match0.75 in all three paused services; selected-record identity, override transition and asset-parser binding remain unresolved.'
add('service.ordered_operational_records','Ordered service records used by distance selector and efficiency override','player and loaded AI services; current three lists empty','list','native record identities and provisional fields','sentinel=[service+30]; circular nodes next0,record8;005a51ad selects record into service34;record24 overrides efficiency',['SERVICE-EFFICIENCY-FINDINGS.md','pass144-byte-verification.json','pass145-byte-verification.json','captures/service-records-paused-01/records.json'],'native enumeration/selector traced; empty lists read with stable sentinels','service lifetime and progress-dependent selection; record construction/reset unresolved',common+' No populated-record runtime validation. Record timestamp meanings and loader binding unknown. Geometry helper may leave outputs unwritten on failed lookups; do not assume zero. Not proof of complete timetable extraction.')
for row in rows:
    if row['id'] in {'service.efficiency_baseline','service.efficiency_candidate','service.ordered_operational_records'}:
        row['evidence']+=['service-token-map.json','pass147-byte-verification.json','pass148-byte-verification.json','pass149-byte-verification.json']
        row['evidence_status']+=';service loader binds Efficiency token40411 to baseline204;station-stop loader binds record0 PlatformStartID,14 DistanceDownPath,1c uint16 SkipCount'
        row['limitations']=row['limitations'].replace('Baseline asset-parser binding unresolved.','Baseline service-file binding traced; activity override merge remains unresolved.').replace('baseline writer/reset not yet mapped','constructor default and service parser traced; later reset paths incomplete')
        row['limitations']+=' Station-stop activity merge, populated runtime comparison and arrival/departure field offsets remain unvalidated.'
        if row['id']=='service.ordered_operational_records':row['meaning']='Ordered station-stop records used by distance selector and efficiency override'
for row in rows:
    if row['id'] in {'service.efficiency_baseline','service.efficiency_candidate','service.ordered_operational_records'}:
        row['evidence']+=['maryland-record-comparison.json','captures/maryland-records-paused-01/records.json','captures/maryland-efficiency-paused-01/efficiency.json']
        row['evidence_status']+=';Maryland player has two populated records matching platform/skip/efficiency declarations;first record selected'
        row['limitations']=row['limitations'].replace('No populated-record runtime validation.','Populated Maryland records sampled once; selection transition untested.').replace('populated runtime comparison and arrival/departure field offsets remain unvalidated.','arrival/departure semantics remain unvalidated despite numeric candidate matches.').replace('current three lists empty','grain lists empty; Maryland player list populated')
        row['limitations']+=' Live distance values differ slightly from asset declarations; no exact-copy assertion. Second-record efficiency0.289063 is populated but not yet observed as effective208.'
for name,meaning,offset in [('recorded_arrival','Recorded station arrival time; may be synthesized from schedule',8),('recorded_departure','Recorded station departure-related event time',0x10)]:
    add('station.'+name,meaning,'player station-stop records; AI writer applicability unvalidated','float32','day-clock seconds; zero/unset interpretation state-dependent',f'record+{offset:#x} in service30 station-stop list;player00586f58 writes clock80acd4',['STATION-TIME-FINDINGS.md','pass152-byte-verification.json','captures/maryland-records-paused-01/records.json','maryland-record-comparison.json'],'native player writes traced;two paused records sampled, no departure transition','station-state event writes; retained record values, not continuous clocks',common+' Arrival08 can copy scheduled04 under special branches; numeric equality does not prove observed arrival. Departure10 zero in both samples. No universal actual-time or AI semantics. Interpret with flags1e and activity state; complete flags/zero rules unresolved.')
for name,meaning,offset,token in [('scheduled_arrival','Scheduled station arrival time',4,'4040d ArrivalTime'),('scheduled_departure','Scheduled station departure time',0xc,'4040f DepartTime')]:
    add('station.'+name,meaning,'service station-stop records;Maryland player populated,AI schedule population untested','float32','day-clock seconds',f'record+{offset:#x};005a1656 parses {token};005a102e merges by platform/skip or distance fallback',['STATION-TIME-FINDINGS.md','pass153-byte-verification.json','station-schedule-dispatch.json','service-token-map.json','maryland-record-comparison.json'],'native label/parser/merge traced;two paused player records exactly match activity declarations','schedule loading and merge;later mutation/reset paths incomplete',common+' Not recorded arrival/departure. Merge fallback uses first matching platform and strict distance +/-1. Missing declaration,editing,time offsets and AI lifecycle unvalidated.')
station_transition_evidence=['STATION-TIME-FINDINGS.md','station-transition-summary.json','pass152-byte-verification.json','pass154-byte-verification.json','captures/maryland-station-wait-01/samples.jsonl','captures/maryland-station-departure-01/samples.jsonl']
for name,meaning,typ,units,source,status in [
 ('station.state_flags','Station record branch-local arrival, loading, departure and cue state','uint16 bitmask','raw flags; partial branch meanings','record+1e;player00586f58 and selection advance005a5254','live first-stop0x22->0x62 while stationary; departure remained unset'),
 ('station.boarding_active','Player activity boarding countdown active state','uint32','zero/nonzero','activity809810+370;00586f58','native set/clear traced; sampled zero only'),
 ('station.boarding_remaining','Player activity remaining boarding countdown','float32','simulation seconds by frame-delta subtraction','activity809810+374;00586f58 subtracts828fb4 while370 is nonzero','native initialization/decrement/clamp traced; sampled zero only')]:
    add(name,meaning,'player activity/station records;AI equivalence unvalidated',typ,units,source,station_transition_evidence,status,'frame-driven processing and station events; pause halts observed progression',common+' Only cue-state transition observed. No nonzero boarding timer or recorded departure transition. Flag0x40 is a dispatch-attempt latch, not proof of sound, permission to pass a signal or actual departure. Selected-record advancement clears this bit. Native exported caller00586293 has live patches; station processor00586f58, dispatcher0058ea72 and advance005a5254 match disk/live.')
for row in rows:
    if row['id'] in {'station.recorded_arrival','station.recorded_departure','station.scheduled_departure','service.ordered_operational_records'}:
        row['evidence']+=station_transition_evidence
        row['evidence_status']+=';stationary Maryland run crosses scheduled departure:flags0x22->0x62, recorded departure remains0 and selected first record unchanged'
        row['limitations']+=' Intended departure capture did not move the train; no actual departure or next-stop selection was validated.'
# Consolidated current semantics replace historical append-only caveats that have
# since been resolved. Raw captures and prior finding sections remain unchanged.
for row in rows:
    if row['id']=='service.efficiency_baseline':
        row['update_or_lifecycle']='constructor initializes0.75;service-file Efficiency token40411 writes204; later reset paths incomplete'
        row['limitations']=common+' Service-file baseline binding traced. Activity per-stop override uses a separate source. Effective208 can differ from baseline204. Installed baseline-selection branch clamps approximately0.005..1;selected-record override bypasses clamps. No clamp boundary, later reset or changed effective-override transition validated.'
    elif row['id']=='service.efficiency_candidate':
        row['units']='dimensionless multiplier'
        row['limitations']=common+' Selected-record override bypasses baseline clamps;no universal0..1 guarantee. First Maryland record is selected with effective0.75. Second-record0.289063 is populated but has not been observed as effective208. Baseline service parser is traced; complete activity efficiency merge and reset behavior remain unresolved. Per-field update cadence and changing override transitions remain unvalidated.'
    elif row['id']=='service.ordered_operational_records':
        row['applicability']='player and loaded AI services;Maryland player has two populated records;observed AI lists and grain lists empty'
        row['units']='ordered native record identities, platform IDs, schedule/event times and operational state'
        row['extraction']='sentinel=[service+30];circular nodes next0,record8;selected34,previous38;005a51ad distance selector;005a5254 advances using00690280;record24 overrides effective208'
        row['update_or_lifecycle']='service loading/path reconstruction/activity schedule merge;progress selection and explicit advance;full reset and AI-stop lifecycle unvalidated'
        row['limitations']=common+' Maryland populated records sampled while stationary;no live selection advance or departure. Scheduled4/c loader/merge and recorded8/10 player writers traced;arrival8 can be synthesized. Live distance14 differs slightly from file declarations and has a native geometry-rebuild path. Geometry helper may leave outputs unwritten on failed lookups. Successor returns null for empty,end or missing identity;null input selects first record. Thus null alone does not prove route completion. Complete timetable,AI populated stops,boarding countdown and second-record effective efficiency remain unvalidated.'
        row['evidence']+=['pass153-byte-verification.json','pass155-byte-verification.json','station-successor-model.json']
        row['evidence_status']+=';native identity-based successor and null/end behavior traced;offline boundary model uses captured record identities,not a live transition'
coupling_geometry_evidence=['COUPLING-GEOMETRY-FINDINGS.md','pass156-byte-verification.json','pass157-byte-verification.json','pass158-byte-verification.json','pass159-byte-verification.json','captures/coupling-geometry-paused-01/couplings.json']
for name,meaning,typ,units,method in [
 ('car.connection_endpoints','Native coupling-solver endpoint positions reconstructed from vehicle definition and body transform','derived vector3 pair','native world coordinates; metre scale inherited from body/vehicle length','00634b49 local(0,1-definition414,+/-0.5*definition400);005ad370/005aaa39 transform using bodyc..30'),
 ('car.connection_endpoint_distance','Nonnegative distance between current end0 and following end1 solver connection points','derived float','metres; not signed slack','car+a8 paired vehicle;norm(transformed following end1-current end0)')]:
    add(name,meaning,'physical player/AI vehicle structure;paused9-car player sampled;AI not populated in this capture',typ,units,method,coupling_geometry_evidence,'native geometry path traced;8paused connections reconstructed at approximately0.14942..0.15048m','derived from body/definition state at sampling time;moving cadence and solver phase unvalidated',common+' Python double-precision reconstruction is not bit-exact native float/x87 arithmetic. Body buffers may swap. End0/1 are solver identities,not universal vehicle front/rear. Distance is not signed slack,force or spring extension. Definition414 asset meaning and physical AI transitions remain unvalidated.')
for row in rows:
    if row['id']=='car.connection_force_candidate':
        row['meaning']='Stored magnitude for current-to-following vehicle connection force'
        row['evidence']+=coupling_geometry_evidence
        row['limitations']+=' Native writer takes a vector norm;do not label this a signed tension/compression force. Opposite connection is read through preceding car1a0. Native writer entry is live-patched;solver phase and wrappers remain relevant. Endpoint-distance reconstruction does not validate numerical force equality.'
coupling_velocity_evidence=['COUPLING-GEOMETRY-FINDINGS.md','pass160b-byte-verification.json','pass161-byte-verification.json','captures/coupling-velocity-paused-01/couplings.json']
for name,meaning,typ,method in [
 ('car.connection_endpoint_velocity','Connection endpoint velocity including body rotation','derived vector3 pair','005e17a0:body88 + cross(body94,endpoint-body30)'),
 ('car.connection_separation_rate','Signed rate of separation of connected solver endpoints','derived float','0062d335:dot(following endpoint velocity-current endpoint velocity,unit(following endpoint-current endpoint));zero direction below native epsilon')]:
    add(name,meaning,'physical player/AI structure;paused9-car player read;AI dynamic applicability unvalidated',typ,'m/s',method,coupling_velocity_evidence,'native vector helpers traced;8paused pairs yield near-zero residual rates,all angular velocity zero','derived from instantaneous body-state read;cadence/solver phase and moving behavior unvalidated',common+' Double-precision external reconstruction,not bit-exact float/x87. No meaningful nonzero angular or opening/closing transition observed. Positive scalar denotes opening geometrically;it is not signed force,slack or proof of visible motion. Native epsilon read live only in this pass. Body buffer swaps and asynchronous reads limit dynamic correlation.')
for row in rows:
    if row['id'] in {'body.velocity','body.angular_velocity','car.longitudinal_speed','car.speed_magnitude','car.connection_endpoint_velocity','car.connection_separation_rate'}:
        row['evidence']+=['MOTION-DIFFERENCE-FINDINGS.md','motion-difference-summary.json']
        row['evidence_status']+=';preserved moving player/AI observations reveal orientation changes with zero stored angular velocity and nonzero position/velocity discrepancies'
        row['limitations']+=' Stored body velocity/angular velocity are not universally demonstrated derivatives of track-following position/orientation. Same-clock samples retain discrepancies. Endpoint-velocity formula reconstructs native stored-state calculation,not necessarily actual trajectory velocity;captures lack definition400/414 for endpoint finite differences. Causes remain unresolved;no correction factor justified.'
        if row['id']=='body.angular_velocity':row['meaning']='Stored physics-body angular velocity;not universal track-orientation derivative'
        if row['id']=='body.velocity':row['meaning']='Stored physics-body linear velocity vector'
for row in rows:
    if row['id'] in {'body.velocity','body.angular_velocity','car.connection_endpoint_velocity','car.connection_separation_rate'}:
        row['evidence']+=['pass162-byte-verification.json','angular-reset-provenance.json']
        row['limitations']+=' AI005a7337/00636475 can rebuild track placement via00628d09,clear angular momentum and calculate body94 from body64*body58;therefore turning track geometry need not yield nonzero stored angular velocity. Substituting archived wall time does not resolve the player position/velocity discrepancy. No universal player-path explanation or timing correction inferred.'
payload=dict(generated_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='WORK IN PROGRESS; discovery inventory, no priorities or keep/drop decisions',
             scope='Runtime probes plus installed cab/rolling-stock and preferred-activity direct node declarations. Not comprehensive completion.',
             counts=dict(runtime_direct=sum(not r['id'].startswith(('cab.','config.')) and not r['value_type'].startswith('derived') for r in rows),runtime_derived=sum(r['value_type'].startswith('derived') for r in rows),cab_channels=len(native['channels']),installed_cab_channels=len(cab),config_paths=len(param),config_leaf_paths=len(leaf_paths),config_mixed_paths=len(mixed_paths),files_scanned=len(scanned),total=len(rows)),
             executable_assumption=common,data_points=rows)
(ROOT/'inventory.json').write_text(json.dumps(payload,indent=2))
(ROOT/'source-manifest.json').write_text(json.dumps(sources,indent=2))
lines=['# Telemetry discovery inventory (work in progress)','',str(payload['counts']),'','No priorities or keep/drop decisions. See inventory.json for full provenance and per-field limitations.','','| Candidate | Meaning | Evidence status |','|---|---|---|']
for row in rows:lines.append('| '+row['id'].replace('|','/')+' | '+row['meaning'].replace('|','/')+' | '+row['evidence_status']+' |')
(ROOT/'INVENTORY.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(payload['counts']))
