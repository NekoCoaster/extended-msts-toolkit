"""Match native item indexes/types to installed TDB definitions, without renaming guesses."""
import json,re,hashlib
from pathlib import Path
from collections import Counter,defaultdict
root=Path(__file__).resolve().parent;p=Path('C:/MSTS/ROUTES/USA2/marias.tdb');raw=p.read_bytes();text=raw.decode('utf-16');asset={}
for m in re.finditer(r'\b(\w+Item)\s*\(',text):
    end=m.end();depth=1
    while depth:depth+=(text[end]=='(')-(text[end]==')');end+=1
    block=text[m.end():end-1];ident=re.search(r'\bTrItemId\s*\(\s*(\d+)\s*\)',block)
    if not ident:continue
    i=int(ident[1])
    if i in asset:raise ValueError(f'Duplicate asset item {i}')
    asset[i]=dict(type=m[1],id=i,fields={x[0]:x[1].strip() for x in re.findall(r'\b(\w+)\s*\(\s*([^()]*)\)',block)})
native=json.loads((root/'captures/infrastructure-paused-01/infrastructure.json').read_text())['infrastructure']['databases'][0]['items']
types=defaultdict(Counter);examples=defaultdict(list);missing=[]
for v in native:
    if v['index'] not in asset:missing.append(v['index']);continue
    a=asset[v['index']];types[v['kind']][a['type']]+=1
    if len(examples[v['kind']])<2:examples[v['kind']].append(a)
absent=sorted(set(asset)-{v['index'] for v in native});checks=Counter();differences=[]
typed=json.loads((root/'captures/track-items-paused-01/items.json').read_text())['items']
def check(ident,key,actual,expected,tolerance=None):
    checks[key]+=1
    equal=abs(actual-expected)<=tolerance if tolerance is not None else actual==expected
    if not equal:differences.append(dict(id=ident,field=key,actual=actual,expected=expected))
for n in typed:
    ident=n['index'];f=asset[ident]['fields']
    if 'TrItemSData' in f:
        value,flags=f['TrItemSData'].split();check(ident,'node_distance',n['node_distance'],float(value),.02);check(ident,'common_flags',n['common_flags'],int(flags,16))
    if 'platform' in n:
        v=n['platform'];flags,pair=f['PlatformTrItemData'].split()
        for key,value in [('name',f['PlatformName'].strip('"')),('station',f['Station'].strip('"')),('flags',int(flags,16)),('paired_item',int(pair)),('waiting_passengers',int(f['PlatformNumPassengersWaiting']))]:check(ident,'platform.'+key,v[key],value)
        check(ident,'platform.minimum_wait',v['minimum_wait'],float(f['PlatformMinWaitingTime']),.001)
    if 'siding' in n:
        v=n['siding'];flags,pair=f['SidingTrItemData'].split()
        for key,value in [('name',f['SidingName'].strip('"')),('flags',int(flags,16)),('paired_item',int(pair))]:check(ident,'siding.'+key,v[key],value)
    if 'speedpost' in n:
        v=n['speedpost'];flags=v['flags'];values=list(map(float,f['SpeedpostTrItemData'].split()));expected=[flags]
        if flags&7 in [1,2] or (flags&7==0 and flags&8):expected.append(v['byte_value'])
        if flags&7==0 or flags&16:expected.append(v['float_value'])
        expected.append(v['angle']);check(ident,'speedpost.serialized_length',len(expected),len(values))
        for j,(a,b) in enumerate(zip(expected,values)):check(ident,'speedpost.value'+str(j),a,b,.002)
out=dict(source=dict(path=str(p),sha256=hashlib.sha256(raw).hexdigest()),native_count=len(native),asset_count=len(asset),missing=missing,asset_only_ids=absent,asset_only_types=dict(Counter(asset[i]['type'] for i in absent)),native_kind_to_asset_type={str(k):dict(v) for k,v in types.items()},examples=dict(examples),field_checks=dict(checks),differences=differences,limitation='Native serializer and current-route asset comparison establish stored payload meaning, not effective restriction or changing platform/passenger behavior.')
(root/'track-item-summary.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['source','examples','asset_only_ids','differences']},indent=2));print('Differences:',len(differences),differences[:4])
