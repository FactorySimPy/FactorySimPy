import unittest
import simpy

class ReserveStore(simpy.Store):
    def __init__(self, env, capacity=float('inf')):
        super().__init__(env, capacity)
        self.env = env
        self.reserved_count = 0
        self.itemcount = (0, 0)
        self.reserve_queue = []  # Use a list as a simple queue

    def reserve(self):
        """
        Reserve space in the store.
        If the reserved count is less than the capacity, increment the reserved count.
        Otherwise, put an event in the reserve queue.
        """
        if self.reserved_count < self.capacity:
            self.reserved_count += 1
            return self.env.event().succeed()  # Return an already succeeded event
        else:
            event = self.env.event()
            self.reserve_queue.append(event)  # else add an event to the reserve_queue
            return event

    def get(self):
        """
        Get an item from the store.
        Decrement the reserved count and run the reserve queue.
        """
        event = super().get()  # Call the parent class's get method
        event.callbacks.append(self._decrement_reserved_count)
        event.callbacks.append(self._trigger_reserve)
        return event

    def _trigger_reserve(self, event):
        """
        Trigger the reserve queue to fulfill pending reserve requests.
        """
        if self.reserve_queue:
            reserve_event = self.reserve_queue.pop(0)
            reserve_event.succeed()
            self.reserved_count += 1

    def _decrement_reserved_count(self, event):
        """
        Decrement the reserved count after a successful get operation.
        """
        self.reserved_count -= 1

    def _do_get(self, event):
        super()._do_get(event)
        self.itemcount = self.env.now, len(self.items)

    def _do_put(self, event):
        super()._do_put(event)
        self.itemcount = self.env.now, len(self.items)

class Item:
    """A class representing an item with a 'ready' flag."""
    def __init__(self, name):
        self.name = name

class Processor:
    def __init__(self, env, name, k=1, c=1, delay=1):
        self.env = env
        self.name = name
        self.c = c
        self.k = k
        self.store = ReserveStore(env, capacity=min(k, c))  # Custom store with reserve capacity
        self.resource = simpy.Resource(env, capacity=k)  # Work capacity
        self.delay = delay  # Processing delay

        if k > c:
            print("Warning: Effective capacity is limited by the minimum of k and c.")

        # Start the behaviour process
        self.env.process(self.behaviour())

    def worker(self, i):
        """Worker process that processes items with resource and reserve handling."""
        while True:
            with self.resource.request() as req:
                yield req  # Wait for work capacity
                yield self.store.reserve()  # Wait for a reserved slot if needed
                assert self.store.itemcount[1] <= min(self.k, self.c), (f'Resource util exceeded')
                print(f"At time {self.env.now:.2f}: worker{i} reserving space for item and reserve count is {self.store.reserved_count}")

                # Simulate item retrieval and processing
                item = yield input_store.get()  # Use global input_store
                assert self.store.itemcount[1] <= min(self.k, self.c), (f'Resource util exceeded')
                print(f"At time {self.env.now:.2f}: worker{i} Worker got an item and is processing - {item.name}")

                # Simulate processing delay
                yield self.env.timeout(self.delay)

                # Put the item back (if needed for recycling the item)
                yield self.store.put(item)
                assert self.store.itemcount[1] <= min(self.k, self.c), (f'Resource util exceeded')
                print(f"At time {self.env.now:.2f}: worker{i} putting item into store - reserve count is {self.store.reserved_count} and num_items {len(self.store.items)}, {[i.name for i in self.store.items]}")

    def behaviour(self):
        """Processor behavior that creates workers based on the effective capacity."""
        cap = min(self.c, self.k)
        for i in range(cap):
            self.env.process(self.worker(i + 1))
        yield self.env.timeout(0)  # Initialize the behavior without delay

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
        self.assertTrue(all(len(self.processor.resource.users) <= min(self.processor.k, self.processor.c) for worker in self.processor.resource.users))

    def test_resource_utilization(self):
        self.env.run(until=5)
        self.assertTrue(all(self.processor.store.itemcount[1] <= min(self.processor.k, self.processor.c) for _ in range(5)))

if __name__ == '__main__':
    unittest.main()