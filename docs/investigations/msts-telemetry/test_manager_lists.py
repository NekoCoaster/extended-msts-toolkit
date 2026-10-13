"""Synthetic graph checks; not evidence of native class semantics or live coverage."""
import struct
import unittest
from read_manager_lists import survey


class Fixture:
    def __init__(self):
        self.memory = {}
        self.words(0x7bdecc, 0x10000)
        self.words(0x828108, 0x20000)
        for i in range(5):
            head = 0x30000 + i*0x100
            self.words(0x10000+i*8, head, 0)
            self.words(head, head, head)

    def words(self, address, *values):
        for i, byte in enumerate(struct.pack('<'+'I'*len(values), *values)):
            self.memory[address+i] = byte

    def read(self, address, size):
        return bytes(self.memory[address+i] for i in range(size))

    def unpack(self, address, fmt):
        return struct.unpack('<'+fmt, self.read(address, struct.calcsize('<'+fmt)))

    def u(self, address):
        return self.unpack(address, 'I')[0]

    def add_object(self):
        head, node, obj = 0x30300, 0x40000, 0x50000
        self.words(head, node, node)
        self.words(node, head, head, 12)
        self.words(0x20000+12*8, obj)
        self.words(obj, 15)
        self.words(0x1001c, 1)


class ManagerListTests(unittest.TestCase):
    def test_null_manager_is_unavailable_not_empty(self):
        r = Fixture()
        r.words(0x7bdecc, 0)
        result = survey(r)
        self.assertFalse(result['available'])
        self.assertIsNone(result['lists'])

    def test_valid_empty_lists_are_available(self):
        result = survey(Fixture())
        self.assertTrue(result['available'])
        self.assertEqual(len(result['lists']), 5)
        self.assertTrue(all(not x['objects'] for x in result['lists']))

    def test_index_resolution_without_vehicle_layout(self):
        r = Fixture()
        r.add_object()
        result = survey(r)['lists'][3]
        self.assertEqual(result['stored_count'], 1)
        self.assertEqual(result['objects'][0]['address'], 0x50000)
        self.assertEqual(result['objects'][0]['class_index'], 15)
        self.assertTrue(result['objects'][0]['reciprocal_links'])

    def test_non_sentinel_cycle_is_rejected(self):
        r = Fixture()
        r.add_object()
        r.words(0x40000, 0x40000, 0x30300, 12)
        with self.assertRaisesRegex(ValueError, 'cycle'):
            survey(r)

    def test_stored_count_mismatch_is_retained(self):
        r = Fixture()
        r.add_object()
        r.words(0x1001c, 2)
        result = survey(r)['lists'][3]
        self.assertEqual(result['stored_count'], 2)
        self.assertEqual(len(result['objects']), 1)


if __name__ == '__main__':
    unittest.main()
