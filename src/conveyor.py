# @title trial continuous


import simpy
import random
from simpy import FilterStore

class BeltStore(simpy.FilterStore):
    def __init__(self, env, capacity, delay, acc=0):
        super().__init__(env, capacity)
        self.env = env
        self.ret_item = None
        self.accumulating = acc
        self.delay = delay
        self.release_queue = []
        self.request_queue = []
        self.active_events = []

    def is_empty(self):
        """Check if the belt is completely empty."""
        return (
            len(self.items) == 0 and
            len(self.put_queue) == 0 and
            len(self.request_queue) == 0 and
            len(self.release_queue) == 0
        )

    def is_full(self):
        """Check if the belt is full."""
        return len(self.items) == self.capacity

    def is_stalled(self):
        """Check if the belt is stalled due to time constraints."""
        return self.env.now > self.items[0][1] + (self.delay)

    def can_get(self):
        """Check if an item is available for retrieval."""
        return len(self.items) > 0 and self.env.now >= self.items[0][1] + (self.delay)

    def can_put(self):
        """Check if a new item can be added to the belt."""
        return len(self.items) < self.capacity

    def _do_put(self, event):
        """Override to handle the put operation."""
        print(f"At {self.env.now} do_putting an item. Put queue length: {len(self.put_queue)}")
        super()._do_put(event)

    def move(self):
        """Move items along the belt for accumulation or retrieval."""
        if len(self.request_queue) > 0 and self.can_put():
            put_event = self.put(self.request_queue[0][1])  # Add timestamp to item here.
            print(f"At {self.env.now} putting item {self.request_queue[0][1]}. Put queue length: {len(self.put_queue)}")
            put_out_event = self.request_queue.pop(0)[0]
            put_out_event.succeed()

        if len(self.release_queue) > 0 and self.can_get():
            print(f"At {self.env.now} getting item {self.items}. Put queue length: {len(self.put_queue)}")
            self.ret_item = yield self.get()
            if self.ret_item is not None:
                get_out_event = self.release_queue.pop(0)
                get_out_event.succeed(value=self.ret_item)
            else:
                print(f"At {self.env.now} returned None")

    def accumulate(self):
        """Handle accumulating behavior of the belt."""
        while self.is_stalled():
            if self.can_put():
                if len(self.put_queue) > 0:
                    self.trigger_put()
                elif len(self.request_queue) > 0:
                    put_event = self.put(self.request_queue[0][1])
                    put_out_event = self.request_queue.pop(0)[0]
                    put_out_event.succeed()

            if self.can_get():
                if len(self.get_queue) > 0:
                    self.trigger_get()
                elif len(self.release_queue) > 0:
                    print(f"At {self.env.now} getting item {self.items} and put queue={len(self.put_queue)}")
                    self.ret_item = yield self.get()

                    if self.ret_item is not None:
                        get_out_event = self.release_queue.pop(0)
                        get_out_event.succeed(value=self.ret_item)
                    else:
                        print(f"At {self.env.now} returned None")

            yield self.env.timeout(self.time_per_slot)

    def no_accumulate(self):
        """Handle non-accumulating behavior of the belt."""
        if self.is_stalled() and len(self.release_queue) > 0 and self.can_get():
            print(f"At {self.env.now} is stalled. Checking items {self.items}. Put queue length: {len(self.put_queue)}")
            self.ret_item = yield self.get()
            if self.ret_item is not None:
                get_out_event = self.release_queue.pop(0)
                get_out_event.succeed(value=self.ret_item)
            else:
                print(f"At {self.env.now} returned None")

    def show_occupancy(self):
        """Return the current occupancy of the belt."""
        return len(self.items)

    def get(self, filter=None):
        """Retrieve an item from the belt with a time filter."""
        filter = lambda x: self.env.now >= x[1] + (self.delay)
        print(f"At {self.env.now} attempting to get item. Time threshold: {self.delay}")
        self.ret_event = super().get(filter)
        return self.ret_event

    def item_get(self):
        """Request an item retrieval from the belt."""
        get_in_event = self.env.event()
        self.release_queue.append(get_in_event)
        return get_in_event

    def item_put(self, item):
        """Request to place an item on the belt."""
        put_in_event = self.env.event()
        self.request_queue.append((put_in_event, (item, self.env.now)))  # Add timestamp to item
        return put_in_event

class ConveyorBelt:
    def __init__(self, env, capacity,delay,accumulation):
        self.env = env
        self.state = "stopped"
        self.delay = delay
        self.accumulation = accumulation
        self.belt = BeltStore(env, capacity, delay, self.accumulation)
        self.env.process(self.behaviour())

    def behaviour(self):
        """Monitor and adjust the belt's state dynamically based on events."""
        while True:
            if self.belt.is_empty():
                self.state = "empty"
                print(f"At {self.env.now}, the belt is empty")
                yield self.env.event().succeed()  # Wait for an event to trigger the next action
            elif self.belt.is_full():
                if self.belt.is_stalled():
                    self.state = "stalled"
                    print(f"At {self.env.now}, the belt is stalled")
                    if self.accumulation:
                        print("accumulation")
                        yield self.env.process(self.belt.accumulate())
                    else:
                        print("noaccumulation")
                        yield self.env.process(self.belt.no_accumulate())
            else:
                self.state = "moving"
                print(f"At {self.env.now}, the belt is moving")
                yield self.env.process(self.belt.move())

            if not self.belt.active_events:
                yield self.env.timeout(0)  # Wait for any activity to occur
            else:
                result = yield self.env.any_of(self.belt.active_events)
                self.belt.active_events = [e for e in self.belt.active_events if not e.triggered]

# Simulation setup
def item_generator(env, belt):
    """Generate items and place them on the conveyor belt."""
    yield env.timeout(0.6)
    for i in range(10):  # Generate 10 items
        print(f"{env.now}: Waiting to add item {i + 1} to the conveyor belt.")
        yield belt.item_put(f"item{i + 1}")  # Add item to the belt
        print(f"At {env.now} Belt items: {belt.items}")
        yield env.timeout(random.choice([0.1, 0.3, 0.4, 1.2]))  # Random delay

def reader(env, belt):
    """Process to read items from the conveyor belt."""
    while True:
        yield env.timeout(2)  # Time interval to check for items
        print(f"{env.now}: Waiting to retrieve an item...")
        item = yield belt.item_get()
        print(f"{env.now}: Retrieved item: {item}")

# Environment setup
env = simpy.Environment()
capacity = 5
delay=5
accumulation=0
belt = ConveyorBelt(env, capacity,delay,accumulation)

# Start processes
env.process(item_generator(env, belt.belt))
env.process(reader(env, belt.belt))

# Run simulation
env.run(until=20)
