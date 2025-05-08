# @title Split
import random
import simpy

from factorysimpy.base.reservable_priority_req_filter_store import ReservablePriorityReqFilterStore  # Import your class
from factorysimpy.nodes.node import Node


from factorysimpy.helper.item import Item


class Split(Node):
    """
    Split class representing a processing node in a factory simulation.
    Inherits from the Node class.
    This splitter can have a single input edge and two output edges.
    It processes items from the input edge and splits them into two output edges based on a split ratio.
    Attributes
    ----------
   
    split_ratio : float
        The ratio at which items are split into two output groups.
   
    Methods
    -------
   
    add_in_edges(self, edge):
        Adds an input edge to the splitter.
    add_out_edges(self, edge):
        Adds an output edge to the splitter.
    worker(self, i):
        Worker process that sorts and splits items based on a split ratio.
    behaviour(self):
        Splitter behavior that creates workers based on the effective capacity.
    
    Raises
    -------
    ValueError
        If the splitter already has the maximum number of input or output edges.
    AssertionError
        If the splitter does not have exactly 1 input edge or 2 output edges in the behaviour function.

    """
    def __init__(self, env, name,in_edges=None , out_edges=None,work_capacity=1, store_capacity=1, delay=1,rule=0.5):
        super().__init__(env, name, in_edges , out_edges, work_capacity=1, store_capacity=1, delay=0)
        self.env = env
        self.name = name
        self.work_capacity = work_capacity
        self.store_capacity = store_capacity
        self.in_edges = in_edges
        self.out_edges = out_edges
        self.rule=rule
        self.inbuiltstore = ReservablePriorityReqFilterStore(env, capacity=store_capacity)  # Custom store with reserve capacity
        self.resource = simpy.Resource(env, capacity=min(work_capacity,store_capacity))  # Work capacity
        self.delay = delay  # Processing delay

        if work_capacity>store_capacity :
            print("Warning: Effective capacity is limited by the minimum of work_capacity and store_capacity.")

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
            raise ValueError(f"Edge already exists in Split '{self.name}' in_edges.")

    def add_out_edges(self, edge):
        if self.out_edges is None:
            self.out_edges = []

        if len(self.out_edges) >= 2:
            raise ValueError(f"Split '{self.name}' already has 2 out_edges. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Split '{self.name}' out_edges.")

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
                if random.random()<self.rule:
                   split_item = Item(name=f"{item.name}_a")
                else:
                   split_item = Item(name=f"{item.name}_b")
                self.inbuiltstore.put(put_event, split_item)


                print(f"At time {self.env.now:.2f}: worker {i} placed split item {split_item.name} into store")

    def behaviour(self):
        """Splitter behavior that creates workers based on the effective capacity."""

        assert self.in_edges is not None and len(self.in_edges) == 1, f"Split '{self.name}' must have exactly 1 in_edge."
        assert self.out_edges is not None and len(self.out_edges) == 2, f"Split '{self.name}' must have exactly 2 out_edges."


        cap = min(self.work_capacity, self.store_capacity)
        for i in range(cap):
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay

