# tests/test_reserve_store.py

import unittest
import simpy


class Item:
    """A class representing an item with a 'ready' flag."""
    def __init__(self, name):
        self.name = name

class TestReserveStore(unittest.TestCase):
    def setUp(self):
        self.env = simpy.Environment()
        self.store = ReserveStore(self.env, capacity=5)

    def test_initialization(self):
        self.assertEqual(self.store.capacity, 5)
        self.assertEqual(self.store.reserved_count, 0)
        self.assertEqual(len(self.store.reserve_queue), 0)

    def test_reserve(self):
        for _ in range(5):
            self.store.reserve()
        self.assertEqual(self.store.reserved_count, 5)
        self.assertEqual(len(self.store.reserve_queue), 0)

        # Test reserve when capacity is full
        event = self.store.reserve()
        self.assertEqual(self.store.reserved_count, 5)
        self.assertEqual(len(self.store.reserve_queue), 1)
        self.assertFalse(event.triggered)

    def test_put_and_get(self):
        item = Item(name="TestItem")
        self.store.put(item)
        self.assertEqual(len(self.store.items), 1)
        self.assertEqual(self.store.itemcount[1], 1)

        event = self.store.get()
        self.env.run(until=event)
        self.assertEqual(len(self.store.items), 0)
        self.assertEqual(self.store.itemcount[1], 0)

if __name__ == '__main__':
    unittest.main()