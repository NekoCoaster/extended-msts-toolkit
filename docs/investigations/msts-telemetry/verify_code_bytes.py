"""Compare exported Ghidra instruction bytes with installed disk image and live memory.

Checks only instructions emitted in the requested pass, not whole-function coverage.
"""
import argparse,json,hashlib
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
p=argparse.ArgumentParser();p.add_argument('--pass-name',required=True);p.add_argument('--pid',type=int,required=True);a=p.parse_args()
root=Path(__file__).resolve().parent;pe=PE();r=Reader(a.pid);results=[]
try:
    for file in sorted((root/a.pass_name).glob('*.bytes.tsv')):
        count=total=0;disk_diff=[];live_diff=[];errors=[]
        for line in file.read_text().splitlines():
            addr,h=line.split('\t');va=int(addr,16);expected=bytes.fromhex(h);count+=1;total+=len(expected)
            if pe.read(va,len(expected))!=expected:disk_diff.append(addr)
            try:
                actual=r.read(va,len(expected))
                if actual!=expected:live_diff.append(dict(address=addr,expected=h,actual=actual.hex()))
            except OSError as e:errors.append(dict(address=addr,error=str(e)))
        results.append(dict(function=file.stem.split('.')[0],instructions=count,bytes=total,disk_mismatches=disk_diff,live_mismatches=live_diff,errors=errors))
finally:K.CloseHandle(r.h)
if not results:raise SystemExit('No exported instruction bytes found')
report=dict(disk_sha256=hashlib.sha256(pe.data).hexdigest(),pid=a.pid,pass_name=a.pass_name,limitation='Only exported instruction ranges checked; missing function chunks, data tables, relocations and future process writes need separate consideration.',functions=results)
(root/(a.pass_name+'-byte-verification.json')).write_text(json.dumps(report,indent=2))
print(json.dumps(dict(functions=len(results),instructions=sum(x['instructions'] for x in results),bytes=sum(x['bytes'] for x in results),disk_mismatches=sum(len(x['disk_mismatches']) for x in results),live_mismatches=sum(len(x['live_mismatches']) for x in results),errors=sum(len(x['errors']) for x in results))))
