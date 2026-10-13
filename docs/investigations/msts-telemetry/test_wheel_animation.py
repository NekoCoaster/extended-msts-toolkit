"""Synthetic rejection/coherence checks; not native layout validation."""
import struct
import unittest
from read_wheel_animation import sample, shape_state, vehicle_state


class Memory:
    def __init__(self):
        self.data={}
    def put(self,address,fmt,*values):
        self.data.update({address+i:b for i,b in enumerate(struct.pack('<'+fmt,*values))})
    def read(self,address,size):
        return bytes(self.data[address+i] for i in range(size))
    def unpack(self,address,fmt):
        return struct.unpack('<'+fmt,self.read(address,struct.calcsize('<'+fmt)))
    def u(self,address):return self.unpack(address,'I')[0]
    def f(self,address):return self.unpack(address,'f')[0]


class WheelTests(unittest.TestCase):
    def shape(self):
        r=Memory()
        r.put(0x10000,'I',0x828be0)
        r.put(0x10008,'H',5)
        r.put(0x828c0c,'I',0x6a5fd0)
        r.put(0x1008c,'I',0x20000)
        r.put(0x10090,'ff',1.0,2.0)
        return r
    def test_unavailable_manager_does_not_enumerate(self):
        r=Memory();r.put(0x7bdecc,'I',0)
        result=sample(r)
        self.assertFalse(result['available'])
        self.assertIsNone(result['vehicles'])
    def test_unsupported_shape_does_not_follow_layout(self):
        r=Memory();r.put(0x10000,'I',0x20000);r.put(0x10008,'H',4)
        self.assertEqual(shape_state(r,0x10000)['reason'],'unsupported_shape')
    def test_separate_times_and_raw_provenance(self):
        result=shape_state(self.shape(),0x10000)
        self.assertEqual(result['current_animation_seconds'],2.0)
        self.assertEqual(result['processed_animation_seconds'],1.0)
        self.assertFalse(result['equal_at_read'])
        self.assertTrue(result['identity_stable'])
        self.assertEqual(struct.unpack('<ff',bytes.fromhex(result['raw_times'])),(1.,2.))
    def test_nonfinite_time_rejected(self):
        r=self.shape();r.put(0x10090,'ff',1.,float('nan'))
        with self.assertRaisesRegex(ValueError,'Nonfinite'):shape_state(r,0x10000)
    def test_changed_descriptor_reported(self):
        r=self.shape();original=r.u;count=0
        def changed(address):
            nonlocal count
            if address==0x1008c:
                count+=1
                if count>1:return 0x30000
            return original(address)
        r.u=changed
        self.assertFalse(shape_state(r,0x10000)['identity_stable'])
    def test_recycled_vehicle_rejected_before_fields(self):
        r=Memory()
        for offset,value in ((0x50,99),(0x98,0x20000),(0x94,0x30000),(4,7)):r.put(0x10000+offset,'I',value)
        obj=dict(address=0x10000,physics=dict(definition=0x30000,powered=False),native_kind=0x4000d,
                 object_id=98,owner=0x20000,table_index=7,stable=True,reciprocal_list_links=True)
        with self.assertRaisesRegex(ValueError,'identity changed'):vehicle_state(r,obj)


if __name__=='__main__':unittest.main()
