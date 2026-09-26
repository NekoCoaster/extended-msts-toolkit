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
        limits+=' Only diesel live-validated in this phase; steam/electric offsets are inherited candidates.'
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
        add('evaluation.'+prefix+'_'+suffix,meaning,'player consist evaluation; not AI telemetry',typ,units,method,['EVALUATION-FINDINGS.md','captures/evaluation-paused-03/evaluation.json','vehicle-condition-labels.json','pass75/00586666.asm','pass74/0043bc16.asm','pass74-byte-verification.json','pass75-byte-verification.json'],'native collector and installed display labels traced; empty paused lists read, no exceedance emission observed','shared30-second interval after either kind records; both disabled at either count40',common+' Sampled evaluation records, not complete event history or measured physical damage. No vehicle ID in records. Condition compares loaded Durability with a threshold derived from stored acceleration; see VEHICLE-MOTION-EVALUATION.md. Reference threshold initialization unresolved. Freight branch takes precedence over passenger-bearing definition. Marker conversion and reset lifecycle unvalidated.')
for name,meaning,unit,method in [('stored_velocity','Native stored car signed speed','m/s','car+0x1bc;0062924c signed magnitude of physics velocity; derailed branch unsigned'),('stored_acceleration','Native stored car signed acceleration','m/s squared','car+0x1c0;0062924c signed force magnitude times inverse mass; derailed branch unsigned'),('loaded_durability','Durability copied from service/consist definition','native dimensionless scalar','car+0x28e copied from definition+0xa0 by005a7821/005a7a5f; token4028c Durability')]:
    add('car.'+name,meaning,'physical player and AI cars; fresh validation player only','float32',unit,method,['VEHICLE-MOTION-EVALUATION.md','vehicle-evaluation-labels.json','captures/vehicle-evaluation-paused-02/snapshot.json','pass81-byte-verification.json','pass82-byte-verification.json','pass83-byte-verification.json'],'native producers/display/parser traced;23 stopped player cars read; moving and AI behavior untested','motion physics update with branch gates; Durability copied during creation, later writers not exhaustively excluded',common+' Stored signed magnitude is not longitudinal projection or finite-difference acceleration. Derailment changes sign semantics; skip flag and body swaps matter. Durability is loaded configuration, not damage. One debug call differs live outside relevant display instructions; exact-image offsets only.')
camera_fields=[
    ('mode','Player view mode raw enum','uint32','observed 0 cab, 1 front exterior, 2 rear exterior, 3 trackside; others unresolved','[[0x7c2a88]+0x11c]'),
    ('tracking','Player camera tracking state used by native debug display','uint32','zero/nonzero; only interpreted for mode 1, 2 or 3','[[0x7c2a88]+0x110]'),
    ('render_position','Current render-camera position','float32[3]','native local scene coordinates; origin shifts apply','[0x829224] +0x30/+0x34/+0x38'),
    ('render_basis','Current render-camera basis vectors','float32[3][3]','dimensionless native basis; axis conventions need camera-transition validation','[0x829224] +0x0c/+0x18/+0x24')]
for name,meaning,typ,units,method in camera_fields:
    add('camera.'+name,meaning,'current player view/render scene; not independent AI viewpoints',typ,units,method,['CAMERA-FINDINGS.md','camera-transition-summary.json','captures/camera-final-paused-01/consist-check.json','captures/camera-paused-01/camera.json','pass61/004918e0.asm','pass62/006c0290.asm','pass62/006b63c0.asm','pass61-byte-verification.json','pass62-byte-verification.json'],'native consumers traced; cab/front/rear/trackside/cab switches observed with matching post-input snapshots','view/render update; paused values may retain last rendered frame',common+' View-state and render-camera pointers are distinct. Other mode names, transition timing, projection lifecycle and train-relative camera attachment remain unresolved. Stable pointer/time checks do not make external reads atomic.')
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
