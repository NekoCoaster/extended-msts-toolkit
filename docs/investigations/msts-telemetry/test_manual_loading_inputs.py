"""Synthetic edge cases for read-only manual-loading extraction, not game proof."""
import struct,unittest
from read_manual_loading_inputs import sample

class Fake:
    def __init__(self):self.mem={};self.calls={};self.drift=None
    def put(self,address,fmt,*values):
        for i,b in enumerate(struct.pack('<'+fmt,*values)):self.mem[address+i]=b
    def unpack(self,address,fmt):
        key=(address,fmt);self.calls[key]=self.calls.get(key,0)+1
        if self.drift==address and self.calls[key]>1:
            return (101.0,) if fmt=='f' else (0xdead000,)
        return struct.unpack('<'+fmt,bytes(self.mem[address+i] for i in range(struct.calcsize('<'+fmt))))
    def u(self,a):return self.unpack(a,'I')[0]
    def f(self,a):return self.unpack(a,'f')[0]

def fixture():
    r=Fake();a=0x809810;s=a+0x80
    for addr,value in [(0x7be0f4,1),(0x809e1c,0),(a+0x36c,1),(a+0x370,0),(s+0x34,0x10000),(s+0x158,0x11000),(0x80a10c,0x12000),(0x12000,0x12100),(0x12108,0x13000),(0x13020,0x14000),(0x14000,0x15000),(0x14008,2),(0x10000,0),(0x15000,0x16000),(0x15004,0x17000),(0x11062,0x20000)]:r.put(addr,'I',value)
    r.put(0x1001e,'H',0);r.put(0x10008,'f',0);r.put(0x828fb4,'f',.125)
    for addr,value in [(0x80acd4,100),(a+0x374,0),(a+0x364,0),(s+0x138,0)]:r.put(addr,'f',value)
    for addr,index,distance in [(0x16000,0,0),(0x17000,1,100)]:
        r.put(addr,'I',3);r.put(addr+12,'f',distance);r.put(addr+0x34,'I',1-index);r.put(addr+0x38,'f',180);r.put(addr+0x3c,'I',30)
    for i,(kind,cap,pos,membership) in enumerate([(3,0,50,True),(3,0,0,True),(1,40,50,False),(1,0,50,True)]):
        car=0x20000+i*0x1000;definition=0x30000+i*0x1000;track=0x40000+i*0x1000;items=0x50000+i*0x1000
        for addr,value in [(car+0x94,definition),(car+0x128,track),(car+0xa8,car+0x1000 if i<3 else 0),(track+0x20,items),(track+0x24,1),(items,0x16000 if membership else 0x18000)]:r.put(addr,'I',value)
        r.put(definition+0x88,'B',kind);r.put(definition+0xc08,'f',cap);r.put(car+0x138,'f',pos)
    return r

class Cases(unittest.TestCase):
    def test_eligibility_membership_and_strict_endpoint(self):
        x=sample(fixture());self.assertEqual(x['eligible_count'],3);self.assertEqual(x['contributing_count'],1);self.assertEqual(x['conditional_duration'],300);self.assertTrue(all(x['guards'].values()))
    def test_paired_endpoint_supplies_count(self):
        r=fixture();r.put(0x1703c,'I',7);self.assertEqual(sample(r)['conditional_duration'],70)
    def test_reversed_endpoints(self):
        r=fixture();r.put(0x1600c,'f',100);r.put(0x1700c,'f',0);self.assertEqual(sample(r)['contributing_count'],1)
    def test_definition_pointer_changes(self):
        r=fixture();r.drift=0x20094;x=sample(r);self.assertFalse(x['vehicles'][0]['pointers_stable']);self.assertFalse(x['comparison_guards_pass']);self.assertIsNone(x['contributing_count']);self.assertIsNone(x['conditional_duration'])
    def test_clock_crossing_suppresses_model(self):
        r=fixture();r.drift=0x80acd4;x=sample(r);self.assertFalse(x['comparison_guards_pass']);self.assertIsNone(x['eligible_count']);self.assertIsNone(x['conditional_duration'])
    def test_vehicle_cycle_rejected(self):
        r=fixture();r.put(0x230a8,'I',0x20000)
        with self.assertRaisesRegex(ValueError,'cycle'):sample(r)
    def test_item_bound_rejected(self):
        r=fixture();r.put(0x40024,'I',10001)
        with self.assertRaisesRegex(ValueError,'array bound'):sample(r)
    def test_no_contributing_vehicle_has_no_duration(self):
        r=fixture();r.put(0x20138,'f',100);x=sample(r);self.assertEqual(x['contributing_count'],0);self.assertIsNone(x['conditional_duration'])
if __name__=='__main__':unittest.main()
