"""Offline model of00690280; never calls or writes into the game."""
import json
from pathlib import Path
root=Path(__file__).resolve().parent
data=json.loads((root/'captures/maryland-records-paused-01/records.json').read_text(encoding='utf-8'))
player=next(s for s in data['services'] if s['address']==0x809890)
records=[r['address'] for r in player['records']]
def successor(items,current):
    if not current:return items[0] if items else 0
    for index,value in enumerate(items):
        if value==current:return items[index+1] if index+1<len(items) else 0
    return 0
cases=[('null starts first',records,0,records[0]),('first advances second',records,records[0],records[1]),('last returns null',records,records[1],0),('empty returns null',[],0,0),('missing identity returns null',records,1,0)]
results=[]
for label,items,current,expected in cases:
    actual=successor(items,current)
    if actual!=expected:raise AssertionError(label)
    results.append(dict(case=label,records=items,current=current,result=actual,expected=expected))
result=dict(source='pass155/00690280.asm; pass154/005a5254.asm',capture='captures/maryland-records-paused-01/records.json',cases=results,limitations='Offline model and boundary examples, not runtime execution or observed selection transitions. Assumes a valid circular list and unique record identities. Native search chooses the first matching identity; corrupted/cyclic lists are not protected by the native helper. Null does not distinguish exhausted list, empty list or missing identity.')
(root/'station-successor-model.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result))
