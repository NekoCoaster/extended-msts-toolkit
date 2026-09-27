"""Reconstruct traced bit/table norm step; no native function invocation."""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path
from binary_fields import PE
from read_live import Reader,K
p=argparse.ArgumentParser()
p.add_argument('--pid',type=int,required=True)
a=p.parse_args()
r=Reader(a.pid)
try:
    pe=PE()
    assert pe.read(0x7af118,4)==b'pow\0' and r.read(0x7af118,4)==b'pow\0'
    assert pe.u(0x795668+4)==0x4017c and pe.string(pe.u(0x795668))=='Friction'
    assert r.read(0x795668,8)==pe.read(0x795668,8)
    assert r.read(pe.u(0x795668),18)=='Friction'.encode('utf-16le')+b'\0\0'
    raw=r.read(0x82b630,4096)
    table=struct.unpack('<1024I',raw)
    rows=[]
    for value in (0.,1e-12,0.25,1.,2.,4.,9.,100.,10000.):
        bits=struct.unpack('<I',struct.pack('<f',value))[0]
        index=(bits>>14)&0x3ff
        result_bits=(((bits&0x7f800000)+0x3f800000)>>1)&0x7f800000|table[index]
        result=struct.unpack('<f',struct.pack('<I',result_bits))[0]
        rows.append(dict(squared_input=value,index=index,result=result,reference_sqrt=math.sqrt(value),result_bits=hex(result_bits)))
    report=dict(pid=a.pid,image_sha256=r.sha,table_address='0x82b630',table_words=list(table),
                labels=dict(math_name_address='0x7af118',math_name='pow',friction_table='0x795668',friction_token='0x4017c'),
                sha256=hashlib.sha256(raw).hexdigest(),stable=raw==r.read(0x82b630,4096),examples=rows,
                limitation='Offline bit-formula reconstruction from live table;not native calls,not observed vehicle speed,andnot full floating-point emulation of preceding vector sum.')
    Path(__file__).with_name('velocity-norm-table-map.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(dict(stable=report['stable'],examples=rows)))
finally:
    K.CloseHandle(r.h)
