import math
import struct
import unittest
from read_track_interaction_records import sample


class Memory:
    def __init__(self, old_a=20, a=15, old_b=30, b=25, threshold=10, change=None):
        self.data = {}
        self.calls = {}
        self.change = change
        for address, fmt, values in [
            (0x80acd4,'f',(100,)),(0x7be0f4,'I',(1,)),(0x80a01c,'I',(1000,)),
            (1000,'I',(1100,)),(1100,'III',(1000,1000,1200)),
            (1200,'II',(1300,1400)),(1300,'I',(8,)),(1400,'I',(1500,)),
            (1500,'III',(1400,1400,1600)),(1600,'I4f',(2000,old_a,a,old_b,b)),
            (2000+0x128,'f',(threshold,))]:
            self.put(address,fmt,*values)

    def put(self,address,fmt,*values):
        for i,v in enumerate(struct.pack('<'+fmt,*values)):self.data[address+i]=v

    def read(self,address,size):
        self.calls[address]=self.calls.get(address,0)+1
        if self.change=='clock' and address==0x80acd4 and self.calls[address]>1:
            self.put(address,'f',101)
        if self.change=='record' and address==1600 and self.calls[address]>1:
            self.put(1608,'f',14)
        return bytes(self.data[address+i] for i in range(size))

    def unpack(self,address,fmt):return struct.unpack('<'+fmt,self.read(address,struct.calcsize('<'+fmt)))
    def u(self,address):return self.unpack(address,'I')[0]
    def f(self,address):return self.unpack(address,'f')[0]


class InteractionTests(unittest.TestCase):
    def state(self,**kwargs):
        result=sample(Memory(**kwargs));self.assertTrue(result['guards_pass'])
        return result['records'][0]['conditional_state']

    def test_strict_threshold_and_both_endpoints(self):
        self.assertEqual(self.state(a=9,b=9),1)
        self.assertEqual(self.state(a=10,b=9),2)
        self.assertEqual(self.state(a=9,b=10),2)

    def test_sentinel_and_proximity_precedence(self):
        self.assertEqual(self.state(old_a=-1),0)
        self.assertEqual(self.state(old_b=-1),0)
        self.assertEqual(self.state(old_a=-1,old_b=-1,a=9,b=9),1)

    def test_trend_and_unchanged(self):
        self.assertEqual(self.state(a=19),2)
        self.assertEqual(self.state(a=21),3)
        self.assertEqual(self.state(a=20),0)

    def test_nonfinite_rejected(self):
        with self.assertRaisesRegex(ValueError,'Nonfinite'):sample(Memory(a=math.nan))

    def test_clock_crossing_suppresses(self):
        result=sample(Memory(change='clock'))
        self.assertFalse(result['guards_pass']);self.assertIsNone(result['records'][0]['conditional_state'])

    def test_record_change_suppresses(self):
        result=sample(Memory(change='record'))
        self.assertFalse(result['guards_pass']);self.assertIsNone(result['records'][0]['conditional_state'])

    def test_cycle_rejected(self):
        memory=Memory();memory.put(1500,'I',1500)
        with self.assertRaisesRegex(ValueError,'cycle'):sample(memory)

if __name__=='__main__':unittest.main()
