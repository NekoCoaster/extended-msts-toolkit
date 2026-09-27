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
    rows.append(dict(id=id,meaning=meaning,applicability=applies,value_type=typ,units=unit,extraction=method,evidence=list(evidence),
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
        sorted({unit for e in examples for unit in (e['units'] or [])}) or ['not declared in sampled CVF controls; native units unresolved'],'CVF Type declares channel; trace native cab dispatchers 0x41f357 / 0x42064b / 0x4218ae to actual producers',examples,
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
for row in rows:
    if row['id'] in {'body.velocity','body.angular_velocity','car.connection_endpoints','car.connection_endpoint_distance','car.connection_endpoint_velocity','car.connection_separation_rate'}:
        row['evidence']+=['motion-context-grain-01-summary.json','captures/motion-context-grain-01/metadata.json','captures/motion-context-grain-final-paused-01/samples.jsonl']
        row['limitations']+=' New combined player moving capture includes definition/track/timing inputs:body and track movement exceed stored velocity with unchanged origin tile. Endpoint trajectory analysis still pending;do not claim dynamic coupling validation from data availability alone.'
for row in rows:
    if row['id'] in {'body.velocity','body.angular_velocity','car.connection_endpoints','car.connection_endpoint_distance','car.connection_endpoint_velocity','car.connection_separation_rate'}:
        row['evidence']+=['analyse_connection_motion.py','motion-context-ai-01-summary.json','motion-context-grain-01-connections.json','motion-context-ai-01-connections.json','captures/motion-context-ai-01/metadata.json','captures/motion-context-ai-final-paused-01/samples.jsonl']
        row['evidence']=list(dict.fromkeys(row['evidence']))
        row['limitations']=row['limitations'].replace('Endpoint trajectory analysis still pending;do not claim dynamic coupling validation from data availability alone.','Moving player/AI endpoint differences now analysed; stored-state projected velocity does not universally match gap derivatives, including same-clock subsets.').replace('captures lack definition400/414 for endpoint finite differences.','older captures lacked definition400/414; combined captures now include these inputs.').replace('No meaningful nonzero angular or opening/closing transition observed.','No validated nonzero angular transition; sampled gap changes may contain asynchronous placement artifacts.').replace('Definition414 asset meaning and physical AI transitions remain unvalidated.','Definition414 asset meaning remains unvalidated; moving physical AI sampled with non-atomic reads.')
        row['limitations']+=' AI worst rate outlier includes a zero body velocity despite nonzero car/train speed and continued movement; consistent with intermediate reset phase, not execution proof. No force/slack truth or correction factor inferred.'
        row['evidence_status']+='; combined moving player/AI endpoint analysis preserves discrepancies and phase-sensitive outliers'
        if row['id'].startswith('car.connection_'):
            row['applicability']='physical player and AI; paused and moving observations, with non-atomic phase limits'
        if row['id']=='car.connection_separation_rate':row['meaning']='Projected relative stored-state velocity of connected solver endpoints; not universal gap derivative'
integrator_evidence=['INTEGRATOR-TIME-FINDINGS.md','pass163-byte-verification.json','pass164-byte-verification.json','pass165-byte-verification.json','captures/integrator-paused-01/metadata.json','captures/integrator-paused-01/samples.jsonl']
for name,meaning,typ,units,offset in [
 ('time','Stored physics integrator time accumulator','float32','seconds',0x54),
 ('configured_step','Configured physics integration step','float32','seconds',0xc),
 ('current_step','Current or last physics integration step','float32','seconds',0x10),
 ('mode_raw','Physics solver selection code','uint32','native enum',8),
 ('status_raw','Last simulation-object operation status code','uint32','native status',4),
 ('body_count','Registered integration body count','uint32','bodies',0x6c),
 ('enabled_raw','Physics loop continuation gate','uint32','zero/nonzero',0x84)]:
    add('physics_integrator.'+name,meaning,'shared simulation object;player physics path and registered bodies,not independent AI-service clock',typ,units,f'object=[0x80aa1c];object+0x{offset:x};require current vtable0x773280',integrator_evidence,'native setter/getter/integrator traced;11paused samples stable at distinct physics/game elapsed times','step/time updated by native integrator;paused snapshot validates readability only',common+' Sequential non-atomic reads. Internal accumulator is not interchangeable with gameplay elapsed or wall time;paused270.662750 versus gameplay169.710281. Reset/cadence and movement correlation pending. Mode1/3/5/7 have observed dispatch branches;other accepted setter codes are not promised supported solver modes. Status can reflect the last getter/setter,not overall game health. Body count is not train count. Do not infer a universal timing correction.')
for row in rows:
    if row['id'].startswith('physics_integrator.') or row['id'] in {'body.velocity','body.angular_velocity','car.connection_endpoint_velocity','car.connection_separation_rate'}:
        row['evidence']+=['INTEGRATOR-TIME-FINDINGS.md','analyse_integrator_motion.py','integrator-moving-grain-01-integrator-summary.json','captures/integrator-moving-grain-01/metadata.json','captures/integrator-moving-final-paused-01/samples.jsonl']
        row['evidence']=list(dict.fromkeys(row['evidence']))
        row['evidence_status']+='; combined moving player/AI comparison supports distinct motion time bases'
        if row['id'].startswith('physics_integrator.'):
            row['update_or_lifecycle']='native integrator step/time fields;moving130-second capture records accumulation independently of gameplay time,plus paused stability and lower post-reload value;exact per-frame cadence/reset order unproven'
        row['limitations']=row['limitations'].replace('Reset/cadence and movement correlation pending.','Reload shows lower accumulator;moving cadence and position correlation now sampled,exact reset/producer execution still unproven.')
        row['limitations']+=' In integrator-moving-grain-01,player body-speed discrepancy median falls5.179556 to0.002479m/s using physics elapsed,while AI discrepancy rises0.664115 to8.205889m/s. This supports different player/AI time bases in this configuration;not a universal correction or atomic-read guarantee. Residual outliers remain;connection derivative reanalysis under physics time is pending.'
for row in rows:
    if row['id'] in {'car.connection_endpoints','car.connection_endpoint_distance','car.connection_endpoint_velocity','car.connection_separation_rate'}:
        row['evidence']+=['INTEGRATOR-TIME-FINDINGS.md','integrator-moving-grain-01-connections.json','integrator-moving-grain-01-connections-physics.json']
        row['evidence']=list(dict.fromkeys(row['evidence']))
        row['limitations']=row['limitations'].replace('connection derivative reanalysis under physics time is pending.','connection derivative reanalysis now improves typical player agreement but retains significant same-clock outliers.')
        row['limitations']+=' Matched1692player connection comparisons:median error0.004428m/s under gameplay time versus0.000740 under physics time. AI near-zero relative-gap statistics do not determine its clock;absolute AI movement remains inconsistent with physics elapsed. Apparent gap jumps are not physical slack proof.'
owner_evidence=['INFRASTRUCTURE-OWNERS-FINDINGS.md','captures/infrastructure-owners-paused-01/owners.json','pass166-byte-verification.json','pass167-byte-verification.json','pass168-byte-verification.json','pass169-byte-verification.json','pass170-byte-verification.json']
for name,meaning,typ,units,method in [
 ('junction_service_association','Junction matching-service association used by release path','pointer32','service identity','kind2 node+0x58;00595b41 clears matching service then restores shape-defined branch'),
 ('junction_flags4e','Junction raw flags containing cleanup-cleared bit2','uint16','bitfield','kind2 node+0x4e;005959d0 clears bit0x2;full semantics unresolved'),
 ('vector_service_associations','Service values in vector-node routing list,distinct from per-car presence','list of pointer32','service identities','kind1 node+0x38 circular sentinel;next0,prev4,value8;bounded read;00595b6e removes service'),
 ('vector_state35_raw','Vector-node byte set to3 when service list becomes empty','uint8','raw enum','kind1 node+0x35;00595b6e empty-list branch;other values unclassified')]:
    add('infrastructure.'+name,meaning,'shared route nodes;paused player and AI service joins;ownership acquisition/transitions unvalidated',typ,units,method,owner_evidence,'typed release/native layout traced and verified;246junctions408vectors read;3junctions and5vector lists join services','service/route lifecycle;sequential snapshot only,update cadence and reset ordering unknown',common+' No occupancy,exclusive reservation,permission or whole-train extent claim. Selected branch and signal aspect remain separate. Null is not clear/safe. Raw state/flag meanings incomplete. List/pointer checks do not prevent non-atomic races or identity reuse. Route IDs are registry-derived for this route build.')
acquisition_evidence=['INFRASTRUCTURE-OWNERS-FINDINGS.md','pass172-byte-verification.json','pass173-byte-verification.json','captures/infrastructure-acquisition-paused-01/owners.json']
add('infrastructure.vector_constraint34_raw','Vector-node directional claim constraint/state input','shared route nodes;player/AI routing','uint8','raw enum','kind1 node+0x34;0059867c compares with requested direction/code and current35',acquisition_evidence,'native claim-check consumer traced;408paused nodes read with values0/1/3/4','route/service updates;producer and reset cadence unresolved',common+' Values0/1 used with direction requests;2/3special branches,4dominant in snapshot but meaning unresolved. Not occupancy,permission or universal blocked/clear enum. No live transitions validated.')
for row in rows:
    if row['id'] in {'infrastructure.junction_service_association','infrastructure.junction_flags4e','infrastructure.vector_service_associations','infrastructure.vector_state35_raw'}:
        row['evidence']+=acquisition_evidence;row['evidence']=list(dict.fromkeys(row['evidence']))
        row['evidence_status']+='; typed two-pass route claim and directional vector check/commit paths traced'
        row['limitations']+=' Junction first pass checks owner/branch conflicts,second writes owner/branch. Vector commit may write35 before list insertion fails;list may contain repeated service values. Snapshot alone does not prove live acquisition/release timing or physical occupancy.'
for row in rows:
    if row['id']=='infrastructure.signal_service_association':
        row['evidence']+=acquisition_evidence
        row['evidence_status']+=';005c4e55 acquisition traced,including null-owner/flag8000 success without store'
        row['limitations']=row['limitations'].replace('Signal association acquisition and reservation semantics remain unverified.','Signal acquisition helper traced statically;complete reservation semantics and live transitions remain unverified.')
        row['limitations']+=' Acquisition returns success for null24 with existing8000 without assigning owner;success and ownership differ. No such null/8000 combination in the new paused292signal snapshot. Distinct signal28 writer remains separately unresolved.'
for row in rows:
    if row['id'] in {'infrastructure.vector_presence','infrastructure.presence_service','infrastructure.presence_node_distance','infrastructure.signal_service_association','infrastructure.junction_service_association','infrastructure.junction_flags4e','infrastructure.vector_service_associations','infrastructure.vector_state35_raw','infrastructure.vector_constraint34_raw'}:
        row['evidence']+=['INFRASTRUCTURE-OWNERS-FINDINGS.md','infrastructure-ai-transitions-01-summary.json','presence-track-snapshot-check.json','captures/infrastructure-ai-transitions-01/metadata.json']
        row['evidence']=list(dict.fromkeys(row['evidence']))
        row['limitations']+=' New241sample within-node AIrun records moving presence distances but no discrete claim/signal/branch transitions. Paused sorted player presence/physical distances agree;AI22distances all differ+9.65234375m. Not a per-car identity proof or interchangeable position source;timing/reference cause unresolved.'
        row['evidence_status']+=';moving AI within-node presence observed,typed infrastructure transitions not yet captured'
for row in rows:
    if 'timing/reference cause unresolved.' in row['limitations']:
        row['limitations']=row['limitations'].replace('timing/reference cause unresolved.','Native stored-service versus physical extrapolation paths now traced; single paused AI gap agrees with reconstructed travel within0.000342m. No universal correction,per-car identity or cross-node validation.')
    if row['id'] in {'infrastructure.vector_presence','infrastructure.presence_node_distance'}:
        row['evidence']+=['pass177/005a5c32.asm','pass177/005a5b44.asm','pass177/005a5167.asm','pass178/005a4f86.asm','pass178/005a41c2.asm','pass178/005d0334.asm','pass177-byte-verification.json','pass178-byte-verification.json','pass174/005a5c9a.asm','pass174-byte-verification.json','pass179/0062924c.asm','pass179-byte-verification.json']
        row['evidence_status']+=';typed record writer,stored-service and physical-car producer paths traced;paused extrapolation agrees within0.000342m'
        row['update_or_lifecycle']='005a4f86/005a5b44 update from service track during gated service updates;005a5167 uses physical car128 for two supplied lists after005f9285 integration returns;complete list ownership and scheduler ordering unvalidated'
        row['limitations']+=' Writer updates direction18 only when node changes;in-node reversal and insertion/move failures remain unvalidated.'
identity_evidence=['INFRASTRUCTURE-OWNERS-FINDINGS.md','presence-identity-summary.json','captures/presence-identity-paused-01/identity.json','pass177/005a5c32.asm','pass177/005a5167.asm','pass177/005a7821.asm','pass177-byte-verification.json']
for name,meaning,typ,units,method in [
 ('infrastructure.presence_physical_car','Presence record association to physical car','pointer32','session-local address','presence record+0x10;dereference only after matching bounded physical-car registry'),
 ('car.presence_backlink','Physical-car backlink to abstract presence record','pointer32','session-local address','enumerated physical car+0x258;compare with presence record address and reverse record+0x10'),
 ('infrastructure.presence_direction_raw','Stored direction byte in abstract presence record','uint8','native direction code','presence record+0x18;005a5c32 copies track+c only when node changes')]:
    add(name,meaning,'player and physical AI;23player22AI paused exact joins',typ,units,method,identity_evidence,'native access paths and paused bidirectional identity joins verified','record creation/track updates;direction refresh in traced helper only on node change',common+' Single paused state;null/stale/reused pointers possible. Not persistent vehicle identity or proven lifecycle invariant. In-node reversal not validated;direction can retain previous value until refresh. No moving atomicity claim.')
for row in rows:
    if row['id'] in {'infrastructure.vector_presence','infrastructure.presence_node_distance','infrastructure.presence_service'}:
        row['evidence']+=['presence-identity-summary.json','captures/presence-identity-paused-01/identity.json']
        row['evidence_status']+=';later paused45-car pointer/backlink join confirms individual-car correspondence'
        row['limitations']+=' Later presence-identity-paused-01 validates each individual car through record10 and car258 at the same paused time;this strengthens only that state,not moving/lifetime or cross-node guarantees.'
for row in rows:
    if row['id'] in {'infrastructure.vector_presence','infrastructure.presence_node_distance','infrastructure.presence_service','infrastructure.presence_physical_car','car.presence_backlink','infrastructure.presence_direction_raw'}:
        row['evidence']+=['presence-identity-moving-01-summary.json','captures/presence-identity-moving-01/metadata.json','captures/presence-identity-final-paused-01/identity.json']
        row['evidence_status']+=';261sample series observes physical AI removal while22abstract presence records continue moving'
        row['limitations']+=' Single physical-removal transition:record10 becomesnull and AItrain158/physicalized134 clear;abstract records persist and advance. Before removal40moving samples show start-clock median gap error1.588825m versus end-clock0.000268m,max0.244449m;no same-clock moving samples. Sequential read phase remains material. Observed update ages reach1.453125s;not bounded to1s. Rephysicalization and node crossing untested.'
gate_evidence=['AI-LIFECYCLE-FINDINGS.md','captures/ai-distance-gate-paused-01/gate.json','pass180/005a58af.asm','pass180/005a7d3d.asm','pass180/005a966e.asm','pass180-byte-verification.json']
for name,meaning,typ,units,method in [
 ('camera.view_position','Player view-state position used by AI physicalization gate','float32[3]','metres in shared local frame','[[0x7c2a88]+0x38];distinct from render-camera position'),
 ('service.physicalization_distance_squared_threshold','Native squared-distance threshold for AI physicalization','float32','square metres','0x770718;this image1960000.0 implies1400m radius'),
 ('service.physicalization_endpoint_distances','Distances from both stored service endpoints to player view','derived float64[2]','metres','sqrt(sum((service+94/fc vector - view+38 vector)^2));retain endpoint/view inputs and service gates')]:
    add(name,meaning,'player-view context and AI service physicalization',typ,units,method,gate_evidence,'native comparison/removal paths traced;paused distance inputs and disk/live threshold match','view/service updates;origin and lifecycle validity required',common+' Finite-value reconstruction,not instruction-exact rounding. Null/uninitialized endpoints and disabled service gates can satisfy numeric predicates without spawning. Either endpoint strictly inside allows creation path;both strictly outside allow removal path;success/other gates unproven. No threshold-crossing or other-view/origin-shift runtime validation. Current initialized AI remains outside;later inactive service has zero endpoints.')
for row in rows:
    if row['id'] in {'infrastructure.junction_service_association','infrastructure.vector_service_associations','infrastructure.vector_state35_raw','infrastructure.vector_constraint34_raw','infrastructure.signal_service_association'}:
        row['evidence']+=['infrastructure-player-approach-01-summary.json','captures/infrastructure-player-approach-01/metadata.json']
        row['evidence_status']+=';restart capture observes junction/vector/signal association acquisition and independent aspect transitions'
        row['limitations']+=' First resume initialization bracket acquiresjunction302AIassociation and3vectorlists;3signalassociationsfollow. No release or selected-branch change. Some aspect changes occur independently of associations. Player approach failed at red before node crossing;capture intentionally interrupted,300complete records preserved. All eventpairs cross simulation steps;route/database indices are local.'
for row in rows:
    if row['id'] in {'infrastructure.junction_service_association','infrastructure.vector_service_associations','infrastructure.vector_state35_raw','infrastructure.vector_constraint34_raw','infrastructure.signal_service_association','infrastructure.vector_presence','infrastructure.presence_node_distance','infrastructure.presence_service'}:
        row['evidence']+=['infrastructure-ai-clearance-01-summary.json','infrastructure-ai-clearance-01-crossings.json','captures/infrastructure-ai-clearance-01/metadata.json','captures/infrastructure-clearance-final-paused-01/owners.json']
        row['evidence_status']+=';421sample run observes22AIpresence crossings,release and player acquisition with selected-branch changes'
        row['limitations']+=' Later stationary-player run records22same-identity AIrecords300->310,count22conserved;last crossing shares snapshot bracket withjunction302/vector300release. Player acquires lists thenjunction302branch0->1. Dynamic release/branch coverage nowpositive,butexactinstructionorder and visualsignalitemjoin unproven. Playerdidnotcross. Earlier no-transition statements apply to their named captures only.'
for row in rows:
    if row['id'] in {'signal.next_iterator','signal.next_distance','signal.head_identity','signal.aspect','infrastructure.signal_service_association'}:
        row['evidence']+=['SIGNALS-AND-CAB-FINDINGS.md','forward-signal-clearance-join.json','captures/clearance-forward-signal-paused-01/details.jsonl']
        row['evidence_status']+=';paused forward head joins to databaseitem318 and same-run421sample0->7 clearance history'
        row['limitations']+=' Current iterator index46 is databaseitem318,distinct index spaces. Head/definition continuous in421samples;iterator itself not continuously sampled. Clear attribution remains scoped to current run and prior aspect UI validation,not portable ID or exact causal timing.'
# Consolidate later evidence without treating historical capture limitations as
# permanent absence of evidence. Candidate IDs and underlying raw files persist.
for row in rows:
    if row['id']=='body.position':
        row['meaning']='Physics-body reference position in local simulation coordinates'
        row['units']='metres; current local origin, not geographic coordinates'
        row['evidence']+=['TRACK-POSITION-FINDINGS.md','MOTION-DIFFERENCE-FINDINGS.md','INTEGRATOR-TIME-FINDINGS.md']
        row['evidence_status']='live player/AI movement sampled; local body and track reference points compared; clock and producer-phase differences documented'
        row['limitations']=common+' Track traversal uses the native 2048-m tile-origin translation; this does not prove the same inverse is a validated continuous body-world transform through an origin shift. Body and track reference points differ. Physical-body buffers can change and intermediate AI placement/reset phases can yield misleading derivatives. Player physics and AI service movement use distinct observed time bases; do not silently substitute gameplay time or infer a universal velocity correction.'
    if row['id'] in {'signal.next_iterator','signal.next_distance','signal.head_identity','signal.aspect','infrastructure.signal_service_association'}:
        row['evidence']+=['PAIRED-INFRASTRUCTURE-FINDINGS.md','paired-player-crossing-01-paired-summary.json','captures/paired-player-crossing-01/metadata.json']
        row['evidence_status']+=';601-sample stationary-player paired series has unique head/definition joins and zero aspect disagreements'
        row['limitations']+=' Separate paired series continuously samples iterator/head/distance while player stays stopped;distance882.151367m and aspect7 remain constant. This does not validate moving refresh or player crossing. Infrastructure/monitor/tracks are sequential phases;stable rereads do not establish atomicity.'
    if row['id'] in {'infrastructure.vector_presence','infrastructure.presence_node_distance','infrastructure.presence_service','infrastructure.presence_direction_raw'}:
        # The crossing analyzer checks identity and node changes, not physical extent
        # or direction correctness. Never broaden its result to those properties.
        row['evidence']+=['infrastructure-ai-clearance-01-crossings.json','PAIRED-INFRASTRUCTURE-FINDINGS.md','paired-player-crossing-01-crossings.json']
        row['limitations']=row['limitations'].replace('Rephysicalization and node crossing untested.','Rephysicalization remains untested; a later capture validates22abstract-record node crossings,not physical extent or direction semantics.')
        row['limitations']+=' The later paired series preserves45abstract records after physical AI removal;no node crossing occurs in that series. Earlier421-sample crossing evidence is separate. Direction correctness during crossing/reversal remains unvalidated.'
selection_evidence=['ENVIRONMENT-SELECTION-FINDINGS.md','pass181-byte-verification.json','pass181/004935af.c','pass181/00493341.c','environment-selection-summary.json','captures/environment-selection-paused-01/selection.json']
for name,meaning,typ,units,method in [
    ('season_selector','Season selector consumed by ENV filename selection','uint32','raw0..3;out-of-range fallback','[0x79a3ac]'),
    ('weather_selector','Weather selector consumed by ENV filename selection','uint32','1 snow,2 rain,other default slot;not route slot index','[0x7be0d8]'),
    ('editor_override','Raw selector override choosing editor.env','uint32','zero/nonzero','[0x7be0f8]'),
    ('route_filename_table','Loaded route season/weather ENV filename table','12 pointer32 to bounded UTF16 strings','filenames;four rows of clear/rain/snow slots','route=[0x7b8d3c];route+0x70+season*12+slot*4'),
    ('selected_filename','Current selected ENV filename buffer','bounded UTF16 string','filename','buffer at0x7b8d48;not pointer indirection'),
    ('route_directory','Route directory buffer used by path setup','bounded UTF16 string','installation-relative path','buffer at0x7b8310'),
    ('env_directory','ENV directory buffer constructed by route setup','bounded UTF16 string','installation-relative path','buffer at0x7b74cc'),
    ('env_texture_directory','ENV texture directory buffer constructed by route setup','bounded UTF16 string','installation-relative path','buffer at0x7b76d4')]:
    add('environment.selection.'+name,meaning,'shared loaded route/environment context;not per-train state',typ,units,method,selection_evidence,'native selector/path setup traced and live bytes verified;paused12-slot table and selected name match installed route','route/activity setup;alternate initialization/reset writers and change latency unvalidated',common+' One paused winter/snow sample. Selectors differ from activity-header addresses despite matching values. Selected string is not proof of current file contents or complete successful resource loading. Unknown season falls back to row1/default slot;editor and invalid/weather branches not exercised. Bounded string reads and endpoint checks do not prevent races/reuse. Allseasons share filenames here,so file comparison cannot independently establish season order.')
sky_evidence=['ENVIRONMENT-SELECTION-FINDINGS.md','pass182-byte-verification.json','pass182/006e3dd0.c','captures/sky-structure-paused-01/sky.json']
for name,meaning,typ,units,method in [
    ('pointer','Loaded sky object identity','pointer32','session identity','sky=[[0x7b6d60]+0]'),
    ('layer_count','Loaded sky layer record count','uint32','records','sky+0'),
    ('layer_split','Stored satellite insertion split selector','int32','raw layer index/sentinel;renderer semantics require validation','sky+4'),
    ('layer_array','Loaded sky layer record identities','pointer32 plus bounded array','record addresses,stride0x1ac','array=[sky+8];count=[sky]'),
    ('satellite_count','Loaded sky satellite record count','uint32','records','sky+0x180'),
    ('satellite_array','Loaded satellite record identities','pointer32 plus bounded array','record addresses,stride0x1cd','array=[sky+0x184];count=[sky+0x180]')]:
    add('environment.sky.'+name,meaning,'shared render environment;not per-train state',typ,units,method,sky_evidence,'native parser allocation/layout verified against disk/live;paused3layers2satellites and split2 sampled','environment load;runtime updates/teardown and pointer reuse unvalidated',common+' Loaded count is not active/visible/drawn count. Conservative32-record probe bound is not native capacity. Raw records retained without promoting undecoded bytes to semantic fields. Split initializes-1 and defaults count-1 if not overridden;renderer and malformed/zero-count behavior not validated. Snapshot non-atomic despite stable structural rereads.')
satellite_evidence=['SATELLITE-FIELDS-FINDINGS.md','satellite-fields.json','satellite-fields-summary.json','pass183-byte-verification.json','pass183/006e4cf0.c','captures/sky-structure-paused-01/sky.json']
for name,offset,fmt,meaning,units in json.loads((ROOT/'satellite-fields.json').read_text()):
    typ='pointer32' if name=='light_pointer' else {'f':'float32','I':'uint32','B':'uint8'}[fmt]
    add('environment.satellite.'+name,meaning,'loaded shared sky satellite records;not independent player/AI state',typ,units,
        f'sky=[[0x7b6d60]];base=[sky+0x184];index<[sky+0x180];record=base+index*0x1cd;record+0x{offset:x}',
        satellite_evidence,'native parser and caller match disk/live;two retained paused records decoded;20selected literal/default comparisons exact',
        'loaded during ENV parsing;subsequent writers/reset/teardown not completely surveyed',
        common+' Configuration inputs and session object identity,not current visible/render output. Approximate degree conversion and loader scale apply;scale ratio1observed here only. Six colours are packed native keys,not linear RGB. Fade2400 and fog255 defaults observed;fog token narrows tobyte. Light object is created even for authored light0,so pointer does not prove registration,visibility or active illumination. File order matters to initial light inputs. No dynamic sky transition or universal parser acceptance validated.')
layer_evidence=['SKY-LAYER-FINDINGS.md','unity-kb-provenance.json','pass182-byte-verification.json','pass184-byte-verification.json','sky-layers-summary.json','captures/sky-layers-paused-01/layers.json']
for name,meaning,typ,units,method in [
    ('top_faces','Stored layer top face parameter','uint32','count;parser initializes8','layer+0'),
    ('top_radius','Loaded layer top radius','float32','native length after loader scaling','layer+4'),
    ('top_height','Loaded layer top height','float32','native length after loader scaling','layer+8'),
    ('edge_count','Loaded edge-step count','uint32','records','layer+0xc'),
    ('edge_array','Loaded edge-step record identities','pointer32 plus bounded array','stride8 record addresses','[layer+0x10]'),
    ('edge_height','Loaded edge-step height','float32','native length after loader scaling','edge+0'),
    ('edge_radius','Loaded edge-step radius','float32','native length after loader scaling','edge+4'),
    ('fadein_start','Loaded layer fade-in start','float32','day-clock seconds','layer+0x14'),
    ('fadein_end','Loaded layer fade-in end','float32','day-clock seconds','layer+0x18'),
    ('fadeout_start','Loaded layer fade-out start','float32','day-clock seconds','layer+0x1c'),
    ('fadeout_end','Loaded layer fade-out end','float32','day-clock seconds','layer+0x20')]:
    add('environment.layer.'+name,meaning,'shared loaded sky layers;not per-train values',typ,units,
        'sky=[[0x7b6d60]];layer=[sky+8]+index*0x1ac,index<[sky];edge=[layer+0x10]+edgeIndex*8,edgeIndex<[layer+0xc];'+method,
        layer_evidence,'native parser/render ranges verified;3layers4edges read with stable headers;24literal/default scalar/array comparisons match',
        'environment parsing/configuration;later mutation/reset writers and teardown unvalidated',
        common+' Loaded parameters,not current alpha or draw visibility. Matching authored face8 cannot prove token consumption;parser initializes8. Geometry scaling ratio1here only. Missing fade declarations retainzero pairs;do not infer invisibility. Native edge tokenorder increments onradius. Pointer/header rereads do not prove atomicity. Consolidated UnityKB preserves earlier native evidence but its historical time-substitution/device tests are not current passive telemetry validation.')
vertex_evidence=['SKY-VERTEX-FINDINGS.md','pass184-byte-verification.json','pass185-byte-verification.json','pass184/006e53c0.asm','pass184/006e1310.c','pass185/006e1070.c','sky-vertices-paused-01-summary.json','sky-vertices-paused-02-summary.json','captures/sky-vertices-paused-02/metadata.json']
vertex_evidence += ['SKY-CLOCK-FINDINGS.md','sky-scroll-summary.json','pass188-byte-verification.json','pass188/006e1470.asm','pass188/006e1520.asm','pass188/0053314d.asm']
for name,meaning,typ,units,method in [
    ('vertex_count','Allocated sky draw-object vertex count','uint32','vertices','draw+4'),
    ('vertex_array','Sky CPU vertex buffer identity','pointer32','session identity,stride0x28','[draw+8]'),
    ('vertex_position','Stored local sky mesh vertex position','3 float32','native local mesh coordinates,not world train position','vertex+0'),
    ('vertex_diffuse','Stored sky vertex diffuse colour','uint32','packed native colour including alpha','vertex+0x18'),
    ('vertex_secondary','Stored sky vertex secondary/specular word','uint32','raw packed render value;fog interpretation path-dependent','vertex+0x1c'),
    ('vertex_uv','Stored mutable sky texture coordinates','2 float32','UV coordinates,not clamped0..1','vertex+0x20'),
    ('frame_count','Loaded sky animated-shader frame count','uint32','frames','shader+0'),
    ('frame_duration','Loaded sky animated-shader frame duration','float32','native animation time parameter;zero has special update branch','shader+4'),
    ('animation_clock','Stored sky shader animation phase accumulator','float32','native render time;can wrap by frame count times frame duration;advances while gameplay paused','shader+8'),
    ('selected_frame','Raw selected sky shader frame index','uint32','index;FFFFFFFFparser initialization sentinel','shader+0xc'),
    ('frame_array','Loaded sky shader frame records','pointer32 plus bounded array','stride0x20 records','[shader+0x10],count[shader]'),
    ('frame_scroll','Selected frame texture scroll coefficients','2 float32','UV increment per native delta unit','frame+0x18;frame=[shader+0x10]+index*0x20,onlyifindex<count')]:
    add('environment.render.'+name,meaning,'shared layer/satellite CPU sky state;not per-train or proof of visibility',typ,units,
        'layerdraw=layer+0x190,layershader=layer+0x24;satellitedraw=satellite+0x1b1,satelliteshader=satellite+0x45;vertex=[draw+8]+index*0x28;'+method,
        vertex_evidence,'native layout/update/init match current disk/live;61corrected paused samples,0read errors,5shader reread changes',
        'render/animation updates can continue while gameplay clock paused;inactive objects may retain initialization/stale buffers',
        common+' Initial61sample series entirelyfailed overstrictframe-index guard;retained separately. Correctedreader retainsFFFFFFFF withoutdereference. Pauseddayclock fixed yetlayer0/2UV and4shaderclocksadvance;no universal atomicity,drawvisibility,wall-time equivalence or producer rate. Inactivesatellite retainedtinyUV value;allocated doesnot meanmeaningful. Count/frame bounds are probe guards. Onlyone-frame configured objects observed;frame transitions/reload and broader shader cases unvalidated.')
audio_stream_evidence=['AUDIO-STREAM-FINDINGS.md','audio-streams-summary.json','pass189-byte-verification.json','pass189/0053f153.asm','pass189/005384fe.c','pass189/0053e2d2.c','captures/audio-streams-paused-01/streams.json','captures/audio-streams-paused-02/streams.json']
for name,meaning,typ,units,method in [
    ('state_identity','Per-receiver stream runtime record identity','pointer32','session address;stride0x1c','state=[receiver+0x14]+stream_index*0x1c'),
    ('backend_identity','Native stream backend object identity','pointer32','session address;may be replaced by condition transitions','[state]'),
    ('backend_flags','Native stream backend flags','uint32','raw bits;helper005384fe testsbit2;not audibility','[backend+4]'),
    ('queue_head','Stream linked pending-record head','pointer32','session address;zero empty','[state+4];node next at+8'),
    ('queue_count','Number of linked stream pending records when traversal completes','derived uint32 or unavailable','records;not seconds or playback position','bounded traversal from[state+4] following node+8;unavailable on bound/cycle/error'),
    ('cached_volume_curve','Cached stream volume-curve result','float32','native multiplier before global/receiver scaling;not final output volume','state+8'),
    ('cached_frequency_curve','Cached stream frequency-curve result','float32','native frequency parameter before clamp;not measured hardware output','state+0xc'),
    ('trigger_enable_words','Stream trigger-enable mask words','2 uint32','bit indexed by trigger index;not firing history','state+0x10 and+0x14'),
    ('volume_factor','Stored stream volume factor','float32','native multiplier combined with receiver/global and optional curve','state+0x18'),
    ('interface_identities','Stored buffer and spatial-interface identities','2 pointer32','session addresses;presence not playing/audible','backend+0x30 and+0x74;never invoke from probe'),
    ('trigger_count','Loaded per-stream trigger record count','uint32','configured triggers;not events fired','stream_definition=[definition+0x14]+index*0x20;count at+0')]:
    add('audio.stream.'+name,meaning,'shared audio receiver streams;50 player-associated observed;physical AI unvalidated',typ,units,method,
        audio_stream_evidence,'native consumer/helper instruction ranges match disk/live;33receivers67streams captured;bounded chain exception preserved',
        'audio processing may continue while gameplay paused;backend replacement and receiver lifetime can invalidate identity',
        common+' Sequential snapshot;stable rereads and zero observed lock words do not prove atomicity or lifetime. No native/API calls. One stream exceeds256-node research bound;its full queue count is unavailable. Firing history, audio duration, final output volume/frequency and actual audibility are not measured. Cached curve values may remain stale when branches skip them. Mask storage covers64bits;larger trigger counts require separate layout validation. No AI receiver association in this paused session.')
pending_evidence=['AUDIO-PENDING-FINDINGS.md','audio-pending-summary.json','pass190-byte-verification.json','pass191-byte-verification.json','pass192-byte-verification.json','pass190/0053e203.asm','pass191/005416cc.c','pass192/0053e55a.c','captures/audio-pending-paused-01/pending.json']
for name,meaning,typ,units,method in [
    ('kind','Pending audio record type discriminator','uint8','native type;1sample-reference record;2different nested payload','node+0'),
    ('control_bytes','Pending audio record raw control bytes','3 uint8','raw values;individual meanings not fully traced','node+1,+2,+3'),
    ('sample_identity','Type1 requested sample-reference identity','pointer32','session address;not current playback identity','[node+4] only when[node+0]==1'),
    ('sample_path_parts','Loaded directory and filename labels for requested sample','two bounded UTF16 strings','path labels;not independently verified file content identity','sample=[node+4] forkind1;pair=[sample+8];strings=[pair] and[pair+4]'),
    ('acquisition_counter','Sample load/acquisition reference counter candidate','uint32','successful acquisition increments;release accounting untraced;not play count','sample+4 forkind1'),
    ('resource_identity','Loaded resource object for requested sample','pointer32','session address;not proof of successful/current audio output','[sample+0x14] forkind1')]:
    add('audio.pending.'+name,meaning,'shared pending audio requests;five samples observed on unassociated receivers;AI/player applicability beyond structure unvalidated',typ,units,method,
        pending_evidence,'typed constructors/load helper match disk/live;262nodes and5kind1 sample objects read with stable rereads',
        'audio enqueue/processing and resource lifetime;non-atomic reads;no release/reset transition observed',
        common+' Type2payload is not a sample pointer and nested structures are not traversed. One chain remains incomplete at256nodes;raw bytes retain uncertainty. Paths are loaded labels,not hash-verified files or observed playback. Counter cannot be inferred from partial queue counts. No AI association from filenames. Native flag2 can be set without a buffer playback call in flag10 branch.')
nested_evidence=['AUDIO-NESTED-FINDINGS.md','audio-nested-summary.json','captures/audio-nested-paused-01/nested.json','pass190/0053e2d2.c','pass192-byte-verification.json']
for row in rows:
    if row['id'].startswith('audio.pending.'):
        row['evidence'].extend(nested_evidence)
        row['applicability']='shared pending audio requests;player engine/cab and unassociated sources observed;AI unvalidated'
        row['limitations']=row['limitations'].replace('Type2payload is not a sample pointer and nested structures are not traversed.','Type2payload is not a sample pointer;follow its child ring only with the verified wrapper-return traversal.')
        row['limitations']+=' Follow-up bounded type2 traversal resolves12 type1 children returning to4wrappers and8samples including player engine/cab. Sample identity can be shared by different receiver/stream/car associations;retain all levels. Raw control-byte meanings and current playback remain unvalidated.'
for name,meaning,typ,units,method in [
    ('nested_children','Type2 pending-record child ring identities','bounded pointer32 array','session identities;128-child probe bound not native capacity','first=[wrapper+4],follow child+8 until wrapper;require child kind1'),
    ('nested_child_count','Child count for a completely traversed type2 pending record','derived uint32 or unavailable','records,not audio duration or playback position','count children only on successful return to wrapper;unavailable on null/type/cycle/bound/error')]:
    add('audio.pending.'+name,meaning,'player engine/cab and unassociated source wrappers observed;AI unvalidated',typ,units,method,
        nested_evidence,'verified native construction rule;4wrappers3children each with stable full-record rereads',
        'pending request enqueue/processing;no lifetime or removal transition tested',
        common+' Return to wrapper is expected;other cycles are invalid to this probe. Counts are structural,not playing voices. Sample references can be shared. Top-level traffic chain remains incomplete. No actual playback, sound segment meaning, AI owner or global reference-accounting proof.')
input_evidence=['INPUT-BINDINGS-FINDINGS.md','input-bindings-summary.json','captures/input-bindings-paused-01/input.json','pass194-byte-verification.json','pass194/006bb790.c','pass194/006bb8b0.c','pass194/006bc130.c']
for name,meaning,typ,units,method in [
    ('mode','Raw native input mode/gate','uint32','opaque mode;zero observed;full enum untraced','[0x829980]'),
    ('devices','Native input device registry identities','bounded pointer32 list','session addresses;not connected physical-device count guarantee','root=[0x8299a0];circular nodes next0/device8'),
    ('device_kind','Input object device kind','uint8','native kind;1keyboard;2observed but not independently named','input=[device+4];input+0x2d'),
    ('keyboard_count','Native keyboard entry count','uint32 difference','entries;238observed,not fixed256','[device+0x14]-[device+0x10]'),
    ('keyboard_held','Native keyboard held-state bitset','bounded bitset','one bit per native scan index;not virtual-key codes or dispatched commands','bits=[input+0x24],readceil(count/8),bitindex scan'),
    ('bindings','Native scan binding records and modifier words','bounded records','16-byte records;action0,next4,modifier8,flagsc','table=[device+0x18];first=table+(device10+scan)*16;followbinding+4'),
    ('action_id','Bound input action opaque identifier','uint32','native identifier;semantic names untraced','action=[binding];[action]'),
    ('action_flags','Native bound-action state flags','uint32','raw bits;context/lifecycle-dependent','action+0x10'),
    ('listeners','Bound action listener callback/context/mask/flags','bounded records','20-byte records;callback0,context4,next8,maskc,flags10','head=[action+4];followlistener+8;neverinvoke')]:
    add('input.'+name,meaning,'local native input context;not AI driver commands',typ,units,method,input_evidence,
        'layout reused from pinned clean NEMT source;native list/binding/listener helpers verified;paused238-entry keyboard read',
        'input polling/binding context;producer cadence and key transitions not tested here',
        common+' No OS-wide input read or native callback calls. Paused all-zero held bitset only;does not prove functioning gameplay dispatch.73retained records include6action references/5unique actions,not73commands. Count-sized30byte read avoids allocator-tail keys. Stable sequential rereads cannot exclude ABA. Other device kinds/axes,complete modifier semantics,action naming and buffered event transitions remain open.')
dispatch_evidence=['INPUT-DISPATCH-FINDINGS.md','pass195-byte-verification.json','pass195/006bad60.asm','pass197-byte-verification.json','pass197/range.asm','pass198-byte-verification.json','pass198/range.asm','captures/input-dispatch-buffer-paused-01/dispatch.json']
for row in rows:
    if row['id'] in {'input.keyboard_held','input.listeners','input.action_flags'}:
        row['evidence'].extend(dispatch_evidence)
        row['limitations']+=' Keyboard producer/event getter bounded bytes match disk/live, but006bad60 has an existing live entry detour;no complete dispatch equivalence. Empty-buffer and zero-held observations are not a key-transition test.'
    if row['id']=='input.listeners':
        row['meaning']='Bound action listener target/context/mask/flags'
        row['units']='20-byte records;target0,context4,next8,maskc,flags10;mask0x100 selects callback,otherwise target is value destination'
    if row['id']=='input.action_flags':
        row['value_type']='uint16';row['extraction']='action+0x12';row['units']='raw state bits;prior uint32 read also included filter word at+0x10'
for name,meaning,typ,units,method in [
    ('action_value','Stored action event value or button-reference count','uint32','event-type-dependent;not universal boolean or axis','action+0xc'),
    ('action_filter','Action dispatch filter word','uint16','opaque filter;compared toFFFFwhen globalmode2','action+0x10'),
    ('buffer_capacity','Keyboard native event buffer capacity','uint32','16-byte records;12observed','input+0x10'),
    ('buffer_cursor','Keyboard event consumption cursor','uint32','record index;not lifetime event count','input+0x14'),
    ('buffer_count','Keyboard current buffered record count','uint32','records this transient buffer;not history','input+0x18'),
    ('buffer_records','Keyboard buffered native input records','bounded array of4uint32','16-byte records:scan/typeword,0or1value,two raw source words','buffer=[input+0xc],readcount records only;cursor partitions consumed/unconsumed snapshots')]:
    add('input.'+name,meaning,'local keyboard/input actions;not AI driver state',typ,units,method,dispatch_evidence,
        'disk dispatcher semantics traced with existing live entry patch;keyboard update/getter ranges match disk/live;capacity12emptybuffer observed',
        'input polling clears/produces/consumes buffer;non-atomic external reads may miss events',
        common+' Do not invoke methods or write target pointers. Live dispatch patch fingerprint retained but full detour behavior unaudited. No complete-event guarantee or timestamp units. Nonempty buffer,held-key transitions and action invocation remain untested. Mode/filter/action units vary by event type;source flags not gameplay outcomes.')
for row in rows:
    if row['id'] in {'input.keyboard_held','input.buffer_capacity','input.buffer_cursor','input.buffer_count','input.buffer_records'}:
        row['evidence'].extend(['KEYBOARD-TRANSITION-FINDINGS.md','keyboard-transition-summary.json','captures/keyboard-shift-paused-01/metadata.json'])
        row['evidence_status']+=';one paused Shift_L press yields2distinct native records in3samples;5394samples0errors,held bits always zero'
        row['limitations']+=' Later short-key test observes scan2a/value1and0 records but no sampled held interval. Nonempty-buffer evidence supersedes the earlier empty-only observation;it does not establish lossless capture or successful gameplay dispatch. Repeated buffer snapshots are not additional events;cursor distinguishes consumed entries.'
header_evidence=['SAVE-HEADER-FINDINGS.md','save-header-prefix.json','save-token-map.json','pass203-byte-verification.json','pass203/0049f73c.asm','captures/save-header-sources-paused-01/sources.json']
for name,meaning,method in [
    ('route_display_label','Loaded route display label','route=[0x7b8d3c];UTF16 [route+4]'),
    ('route_identifier_label','Loaded route identifier label used by header','route=[0x7b8d3c];UTF16 [route+0x14]'),
    ('activity_context_label04','Loaded activity context label at+4','activity=[0x7b8d40];UTF16 [activity+4]'),
    ('activity_context_label08','Loaded optional activity context label at+8','activity=[0x7b8d40];UTF16 [activity+8],null unavailable'),
    ('activity_title','Loaded activity title used by save header','activity=[0x7b8d40];UTF16 [activity+0xc]'),
    ('activity_path','Loaded activity source path;header emits basename','activity=[0x7b8d40];UTF16 [activity+0x1c]')]:
    add('session.'+name,meaning,'shared loaded session;not individual AI service identity','bounded UTF16','text;labels not globally unique file identities',method,header_evidence,
        'writer argument sources match disk/live;6live strings with stable pointer/root rereads;stored ASV title/basename corroboration',
        'route/activity load context;reload/reuse and editor fallback not validated',
        common+' Non-atomic strings;stable pointers do not guarantee stable contents. Current root branch only. Opaque context labels must not be named solely from valuesUSA2/USA2_2. Header stripsactivitypath basename andalternatebranch emits emptyroute strings. Installed ASV is not a current SAV,origin differs;no save/load round trip or file-content identity proof.')
resource_evidence=['SAVE-HEADER-TAIL-FINDINGS.md','save-header-tail.json','save-header-lists.json','header-resource-comparison.json','captures/header-resource-versions-paused-01/versions.json','pass204-byte-verification.json','pass205-byte-verification.json','pass206-byte-verification.json','pass204/0049fe49.asm','pass204/0049ffa1.asm','pass204/0049ffe5.asm','pass205/0049fe93.asm']
for name,meaning,method,applies in [
    ('path_version_word','Loaded path raw word emitted in native Version_Path list','path=[service+0x130];uint32[path+0x18]','player and AI services with loaded path'),
    ('consist_version_word','Loaded consist raw word emitted in native Version_Consist list','consist=[service+0x18];uint32[consist+0x88]','player and AI services with loaded consist;header requires loaded path'),
    ('service_version_word','Loaded service raw word emitted in native Version_Service list','uint32[service+4]','player and registered AI services;header requires loaded path'),
    ('traffic_version_word','Loaded traffic raw word emitted in native Version_Traffic block','uint32[0x809ae8];name UTF16[0x809ae0]','shared loaded activity traffic metadata')]:
    add('resource.'+name,meaning,applies,'uint32','raw native Version_* metadata;producer meaning untraced',method,resource_evidence,
        'writer callbacks match disk/live;paused player and2AI service sources readable;9distinct stored/live name-word pairs agree',
        'loaded resource/service lifetime;reload and word mutation not observed',
        common+' Resource metadata,not motion or simulation counters. No uniqueness/content-hash/revision-increment guarantee. Header filters missing path resources and deduplicates names via native comparison whose case rules remain untraced. Sequential reads are non-atomic. Installed ASV agreement is not a newly generated SAV or load round trip.')
save_object_evidence=['SAVE-OBJECT-SURFACE-FINDINGS.md','save-object-source-summary.json','captures/save-object-sources-paused-01/sources.json','pass207-byte-verification.json','pass208-byte-verification.json','pass209-byte-verification.json','pass210-byte-verification.json']
for row in rows:
    if row['id'] in {'train.identity','train.speed','train.kind_raw','train.first_car','train.last_car','train.lead_car','train.service_pointer','car.body_pointer','body.position','body.right','body.up','body.forward','body.velocity','body.angular_velocity','body.momentum','body.angular_momentum','body.inverse_mass','body.flags_raw','body.derailed','body.resting'}:
        row['evidence'].extend(save_object_evidence)
        row['limitations']+=' Save-writer coverage follow-up traces containing raw ranges or explicit references and captures one paused23-vehicle player train. This is not an independent proof of field units, portable serialization, physical AI coverage, or successful save/load. Raw blocks retain pointers alongside separately encoded IDs.'
for row in rows:
    if row['id'] in {'train.registry','train.first_car','train.last_car','train.lead_car','train.service_pointer','car.train_owner','car.links','car.definition','engine.definition'}:
        row['evidence'].extend(['SAVE-LOAD-IDENTITY-FINDINGS.md','pass211-byte-verification.json','pass212-byte-verification.json','pass213-byte-verification.json','pass214-byte-verification.json','pass215-byte-verification.json','pass216-byte-verification.json'])
        row['limitations']+=' Load-side code clears/reconstructs copied pointers; some normally pointer-bearing fields temporarily hold saved IDs until later fixup. Rebuild associations after load; no externally validated load-complete gate or actual round-trip observation. Main loading caller has a documented live patch at494bc1; focused reconstruction routines match disk/live.'
for row in rows:
    if row['id'] in {'train.registry','train.identity','train.first_car','train.last_car','train.lead_car','train.service_pointer','car.identity','car.train_owner','car.links','car.definition','engine.definition','body.position','body.right','body.up','body.forward'}:
        row['evidence'].extend(['SAVE-RELOAD-RUNTIME-FINDINGS.md','generated-save-structure.json','save-reload-comparison.json','captures/reload-transition-01/metadata.json','captures/after-reload-services-01/services.jsonl'])
        row['limitations']+=' Follow-up native UI save/reload succeeds for one23-vehicle player fixture: numeric train/vehicle IDs preserved,all23caraddresses change,positions/orientations exact. This supersedes prior no-round-trip notes only for these observed checks.96of239transition samples have recorded registry errors;AIphysicalreload and a reliable load-complete gate remain unvalidated.'
moving_evidence=['MOVING-PLAYER-ORIGIN-FINDINGS.md','paired-moving-restart-01-paired-summary.json','paired-moving-restart-01-moving-tracks.json','paired-moving-restart-01-origin-shifts.json','paired-moving-approach-02-paired-summary.json','paired-moving-approach-02-moving-tracks.json','captures/red-signal-evaluation-01/evaluation.json']
moving_evidence.extend(['paired-n2-approach-01-paired-summary.json','paired-n2-approach-01-moving-tracks.json','paired-n2-approach-01-origin-shifts.json'])
for row in rows:
    if row['id'].startswith('track.') or row['id'] in {'body.position','train.registry','monitor.distance','service.physicalized_raw','service.train_pointer'}:
        row['evidence'].extend(moving_evidence)
        row['limitations']+=' Follow-up paired moving run observes63player section changes across two series,AI physical appearance and one originX+1rebase across45matchedcar/body identities. No player node crossing or successful signal passage;activity ended at red. Full coordinate conventions and repeated AI reappearance remain unvalidated.'
    if row['id']=='track.route_position_candidate':
        row['extraction']='X=localX+2048*originTileX; Z=localZ+2048*originTileZ; Y retained; usefloat64 and stable origin/body identities.'
        row['evidence_status']+=';one live origin rebase across23player+22AIcars reduces2048m local jump to maximum9.561979m corrected sampled displacement'
        row['limitations']+=' This supersedes earlier no-origin-crossing observations for oneX-tile shift only;not exact integration or atomicity proof.'
for row in rows:
    if row['id'] in {'body.position','body.angular_velocity','body.angular_momentum','body.flags_raw','body.derailed','body.resting'} or row['id'].startswith('track.'):
        row['evidence'].extend(['COLLISION-STATE-FINDINGS.md','collision-state-summary.json','captures/collision-paused-01/samples.jsonl','captures/collision-track-paused-01/tracks.json'])
        row['limitations']+=' Post-collision paused observation:23player and19AIvehicles flaggedderailed;18AIalsoflaggedresting. Tracksectionpointerchecks pass all45vehicles despite body/track separation up to69.092474m. Nonzero angular values observed on23player/1AIvehicle;units/frame/integration remain unproven. Impact interval unsampled.'
for row in rows:
    if row['id'].startswith('evaluation.'):
        row['evidence'].extend(['COLLISION-STATE-FINDINGS.md','captures/post-red-collision-evaluation-01/evaluation.json','captures/collision-exit-evaluation-01/evaluation.json'])
        row['limitations']+=' Later exit test observes one active speed episode becoming one completed22.4140625s record,UI22s;operational-error/condition lists remainempty. This only validates the specific speed-episode lifecycle,not every evaluation writer or a generic collision record.'
physical_evidence=['PHYSICAL-REGISTRY-FINDINGS.md','pass217-byte-verification.json','pass218-byte-verification.json','captures/physical-registry-paused-01/registry.json']
for ident,meaning,typ,unit,method in [
 ('car.physical_registry','Physical-object list independently of train-owned consist chains','object list','objects','manager=[0x7bdecc]; sentinel=[manager+0x18]; node+8 indexes [0x828108] with stride8'),
 ('car.native_kind','Native vehicle class discriminator','uint32','opaque native kind','Resolve class from object first-word table index; method0x14 slot at class+0xb4; verified return targets005f15ac=>0x4000e engine,0063465b=>0x4000d wagon; never invoke method'),
 ('car.object_id','Native vehicle identifier used by object lookup and save references','uint32','opaque ID','verified wagon/engine object+0x50; lookup006347ef searches physical list')]:
    add(ident,meaning,'player and physical AI; detached/static applicability unvalidated',typ,unit,method,physical_evidence,
        'native consumers and exact constant-return methods traced;45paused objects match connected train membership',
        'physical object creation/removal and load reconstruction;no persistent identity guarantee',
        common+' Fourengines/41wagons observed. No physical objects outside train chains in this fixture. Unknown method targets remain unknown;do not decode vehicle fields from arbitrary table objects. Stable roots/links do not establish atomicity or exhaustive static/detached coverage.')
for row in rows:
    if row['id'] in {'car.identity','car.train_owner','car.links','car.body_pointer'}:
        row['evidence'].extend(physical_evidence)
        row['limitations']+=' Independent physical-list probe matches45connected player/AIcars;no positive detached/static fixture yet.'
lifecycle_evidence=['PHYSICAL-REGISTRY-LIFECYCLE.md','pass217-byte-verification.json','pass222-byte-verification.json','pass223-byte-verification.json','pass224-byte-verification.json','pass225-byte-verification.json','captures/physical-registry-lifecycle-paused-01/registry.json']
for ident,meaning,typ,unit,method in [
 ('car.physical_registry_stored_count','Stored manager physical-object list count','uint32','objects','[[0x7bdecc]+0x1c]'),
 ('car.registered_bit','Object registration flag used by insertion and teardown','bool','boolean','(uint32[verified vehicle+0x18] & 4) != 0')]:
    add(ident,meaning,'physical objects;player and AI vehicles observed',typ,unit,method,lifecycle_evidence,
        'insertion/removal consumers traced;45paused vehicles have bit4 and storedcount45',
        'list registration/removal;can precede completed initialization',
        common+' Not a load-complete or coherent-read gate. Cleanup clears bit after removal request even if no node found. No live count/bit transition or detached/static fixture yet.')
for row in rows:
    if row['id']=='car.physical_registry':
        row['evidence'].extend(lifecycle_evidence)
        row['limitations']+=' Insertion precedes later setup;listnodes are recycled by native unlink helper. Never cache node addresses as stable identities.'
wheel_evidence=['WHEEL-ADHESION-FINDINGS.md','pass228-byte-verification.json','pass229-byte-verification.json','adhesion-constant-map.json','pass229/0062c679.asm','pass229/0062da12.asm','pass58/00614c8e.asm']
for ident,meaning,applies,unit,method in [
 ('car.wheel_rate_stored','Stored ordinary wheel angular-rate candidate','physical vehicles;player/AI update applicability unvalidated','rad/s from speed/radius formula;animation use unvalidated','float32 car+0x1b0;ordinary branch divides longitudinal speed by definition+0x448;excess-braking branch can zero it'),
 ('engine.driver_rotation_rate','Stored powered driver rotation-rate candidate','powered vehicles;player/AI update applicability unvalidated','rev/s formula candidate;slip branches unvalidated','float32 engine+0x2b2;ordinary branch speed/(2*engine_definition112*pi);other branches zero or force-excess adjusted'),
 ('engine.adhesion_force_limit','Stored powered-vehicle adhesion limit candidate','powered vehicles;player/AI update applicability unvalidated','N candidate from mass*gravity*coefficient','float32 engine+0x2aa;producer0062c679 includes coefficient and denominator max(engine_definition integer11a,1)')]:
    add(ident,meaning,applies,'float32',unit,method,wheel_evidence,
        'native producers and selected constants verified;no live field or transition observation in this checkpoint',
        'vehicle force update;caller eligibility and AI refresh remain unvalidated',
        common+' Formula evidence is not an actual wheel/rail force or visible rotation sensor. Ordinary wheel rate,driver rate and body velocity differ by branches/phase. Weather helper uses context definition separately from car definition;do not substitute source comments for sorted loaded Adheasion values.')
wheel_followup=['WHEEL-ADHESION-FINDINGS.md','pass230-byte-verification.json','pass232-byte-verification.json','adhesion-constant-map.json','pass232/00637dc4.asm']
add('engine.driver_animation_phase','Stored powered-driver animation phase accumulator',
    'powered vehicles with eligible shape/animation branch;AI runtime applicability unvalidated',
    'float32','native animation phase units;not radians or validated frame index',
    'car+0x1dc;00637dc4 adds frame_delta[828fb4]*engine2b2*selected definition4e8 factor;orientation bit can negate factor',
    wheel_followup,'native consumer/store verified;no live phase or visual-transition observation',
    'eligible animation update;shape type5,definition powered,car80bit800 and other prerequisites',
    common+' Default versus local definition multiplier selected by definition90bit10. No wrap proven in this branch;downstream mapping/render submission and pause/AI cadence unvalidated.')
for row in rows:
    if row['id'] in {'engine.driver_rotation_rate','engine.adhesion_force_limit','car.wheel_rate_stored'}:
        row['evidence'].extend(wheel_followup)
        row['limitations']+=' Follow-up confirms shared-simulation vtable callback context and powered-rate use in animation accumulator1dc;this does not establish all-callsite/AI eligibility or ordinary-wheel consumer semantics.'
for row in rows:
    if row['id'] in {'engine.driver_rotation_rate','engine.adhesion_force_limit'}:
        row['evidence'].extend(['engine-wheel-parser-map.json','map_engine_wheel_parser.py','pass58/0061949d.asm'])
        row['limitations']+=' Selected engine parser dispatch confirms definition112 is WheelRadius and definition11a is native NumWheels;NumWheels is not established as axle count. Loaded values and live transitions remain unobserved.'
    if row['id']=='engine.driver_animation_phase':
        row['evidence'].extend(['wheelset-parser-map.json','map_wheelset_parser.py','pass234-byte-verification.json','pass234/00639549.asm'])
        row['limitations']+=' Multiplier definition4e8 is parsed from Wheelset. Parser declaration8cbit10 versus runtime override90bit10 propagation unresolved. Setup00639549 clears phase and passes innercar1c4 to shape virtual44;inner phase offset18 is a tracing lead,not verified downstream interpretation.'
shape_animation_evidence=['WHEEL-ADHESION-FINDINGS.md','driver-animation-callback-map.json','shape-animation-method-map.json','pass235-byte-verification.json','pass236-byte-verification.json','pass238-byte-verification.json','pass239-byte-verification.json','pass240-byte-verification.json','pass241-byte-verification.json','pass239/006a54d0.asm','pass239/006d6200.asm','pass240/006a5fd0.asm','pass241/range.asm']
for ident,meaning,method,lifecycle in [
    ('car.shape_animation_time','Stored current shape animation scalar','float32 [[car+0x10]+0x94];require type5 shape and supported initialized virtual table','shape setter and interpolation may change scalar'),
    ('car.shape_animation_processed_time','Stored previous processed shape animation scalar','float32 [[car+0x10]+0x90];require type5 shape and supported initialized virtual table','dispatcher copies current scalar when processed range ends at animation node count')]:
    add(ident,meaning,'vehicles with type5 shape;player/AI live applicability unvalidated','float32','native animation time units;conversion to seconds/frames unresolved',method,shape_animation_evidence,
        'native constructor/setter/dispatch traced and bytes verified;no loaded shape values sampled',lifecycle,
        common+' Embedded animation object begins at shape+0x8c. Current and processed values are distinct from car+0x1dc driver accumulator. Equality is not proof of full rendering,visibility or gameplay freshness. Interpolation can clamp/loop current scalar;not vehicle accumulator. Null/unloaded shape means unavailable. No AI/paused update cadence established.')
for row in rows:
    if row['id']=='engine.driver_animation_phase':
        row['evidence'].extend(shape_animation_evidence)
        row['limitations']+=' Wheel/rod callback6390cf reads inner18 and passes phase to type5 setter6a5fd0,which stores shape94;downstream interpolation may mutate that separate scalar. Shape90 is processed-time cache,not the descriptor duration compared by callback.'
for row in rows:
    if row['id'] in {'car.shape_animation_time','car.shape_animation_processed_time'}:
        row['units']='animation seconds from key Frame/FrameRate formula;not validated against live wall/game time'
        row['evidence'].extend(['animation-time-token-map.json','pass242-byte-verification.json','pass243-byte-verification.json','pass243/006d51d0.asm','pass243/006d5550.asm'])
        row['limitations']+=' Loader second animation integer supplies reciprocal rate;zero rate maps parsed key times to zero. Open Rails ShapeFile format names corroborate Frame/FrameRate;native arithmetic is independently traced. Initializer zeros current/processed scalars. Render/gameclock cadence remains separate.'
for row in rows:
    if row['id'] in {'car.wheel_rate_stored','engine.driver_rotation_rate','engine.adhesion_force_limit','engine.driver_animation_phase','car.shape_animation_time','car.shape_animation_processed_time'}:
        row['evidence'].extend(['read_wheel_animation.py','test_wheel_animation.py','captures/wheel-animation-availability-01/wheel-animation.json'])
        row['limitations']+=' Standalone wheel probe has six synthetic coherence/rejection checks and a live manager-null availability capture;populated native branch is not yet validated. Reread flags detect some changes,not atomic snapshots or ABA address reuse.'
for row in rows:
    if row['id'] in {'car.wheel_rate_stored','engine.driver_rotation_rate','engine.adhesion_force_limit','engine.driver_animation_phase','car.shape_animation_time','car.shape_animation_processed_time'}:
        row['evidence'].extend(['wheel-runtime-summary.json','analyse_wheel_runtime.py','capture_wheel_sequence.py','captures/wheel-animation-loaded-01/wheel-animation.json','captures/wheel-animation-after-motion-01/wheel-animation.json','captures/wheel-moving-opening-01/samples.jsonl','captures/wheel-moving-player-ai-01/samples.jsonl'])
        row['evidence_status']+='; populated player/AI reads and short moving sequences retained'
        row['limitations']=row['limitations'].replace('Loaded values and live transitions remain unobserved.','Loaded values and short moving observations are now retained; see wheel-runtime-summary.json.').replace('populated native branch is not yet validated.','populated native reads now retained with stable sampled identities.')
        row['limitations']+=' Cab-view sequences: 80 samples (9 unpaused) then 50 (5 unpaused); unsampled motion tails precede final pauses. Player/AI engine rates changed; player adhesion cache 668360.0625 versus AI zero. All four engine driver accumulators stayed zero while shape times stayed near zero. These do not prove physical slip, visible wheel animation, zero AI force, or general update cadence.'
for row in rows:
    if row['id'] in {'engine.driver_animation_phase','car.shape_animation_time','car.shape_animation_processed_time'}:
        row['evidence'].extend(['captures/wheel-external-view-01/samples.jsonl','captures/wheel-gates-external-paused-02/gates.json','read_wheel_gates.py'])
        row['limitations']+=' External-view follow-up: 180 samples,25 unpaused,all45vehicles stable; all four driver phases remain zero. Paused car+80 flags equal1,so required bit0x800 is absent for the traced powered driver-phase branch. Default Wheelset is0.3000000119. This branch is ineligible at the sampled state; other wheel animation paths and eligibility transitions remain open. Initial gates-01 read kind with wrong width; corrected gates-02 uses native byte+88.'
for row in rows:
    if row['id'] in {'car.shape_animation_time','car.shape_animation_processed_time'}:
        row['evidence'].extend(['pass250-byte-verification.json','pass250/range.asm','pass253-byte-verification.json','pass253/00405694.asm'])
        row['limitations']+=' Native animation tail deliberately cycles shape94 through0/epsilon/2epsilon to trigger processing. It is not necessarily elapsed playback time. Live entry405694 is redirected; original native body alone does not prove full live behavior.'
    if row['id']=='car.wheel_rate_stored':
        row['evidence'].extend(['pass254/005d5381.asm','pass254-byte-verification.json','pass255/005d55b5.asm','pass255-byte-verification.json','pass256/005d5684.asm','pass256-byte-verification.json','captures/wheel-hook-provenance-01/provenance.json'])
        row['units']='rad/s from speed/radius producer and rate*frame_delta FSINCOS transform consumer'
        row['limitations']+=' Ordinary callback5d5381 reads car through callbackdata+4,negates by car84bit4,and when callbackdata byte2bit1 is set rotates supplied transform using rate*frame_delta. No accumulated angle stored here. Live callback entry is redirected; NEMT source has matching crawl hook sites and conditional temporary rate replacement for eligible derailed vehicles,but binary attribution/full hook execution remain unverified.'
node_evidence=['WHEEL-ADHESION-FINDINGS.md','read_wheel_nodes.py','captures/wheel-node-registration-02/nodes.json','pass239/006d6200.asm','pass242/006d6100.asm','pass257-byte-verification.json','pass257/00403512.asm']
for ident,meaning,value_type,units,extraction in [
    ('car.shape_node_count','Stored animation node count','uint32','nodes','uint32 shape+0x98 for guarded type5shape'),
    ('car.shape_node_callbacks','Per-node animation callback bindings and ordinary-wheel context','array of structures','addresses/raw flags/node indices','16byte records at [shape+0xa0]+node*16;callback,data,two key cursor words. Verified wheel stub403512->5d5381 uses data byte2bit1 and car pointerdata+4.'),
    ('car.shape_node_transform','Stored per-node animation transform','float32[12] per node','rotation coefficients;translation coordinate units not independently validated','48byte transform at [shape+0x9c]+node*48;current probe samples verified ordinary-wheel nodes only')]:
    add(ident,meaning,'player/AI vehicles with supported type5shape;positive fixture four locomotives',value_type,units,extraction,node_evidence,
        'native slot/transform layout traced;paused four-engine snapshot with24wheel nodes and matching owners',
        'allocated with animation object;dispatcher and callbacks can update node transforms;cadence/reload untested',
        common+' Snapshot has18nodes per engine,6ordinary wheel callbacks each,allwheel flags byte2=7. Other41vehicles unsupported by this type5probe,not absent animation. Identity/slot/data rereads are not atomic or ABA-proof;transforms not reread. Raw matrix is not world pose or guaranteed visible wheel angle. Firstprobe missed thunk callbacks and conflated unsupported shapes with errors;secondcorrected. Wheel targetentry is hooked inliveprocess;binary attribution and finalrendering remain open.')
add('car.wheel_transform_groups','Type-4 per-vehicle wheel transform groups','player/AI type4vehicles;positive fixture41wagons','two grouped structures','raw flags/pointers;12float matrices;rotation parameters with incomplete axis/unit mapping',
    'group=car+0xb0+index*0x3c,index0..1;owner+4,flagsbyte2,base matrixpointer+0x14,three optionalwheelmatrixpointers+0x18..0x20;rotationparameters+0x24/+0x28',
    ['WHEEL-ADHESION-FINDINGS.md','read_type4_wheels.py','captures/type4-wheel-transforms-01/wheels.json','pass232/00637dc4.asm','pass253/00405694.asm','pass257-byte-verification.json','pass258/005d52d1.asm','pass258-byte-verification.json'],
    'native bounded type4branch and base-transform consumer traced;paused41vehicle snapshot reads82groups164wheelmatrices82basematrices',
    'native type4update directly supplies groupcontext and matrix to callbacks;allocation/reload/moving cadence untested',
    common+' All82groups flagsbyte2=7,ownerlinks match;all sampled contexts/matrices/identities stable. Missing matrix pointers mean unavailable,not zero pose. Consumer5d52d1 gates on byte2bit2 and nonzero rotation parameters,preserves translation while rebuilding basis. Matrix coordinate space/physical wheel-angle mapping unvalidated. Native wheelentry5d5381 is hooked;do not infer full live execution from diskbody. Two groups/threewheel slots are this native branch layout,not universal wheel counts. Sequential snapshots are not atomic or ABA-proof.')
for ident,label,offset,definition_offset in [('aws','AWSMonitor',0x4ba,0xb0c),('vigilance','VigilanceMonitor',0x4fa,0xb78),('emergency_stop','EmergencyStopMonitor',0x53a,0xbe4),('overspeed','OverspeedMonitor',0x5ba,0xcbc)]:
    add('engine.'+ident+'_monitor_state',label+' runtime state','engine with validated definition link;positive player lead,unavailable trailing/AI fixture','structured native state','raw enable/action words;remaining scalar bits retain unknown units',
        f'engine+{offset:#x},64bytes;enable+0,action-state+4,rawstate+8..+38,definitionpointer+3c expected engine_definition+{definition_offset:#x}',
        ['ENGINE-MONITOR-FINDINGS.md','monitor-definition-map.json','map_monitor_definitions.py','read_engine_monitors.py','captures/engine-monitor-state-01/monitors.json','pass259-byte-verification.json','pass259/005f212d.asm','pass259/0060f99b.asm','pass260-byte-verification.json','pass260/0060f8b0.asm','pass260/006107a0.asm'],
        'native parser/initializer/selected consumers traced and bytes matched;paused lead-state snapshot',
        'initializer/reset and controller overrides traced;countdown/action transitions and reload lifecycle unvalidated',
        common+' Null definition link means unavailable. Enable word does not prove enforcement;action word0 is not measured absence of brake/power intervention. Trailing player and both AI engines have null links in tested fixture. Raw timers/state words not all named;no event history or audible alarm claim. Sequential rereads are not atomic. Four save helper slots do not correspond one-to-one to these four named devices;overspeed is at5ba,not57a.')
for row in rows:
    if row['id'] in {'engine.aws_monitor_state','engine.vigilance_monitor_state','engine.emergency_stop_monitor_state','engine.overspeed_monitor_state'}:
        row['evidence'].extend(['monitor-timing-summary.json','analyse_monitor_timing.py','captures/engine-monitor-timing-paused-01/monitors.json','STEAM-PRODUCER-FINDINGS.md','AI-SYSTEM-UPDATE-FINDINGS.md','pass267-byte-verification.json','pass268-byte-verification.json','pass269-byte-verification.json','pass267/005f5630.asm','pass268/00607bd0.asm','pass269/005f9285.asm','pass265-byte-verification.json','pass265/00610153.asm','pass265/005ea220.asm','pass266-byte-verification.json','pass266/0061004a.asm','pass266/0060fce3.asm','monitor-parameter-map.json','engine-monitor-state-summary.json','analyse_engine_monitors.py','pass263-byte-verification.json','pass263/0060fa46.asm','pass264-byte-verification.json','pass264/00610623.asm'])
        row['extraction']+=';cached trigger words+24speed,+28current,+2clow reservoir,+30RPM,+34track speed;reset-loaded scalars+10monitor limit,+14alarm limit,+18penalty limit,+1calarm-before-overspeed'
        row['limitations']+=' Trigger branches can skip writes when definition thresholds are disabled,so caches are not universal current-condition flags. RPM branch uses engine maximumRPM+1 with configured trigger value only as enable;speed threshold multiplies by2.236936092. Preserve these native formulas rather than silently substituting expected conversions. Any nonzero trigger invokes helper setting+4/+8/+c to1. Countdown producers00610153/0061004a subtract caller-supplied float delta before the enable gate;reset helpers may overwrite them in the same invocation. Diesel delta is player train+8e fixed engine interval;effective simulation seconds inherit shared-scheduler steam runtime corroboration. Direct monitor cadence/intervention remain unvalidated. Diesel overspeed state+20 caches absolute(speed*2.236936092) in mph even when disabled;it need not equal current speed at sample time.'
add('engine.unnamed_monitor_slot3_state','Unnamed fifth engine monitor runtime state','validated engine definition link;positive player lead,unavailable trailing/AI fixture','structured native state','raw words and float countdown/input fields;subsystem name unverified',
    'engine+0x57a,64bytes;definition+0x3c must equal engine_definition+0xc50;enable+0,action+4,alarm+8,penalty latch+c,countdowns+10/+14/+18/+1c,input+20,triggers+24..+34',
    ['ENGINE-MONITOR-FINDINGS.md','read_engine_monitors.py','captures/engine-monitor-timing-paused-01/monitors.json','pass259/005f212d.asm','pass259/00585e59.asm','pass259-byte-verification.json','pass265/005ea220.asm','pass265-byte-verification.json','pass270/0060f839.asm','pass270-byte-verification.json','map_unnamed_monitor.py','unnamed-monitor-map.json'],
    'native layout,initializer disable and diesel conditional current trigger traced;paused disabled state read with valid definition',
    'diesel update path uses shared monitor updater;initialization explicitly disables this slot;actual enable/trip/reload transitions unvalidated',
    common+' No native subsystem name established;do not relabel as overspeed or circuit breaker. Initializer controller kinds2/3 explicitly clear enable through0060f839 after definition link. Diesel caller triggers when enabled and current exceeds engine_definition+1da times1.0199999809265137;no trip observed. Snapshot has enable/action0,expected link,stable state/config rereads;other engines null links are unavailable. Generic updater can mutate fields before enable gate. No independent AI simulation or actual protection claim. Structured candidate intentionally retains uncertainty rather than omitting a readable surface.')
for row in rows:
    if row['id'] in {'engine.aws_monitor_state','engine.vigilance_monitor_state','engine.emergency_stop_monitor_state','engine.overspeed_monitor_state','engine.unnamed_monitor_slot3_state'}:
        row['evidence'].extend(['sample_monitor_cadence.py','analyse_monitor_cadence.py','monitor-running-opening-01-summary.json','captures/monitor-running-opening-01/samples.jsonl','read_monitor_caller_gates.py','captures/monitor-caller-gates-paused-01/gates.json'])
        row['limitations']+=' Opening run1197samples:disabled overspeed input changed150times;vigilance enable1 yet timers25/17 unchanged. Post-run caller globals790d88/790d8c both1,which suppress their update branches. Gates not sampled throughout run. No observed action/alarm/penalty latch or paused-state changes;no live countdown-rate or intervention proof.'
for ident,label,address in [('vigilance_update_suppressed','Vigilance update suppression gate',0x790d88),('aws_update_suppressed','AWS update suppression gate',0x790d8c)]:
    add('session.'+ident,label,'local player monitor update paths;not AI intent','uint32','zero permits caller branch;nonzero suppresses it',
        f'absolute {address:#x} for pinned executable;alerter command004a5509 toggles zero/nonzero',
        ['ENGINE-MONITOR-FINDINGS.md','pass271-byte-verification.json','pass271/004a5509.asm','pass271/00406df0.asm','pass272-byte-verification.json','pass272/004a40cb.asm','alerter-command-map.json','map_alerter_command.py','sample_monitor_cadence.py','captures/monitor-alerter-toggle-01/samples.jsonl','monitor-alerter-toggle-01-summary.json','pass265/005ea220.asm','pass265-byte-verification.json'],
        'native alerter handler and suppression branches traced;running/paused gate sampled1',
        'global command-controlled gate;successful toggle and initialization/persistence not validated',
        common+' Independent of per-monitor enable word. Command toggles both gates and changes player overspeed enable to0x40000000 when vigilance gate0,otherwise0. Ctrl+numpad4 declaration exists but tested keypress produced no sampled toggle;do not claim successful dispatch or settings persistence. No direct monitor decrement/intervention observation.')
for row in rows:
    if row['id'] in {'engine.vigilance_monitor_state','session.vigilance_update_suppressed','session.aws_update_suppressed','evaluation.operational_error_count','evaluation.operational_error_records'}:
        row['evidence'].extend(['ENGINE-MONITOR-FINDINGS.md','captures/monitor-alerter-enabled-01/samples.jsonl','monitor-alerter-enabled-01-summary.json','analyse_monitor_enabled.py','monitor-enabled-events.json','captures/alerter-penalty-evaluation-01/evaluation.json','captures/monitor-options-restored-01/gates.json'])
        row['limitations']=row['limitations'].replace('Direct monitor cadence/intervention remain unvalidated.','').replace('No direct monitor decrement/intervention observation.','').replace('no live countdown-rate or intervention proof.','no countdown proof in that disabled run.')
        row['limitations']+=' UI-enabled follow-up validates player vigilance quarter-step countdown,alarm/action rising edges and penalty brake response;UI evaluation and code2 record agree. Gates0 during1397sample run;original Alerter option restored with gates1 after reload. Timers continue negative after latching. This does not validate every monitor,AI,acknowledgement,audio or process-restart option persistence.'
        row['evidence_status']+=';UI-enabled player vigilance penalty sequence and retained evaluation record observed'
for row in rows:
    if row['id'] in {'car.shape_node_transform','car.wheel_transform_groups'}:
        row['evidence'].extend(['sample_wheel_matrices.py','analyse_wheel_matrices.py','wheel-matrix-moving-01-summary.json','wheel-matrix-player-ai-01-summary.json','captures/wheel-matrix-moving-01/samples.jsonl','captures/wheel-matrix-player-ai-01/samples.jsonl'])
        row['evidence_status']+=';two moving/paused series validate representative player/AI locomotive and wagon matrix transitions'
        row['limitations']+=' Dynamic follow-up samples one representative per player/AI/type4/type5 class. AI locomotive114/wagon76 matrix changes have stable endpoints;player wagon has2then1context reread differences,reported separately. No changes between consecutive paused samples. Matrix rereads agree but sequential snapshots are not atomic;angles,axes,frame cadence,world pose and visible rendering remain unvalidated.'
for row in rows:
    if row['id'] in {'body.force_accumulator_candidate','body.torque_accumulator_candidate'}:
        row['evidence'].extend(['WHEEL-ADHESION-FINDINGS.md','read_body_accumulators.py','analyse_body_accumulators.py','body-accumulators-summary.json','captures/body-accumulators-paused-01/accumulators.json','pass273/0062e5d6.asm','pass273-byte-verification.json'])
        row['evidence_status']=row['evidence_status'].replace('independent AI population untested','independent AI force evolution unvalidated')+';guarded paused capture covers23player and22AI bodies with stable local rereads'
        row['limitations']+=' Resistance contribution is summed into body+a0 alongside other force contributions;not a standalone drag measurement. All23player forces nonzero,22AI forces zero despite nonzero AI velocity;all45torques zero. These values do not establish absent AI resistance or physical torque. Moving cadence,solver phase,decomposition and AI dynamics remain unvalidated;sequential checks are not atomic.'
# Consolidate current lifecycle statements after chronological evidence additions.
for row in rows:
    if row['id']=='engine.vigilance_monitor_state':
        row['update_or_lifecycle']='Player UI-enabled run observed 0.25 countdown decrements, alarm/action rising edges and penalty brake response; initializer/reset paths traced. Acknowledgement, complete reload restoration and other monitor interventions remain unvalidated.'
        row['units']='Enable/action/alarm/latch words; countdown floats use caller engine simulation interval (seconds), distinct from activity-clock elapsed time; other cached inputs retain field-specific or unresolved units'
        row['limitations']+=' Enabled capture contains one differing vigilance reread away from the reported event edges; no claim of wholly stable or atomic capture.'
    elif row['id'] in {'session.vigilance_update_suppressed','session.aws_update_suppressed'}:
        row['update_or_lifecycle']='Global command/settings gate. Normal UI Alerter enable plus activity restart yielded0; restoring the option plus restart yielded1. Exact write timing, process-restart persistence and shortcut dispatch remain unvalidated.'
        row['limitations']=row['limitations'].replace('do not claim successful dispatch or settings persistence.','do not claim successful shortcut dispatch or process-restart persistence.')
    elif row['id']=='car.shape_node_transform':
        row['update_or_lifecycle']='Allocated with animation object; dispatcher/callback updates traced. Representative player/AI type5 wheel matrices changed during motion and stayed unchanged between consecutive paused samples. Exact frame cadence, allocation/reload lifetime and other node classes remain unvalidated.'
        row['limitations']=row['limitations'].replace('transforms not reread.','initial paused node probe did not reread transforms; subsequent moving probe did.')
    elif row['id']=='car.wheel_transform_groups':
        row['update_or_lifecycle']='Native type4 branch directly supplies group context and matrices to callbacks. Representative player/AI wagon wheel matrices changed during motion and stayed unchanged between consecutive paused samples. Exact frame cadence and allocation/reload lifetime remain unvalidated.'
add('car.collision_callback_state','Collision-object callback binding and unnamed stored state','guarded physical player/AI vehicles;positive fixture23player22AI','structured uint32 callback pointer and state','address and unnamed state code',
    'car+0x74 callback pointer;car+0x78 uint32 state;save encoder maps two table entries at0x7a09b0 to0/1 and special stubs402bc6/401dbb to100/101',
    ['COLLISION-CALLBACK-FINDINGS.md','map_collision_callbacks.py','collision-callback-map.json','read_collision_callbacks.py','captures/collision-callback-paused-01/callbacks.json','pass275-byte-verification.json','pass276-byte-verification.json','pass275/005e143c.asm','pass210/005e2534.asm'],
    'disk/live callback table and stubs agree;selected native targets verified;45vehicle paused capture has callback402bc6,state5 and stable local rereads',
    'serialized state;callback005e143c has a conditional state2 writer;initialization,other writers and live transitions unvalidated',
    common+' Callback binding is not a collision event or invocation count. Three mapped targets return0 without state writes. Current45vehicles select one of these targets. State5 meaning unknown;state2 branch not observed. No damage,derailment,contact count,impact speed or AI collision simulation claim. Raw pointers are process-specific;sequential rereads not atomic. No deliberate collision performed.')
for row in rows:
    if row['id']=='car.collision_callback_state':
        row['meaning']='Collision flags and callback binding (native CollideFlags/CollideFunction)'
        row['units']='Process callback address (or mode-dependent index);uint32 collision bitmask'
        row['evidence'].extend(['map_collision_tokens.py','collision-token-map.json','pass277-byte-verification.json','pass277/005e1ef3.asm','pass277/005e2411.asm','pass277/005fb0fd.asm','pass277/005df360.asm'])
        row['evidence_status']+=';native parser labels,flags consumers,initializer and load callback reconstruction traced and byte-verified'
        row['update_or_lifecycle']='Initializer clears flags;parser loads CollideFlags and ORs0x200;pair-processing code tests masks and may set0x80. Save loader rebuilds callback from code and restores flags. Actual reload/flag transitions unvalidated.'
        row['limitations']+=' Follow-up establishes state is a bitmask;stored5 sets0x1/0x4 but full bit meanings remain unknown. Callback+74 can hold a raw index when global7be0f8!=0. Null/unrecognized restored callback is unavailable. Static reconstruction does not prove live reload fidelity or invocation;do not reuse raw pointer as persistent identity.'
for row in rows:
    if row['id'] in {'car.collision_callback_state','body.position','body.velocity','body.angular_velocity'}:
        row['evidence'].extend(['COLLISION-CALLBACK-FINDINGS.md','map_collision_point_velocity.py','collision-point-velocity-map.json','pass278-byte-verification.json','pass278/005e1561.asm','pass278/005e15b5.asm','pass278/005e150d.asm','pass276/005e17a0.asm'])
        row['limitations']+=' Collision table callback computes selected body velocity + angular_velocity cross(point-position),compares squared magnitude to49. At initial pair construction,body selection is opposite the object receiving flags2;later helper005df0b8 can swap bodies/callbacks without objects,so attribution is phase-dependent. Not relative impact speed or observed damage. Current45vehicle fixture uses a different callback. Point validity,frame agreement and actual invocation remain unvalidated.'
add('physics.collision_work_buffer','Transient collision processing buffer','global physical collision machinery;player/AI record attribution requires validated object links','structured header and bounded raw records','pointer,count,capacity;record field units incomplete',
    'globals80a76c pointer,80a770 count/construction index,80a774 capacity;stride0x62;record object pointers+4/+8,body pointers+c/+10,callbacks+14/+18;raw remaining bytes',
    ['COLLISION-CALLBACK-FINDINGS.md','read_collision_buffer.py','captures/collision-buffer-paused-01/buffer.json','pass279-byte-verification.json','pass280-byte-verification.json','pass279/005f47e8.asm','pass279/005def40.asm','pass279/005df0b8.asm','pass279/005f49f9.asm','pass280/00629dbc.asm'],
    'allocation,rebuild,mutation and teardown traced;paused positive header with count0/capacity4000;no populated runtime record validation',
    'builder resets count and reconstructs records;later processing mutates them;capacity can grow,teardown nulls buffer without explicit count reset',
    common+' Scratch buffer is not collision history or guaranteed current contacts. Count is also construction index during rebuild. Null buffer means unavailable even if stale count remains. Probe caps128records and does not dereference pointers. Body/callback pairs can swap without object pointers swapping;phase-dependent attribution. Sequential rereads not atomic;empty fixture provides no contact semantics or AI simulation proof.')
for row in rows:
    if row['id']=='physics.collision_work_buffer':
        row['evidence'].extend(['pass281-byte-verification.json','pass281/005f952e.asm','map_collision_generation_stub.py','collision-generation-stub-map.json'])
        row['extraction']+=';record dword0 bit0x1 set/cleared by005f952e according to caller+44==1'
        row['limitations']+=' Post-builder005f952e only changes record flags and makes no callbacks;record flags differ from vehicle CollideFlags. Exact stub4038c3 is JMP despite stored CALL reference. Misaligned pass283 is rejected as instruction evidence. Callback invocation remains unresolved.'
for row in rows:
    if row['id'] in {'car.brake_cylinder_pressure','car.brake_pipe_pressure'}:
        row['evidence'].extend(['SIGNAL-APPROACH-BRAKING-FINDINGS.md','analyse_signal_approach_emergency.py','signal-approach-emergency-summary.json','emergency-binding-provenance.json','captures/signal-approach-emergency-01/samples.jsonl','captures/approach-stopped-signal-01/details.jsonl'])
        row['evidence_status']+=';preferred diesel fixture UI emergency stop captured across23player/22AI cars'
        row['limitations']+=' Emergency capture1268samples:player pipe90->0,cylinder0..85.20245PSI,speed reaches0;AI pipe90/cylinder0 unchanged. Owner rereads agree but170clock-crossing samples prevent atomicity/propagation timing claims. No diesel release or successful signal passage yet.'
for row in rows:
    if row['id'] in {'car.brake_cylinder_pressure','car.brake_pipe_pressure','signal.next_distance','signal.aspect','signal.aspect_speed','signal.aspect_flags'}:
        row['evidence'].extend(['SIGNAL-APPROACH-BRAKING-FINDINGS.md','analyse_diesel_emergency_reset.py','diesel-emergency-reset-summary.json','diesel-brake-cab-provenance.json','captures/diesel-emergency-reset-01/samples.jsonl','captures/diesel-reset-signal-paused-01/details.jsonl'])
        row['limitations']+=' Stopped-player follow-up3316samples:brake selector reachesSelfLap98%,not release;732clock-crossing reads. Endpoint signal46 changes aspect0->7 while distance481.9824m and speed0 remain unchanged;AI visibly passed but exact clearance time/exclusive causality unmeasured. No successful player passage.'
for row in rows:
    if row['id'] in {'car.brake_cylinder_pressure','car.brake_pipe_pressure','train.speed','signal.next_distance'}:
        row['evidence'].extend(['SIGNAL-APPROACH-BRAKING-FINDINGS.md','analyse_diesel_release_rollback.py','diesel-release-rollback-summary.json','captures/diesel-keyboard-release-01/samples.jsonl','captures/cleared-player-approach-01/details.jsonl'])
        row['limitations']=row['limitations'].replace('No diesel release or successful signal passage yet.','No release in that emergency-stop capture;later keyboard series validates diesel release. Successful signal passage remains untested.')
        row['limitations']+=' Later diesel keyboard release yields mode4,pipe90/cylinder0 and negative signed motion while signal46distance increases;cab displays speed magnitude and forward reverser. Emergency reapplication stops rollback. Sampled traction current remains0 even withN1;cause unresolved. No forward signal passage or exclusive grade causality claim.'
for row in rows:
    if row['id']=='engine.emergency_stop_monitor_state':
        row['evidence'].extend(['DIESEL-EFFORT-GATE-FINDINGS.md','read_diesel_effort_gates.py','analyse_diesel_acknowledgement.py','diesel-acknowledgement-summary.json','diesel-acknowledgement-binding.json','captures/diesel-acknowledgement-01/samples.jsonl','captures/diesel-effort-gates-paused-01/gates.json','captures/diesel-effort-after-ack-01/gates.json','pass285-byte-verification.json','pass285/005ead0d.asm','pass285/006107a0.asm'])
        row['limitations']=row['limitations'].replace('Direct monitor cadence/intervention remain unvalidated.','Emergency acknowledgement is now observed;other monitor intervention claims remain scoped to their own evidence.')
        row['evidence_status']+=';UIZ acknowledgement clears emergency action/alarm/penalty with stable local rereads;subsequentN1current225A observed'
        row['update_or_lifecycle']='Native emergency action/CutsPower and controller370 gate pre-current effort. UI acknowledgement observed clearing action/alarm/penalty;full reload and other reset conditions unvalidated.'
        row['limitations']+=' Follow-up1397samples validates emergency acknowledgement,not earlier rollback causality. InitialIdle snapshot and subsequentN1snapshot differ in throttle. Cab current is calculated before reverser/optional brake-force cutoff,not actual rail force. After-ack capture paused0 overrides erroneous legacyPaused boilerplate;raw evidence preserved.'
for row in rows:
    if row['id'] in {'signal.next_iterator','signal.next_distance','signal.head_identity','signal.aspect','train.speed'}:
        row['evidence'].extend(['PLAYER-SIGNAL-PASSAGE-FINDINGS.md','analyse_player_signal_passage.py','player-cleared-passage-01-summary.json','player-cleared-passage-02-summary.json','captures/player-cleared-passage-01/details.jsonl','captures/player-cleared-passage-02/details.jsonl'])
        row['evidence_status']+=';forward player next-signal selection transition observed after clearance'
        row['limitations']=row['limitations'].replace('Successful signal passage remains untested.','A later forward run validates a next-signal selection transition;exact geometric passage remains unmeasured.').replace('No successful player passage.','No successful player passage in that earlier capture.').replace('No player node crossing or successful signal passage;activity ended at red.','That earlier capture ended at red without a successful crossing.').replace('No forward signal passage or exclusive grade causality claim.','That rollback capture provides no forward passage or exclusive grade causality claim.')
        row['limitations']+=' LaterN4/release run has positive signed speed and stable-reread iterator transition from node-local46to21 at74410.078125..74410.25;distance7.915m switches to2710.103m. This is next-signal selection,not exact zero-distance or geometric crossing timing. Direction selector0to1 does not indicate train reversal. Two capture series have a55.71875simulation-second gap.'
for row in rows:
    if row['id'] in {'track.node','track.section_index','track.section','track.direction','track.node_distance','track.section_distance','service.posted_speed_cap','service.effective_speed_limit','service.update_active','signal.next_iterator','signal.head_identity','signal.aspect','signal.aspect_speed','signal.aspect_flags'}:
        row['evidence'].extend(['PLAYER-TRACK-CAP-TRANSITION-FINDINGS.md','capture_player_track_caps.py','analyse_player_track_caps.py','player-track-caps-moving-01-summary.json','captures/player-track-caps-moving-01/samples.jsonl','captures/post-signal-track-paused-01/tracks.json'])
        if row['id'].startswith('track.'):
            row['evidence_status']+=';eight matched player car/body pairs cross a node boundary with local direction1to0 during positive motion'
            row['limitations']+=' Later coasting capture validates eight player car node changes,not lead/service crossing:both already on new node at capture start. Node-local distance resets and direction changes;neither is cumulative route distance or universal train direction. Full samples are asynchronous.'
        elif row['id'].startswith('service.'):
            row['evidence_status']+=';AI activation gate0to1 accompanies posted/effective cap initialization;player cap unchanged'
            row['limitations']+=' AIservice3has193gate0samples with effective cache0 while finite-input formula returns fallback26.8224m/s;activation initializes posted/effective13.4112m/s. Other inactiveAIretains an agreeing cap. Gate and lifecycle context required;no player speedpost transition or exact producer invocation established.'
        else:
            row['evidence_status']+=';multiple normal-head fixture aspects4and0 selects4 under traced maximum rule'
            row['limitations']+=' Next iterator21to2..3 observed with stable signal subreads;head2aspect4 and head3aspect0 coexist. Emulated selection is not independent rendered-monitor,appearance or movement-authority validation.'
loose_fixture_path=GAME/'ROUTES/USA2/ACTIVITIES/yard_one.act'
loose_fixture_bytes=loose_fixture_path.read_bytes()
sources[str(loose_fixture_path)]={'sha256':hashlib.sha256(loose_fixture_bytes).hexdigest(),'bytes':len(loose_fixture_bytes)}
for row in rows:
    if row['id'] in {'car.physical_registry','car.native_kind','car.object_id','car.physical_registry_stored_count','car.registered_bit','car.identity','car.train_owner','car.links','car.body_pointer'}:
        row['evidence'].extend(['LOOSE-STOCK-FINDINGS.md','analyse_loose_yard.py','loose-yard-summary.json','captures/loose-yard-notebook-01/registry.json','captures/loose-yard-manager-01/manager.json','captures/loose-fixture-provenance-01/provenance.json','captures/loose-fixture-provenance-01/yard_one.act'])
        row['applicability']='player, physical AI and loaded loose rolling stock; remote/unphysicalized coverage unproven'
        row['evidence_status']+=';positive yard fixture has39owner-null loose vehicles outside train chains in6linked components'
        row['limitations']=row['limitations'].replace('no positive detached/static fixture yet.','that earlier fixture had no loose-stock set difference.').replace('No live count/bit transition or detached/static fixture yet.','No live count/bit transition in that earlier fixture.')
        row['limitations']+=' Yard opening snapshot has40physical objects versus1train-owned player engine;39loose objects have null owner,stable valid bodies and reciprocal links. Component sizes5/3/1/16/13/1 match configured cuts;38wagons and1engine. Exact activity-ID/native-ID join and coupling/detachment transitions remain unvalidated. Null train owner does not invalidate vehicle/body telemetry.'
        if row['id']=='car.identity':row['extraction']='bounded train-chain or independently type-validated physical-registry enumeration; session-local address'
for row in rows:
    if row['id'] in {'track.node','track.section_index','track.section','track.direction','track.node_distance','track.section_distance','track.local_position','track.node_length','track.node_section_count','track.section_definition_index','body.position'}:
        row['evidence'].extend(['LOOSE-TRACK-FINDINGS.md','read_loose_track_context.py','analyse_loose_track_context.py','loose-track-context-summary.json','captures/loose-yard-track-01/context.json','captures/loose-yard-topology-01/topology.json'])
        row['applicability']+=';loaded owner-null loose vehicles validated in paused yard fixture'
        row['evidence_status']+=';39loose vehicle track records have valid node/section joins and bounded distances'
        row['limitations']+=' Paused loose-stock fixture validates40total track joins,39owner-null;body vs trackY differs1.970032..2.833313m and horizontal rounding differences remain. Not a universal offset,track travel distance or coupler gap. No coupling/turnout transition or remote loose-stock coverage inferred.'
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
