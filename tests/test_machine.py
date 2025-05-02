# tests/test_processor.py

import unittest
import simpy


class Item:
    """A class representing an item with a 'ready' flag."""
    def __init__(self, name):
        self.name = name

class TestProcessor(unittest.TestCase):
    def setUp(self):
        global input_store
        self.env = simpy.Environment()
        input_store = simpy.Store(self.env)  # Define input_store as a global variable
        self.processor = Processor(self.env, "Processor1", k=2, c=3, delay=1)
        self.env.process(item_producer(self.env, input_store))
        self.env.process(item_consumer(self.env, self.processor))

    def test_worker_behavior(self):
        self.env.run(until=5)
        self.assertTrue(all(len(worker.users) <= min(self.processor.k, self.processor.c) for worker in self.processor.resource.users))

    def test_resource_utilization(self):
        self.env.run(until=5)
        self.assertTrue(all(self.processor.store.itemcount[1] <= min(self.processor.k, self.processor.c) for _ in range(5)))

def item_producer(env, store):
    """A process to produce items and put them in the store with ready=False."""
    for i in range(10):
        yield env.timeout(1)  # Produce items every 1 time unit
        item = Item(name=f"Item{i}")  # Create an item with 'notready=True'
        yield store.put(item)

def item_consumer(env, processor):
    """A process to consume items from the processor's store."""
    while True:
        yield env.timeout(2)  # Consume items every 2 time units
        item = yield processor.store.get()
        yield processor.store.put(item)

if __name__ == '__main__':
    unittest.main()