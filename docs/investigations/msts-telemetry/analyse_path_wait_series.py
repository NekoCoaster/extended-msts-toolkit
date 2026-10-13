"""Summarize terminal path-wait captures; retain adjacency and raw provenance."""
import argparse
import hashlib
import json
from pathlib import Path

def analyse(rows):
    result=dict(samples=0,errors=0,unstable_roots=0,unstable_cursor=0,wait_braking=0,wait_dwell=0,transitions=[])
    previous=None
    keys=('cursor_index','event_index','iterator_type')
    def state(row):
        return tuple(row[k] for k in keys)+tuple(row['flags'][k] for k in ('0x1dc','0x1e4','0x1e8'))
    def compact(row):
        return {k:row[k] for k in ('utc','time','wall_elapsed','cursor_index','event_index','iterator_type','flags','timers','speed','target','roots_stable','cursor_stable')}
    for row in rows:
        result['samples']+=1
        if 'error' in row:
            result['errors']+=1;previous=None;continue
        result.setdefault('first',compact(row));result['last']=compact(row)
        result['unstable_roots']+=not row['roots_stable'];result['unstable_cursor']+=not row['cursor_stable']
        result['wait_braking']+=bool(row['flags']['0x1e4']);result['wait_dwell']+=bool(row['flags']['0x1e8'])
        if previous is not None and state(row)!=state(previous):
            result['transitions'].append(dict(before=compact(previous),after=compact(row)))
        previous=row
    result['limits']='Sequential external observations; missed brief transitions remain possible. Progress deliberately excluded; first capture read a pointer as float. State adjacency breaks on errors.'
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('capture',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    completion=json.loads((args.capture/'completion.json').read_text())
    raw=(args.capture/'samples.jsonl').read_bytes()
    result=analyse(json.loads(line) for line in raw.splitlines())
    assert result['samples']==completion['samples'] and result['errors']==completion['errors']
    result.update(completion=completion,samples_sha256=hashlib.sha256(raw).hexdigest())
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in result.items() if k not in ('first','last','limits')}))
