# @title Split
import random
import simpy ,os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../extended_resources')))

from reservable_priority_req_filter_store import ReservablePriorityReqFilterStore  # Import your class

from node import Node
from item import Item

class Split(Node):
    def __init__(self, env, name,in_edges , out_edges, k=1, c=1, delay=1,split_ratio=0.5):
        super().__init__(env, name,  work_capacity=1, store_capacity=1, delay=0)
        self.env = env
        self.name = name
        self.c = c
        self.k = k
        self.in_edges = in_edges
        self.out_edges = out_edges
        self.split_ratio=split_ratio
        self.inbuiltstore = ReservablePriorityReqFilterStore(env, capacity=c)  # Custom store with reserve capacity
        self.resource = simpy.Resource(env, capacity=min(k, c))  # Work capacity
        self.delay = delay  # Processing delay

        if k > c:
            print("Warning: Effective capacity is limited by the minimum of k and c.")

        # Start the behaviour process
        self.env.process(self.behaviour())


    def add_in_edges(self, edge):
        if self.in_edges is None:
            self.in_edges = []

        if len(self.in_edges) >= 1:
            raise ValueError(f"Split '{self.name}' already has 1 in_edge. Cannot add more.")

        if edge not in self.in_edges:
            self.in_edges.append(edge)
        else:
            print(f"Edge already exists in Split '{self.name}' in_edges.")

    def add_out_edges(self, edge):
        if self.out_edges is None:
            self.out_edges = []

        if len(self.out_edges) >= 2:
            raise ValueError(f"Split '{self.name}' already has 2 out_edges. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            print(f"Edge already exists in Split '{self.name}' out_edges.")

    def worker(self, i):
        """Worker process that sorts and splits items based on a split ratio."""
        while True:
            with self.resource.request() as req:
                yield req  # Wait for work capacity
                put_event = self.inbuiltstore.reserve_put()  # Wait for a reserved slot if needed
                yield put_event


                print(f"At time {self.env.now:.2f}: worker {i} reserving space for split item")


                get_event = self.in_edges[0].reserve_get()
                yield get_event

                item = self.in_edges[0].get(get_event)



                print(f"At time {self.env.now:.2f}: worker {i} received item {item.name}  for splitting")

                # Simulate processing delay for combining items
                yield self.env.timeout(self.delay)

                # Create a combined output item and put it in the combiner's store
                if random.random()<self.split_ratio:
                   split_item = Item(name=f"{item.name}_a")
                else:
                   split_item = Item(name=f"{item.name}_b")
                self.inbuiltstore.put(put_event, split_item)


                print(f"At time {self.env.now:.2f}: worker {i} placed split item {split_item.name} into store")

    def behaviour(self):
        """Splitter behavior that creates workers based on the effective capacity."""

        assert self.in_edges is not None and len(self.in_edges) == 1, f"Split '{self.name}' must have exactly 1 in_edge."
        assert self.out_edges is not None and len(self.out_edges) == 2, f"Split '{self.name}' must have exactly 2 out_edges."


        cap = min(self.c, self.k)
        for i in range(cap):
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay

