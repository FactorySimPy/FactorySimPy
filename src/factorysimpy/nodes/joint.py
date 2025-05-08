# @title Joint
import simpy ,os, sys


from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore  # Import your class
from factorysimpy.nodes.node import Node

from factorysimpy.helper.item import Item

class Joint(Node):
    """
    Joint class representing a processing node in a factory simulation.
    Inherits from the Node class.
    This joint can have multiple input edges and a single output edge.
    It processes items from the input edges and puts them into the output edge.
    
    Methods
    -------
    
    add_in_edges(self, edge):
        Adds an input edge to the joint.
    add_out_edges(self, edge):
        Adds an output edge to the joint.
    worker(self, i):
        Worker process that processes items by combining two items.
    behaviour(self):
        Combiner behavior that creates workers based on the effective capacity.

    Raises
    -------
    ValueError
        If the joint already has the maximum number of input or output edges.
    AssertionError
        If the joint does not have exactly 2 input edges or 1 output edge in the behaviour function.
    """ 
    def __init__(self, env, name,in_edges=None , out_edges=None, work_capacity=1, store_capacity=1, delay=1):
        super().__init__(env, name,in_edges , out_edges,  work_capacity=1, store_capacity=1, delay=0)
        self.env = env
        self.name = name
        self.work_capacity = work_capacity
        self.store_capacity = store_capacity
      

        self.in_edge_events={}

        
        self.in_edges = in_edges
        self.out_edges = out_edges
        self.inbuiltstore = ReservablePriorityReqStore(env, capacity=store_capacity)  # Custom store with reserve capacity
        self.resource = simpy.Resource(env, capacity=min(work_capacity,store_capacity))  # Work capacity
        self.delay = delay  # Processing delay

        if work_capacity > store_capacity:
            print("Warning: Effective capacity is limited by the minimum of work_capacity and store_capacity.")

        # Start the behaviour process
        self.env.process(self.behaviour())

    def add_in_edges(self, edge):
        if self.in_edges is None:
            self.in_edges = []
        
        if len(self.in_edges) >= 2:
            raise ValueError(f"Joint '{self.name}' already has 2 in_edges. Cannot add more.")
        
        if edge not in self.in_edges:
            self.in_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Joint '{self.name}' in_edges.")

    def add_out_edges(self, edge):
        if self.out_edges is None:
            self.out_edges = []

        if len(self.out_edges) >= 1:
            raise ValueError(f"Joint '{self.name}' already has 1 out_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Joint '{self.name}' out_edges.")

    def worker(self, i):
        """Worker process that processes items by combining two items."""
        while True:
            with self.resource.request() as req:
                yield req  # Wait for work capacity
                put_event  = self.inbuiltstore.reserve_put()  # Wait for a reserved slot if needed
                yield put_event
                print(f"At time {self.env.now:.2f}: worker {i} reserving space for combined item")

                # Retrieve two items from input_store for combining
               
                   
                self.in_edge_events[i] = [edge.inbuiltstore.reserve_get() for edge in self.in_edges]

                #waiting for one of the events to trigger
                edgeevents= self.env.all_of(self.in_edge_events[i])  # Wait for a reserved slot if needed# """A :class:`~simpy.events.Condition` event that is triggered if any of
                print(f"Time {self.env.now:.2f}:{self.name} worker{i} waiting to yield reserve_get from {[edge for edge in self.in_edges]}")
                yield edgeevents
                

                
                


                # get the triggered item
                
                item1 = self.in_edge_events[i][0].resourcename.get(self.in_edge_events[i][0]) # event corresponding to reserve_get is in self.triggered_item[i]
                item2 = self.in_edge_events[i][1].resourcename.get(self.in_edge_events[i][1]) # event corresponding to reserve_get is in self.triggered_item[i]




              

                print(f"At time {self.env.now:.2f}: worker {i} retrieved items {item1.name} and {item2.name} for combining")

                # Simulate processing delay for combining items
                yield self.env.timeout(self.delay)

                # Create a combined output item and put it in the combiner's store
                combined_item = Item(name=f"Combined_{item1.name}_{item2.name}")
                self.inbuiltstore.put(put_event, combined_item)

                print(f"At time {self.env.now:.2f}: worker {i} placed combined item {combined_item.name} into combiner store")

    def behaviour(self):
        """Combiner behavior that creates workers based on the effective capacity."""

        assert self.in_edges is not None and len(self.in_edges) == 2, f"Joint '{self.name}' must have exactly 2 in_edges."
        assert self.out_edges is not None and len(self.out_edges) == 1, f"Joint '{self.name}' must have exactly 1 out_edge."
        cap = min(self.work_capacity, self.store_capacity)
        for i in range(cap):
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay
