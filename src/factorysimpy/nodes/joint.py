# @title Joint
from typing import Generator
import simpy ,os, sys


from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore  # Import your class
from factorysimpy.nodes.node import Node
from factorysimpy.edges.conveyor import ConveyorBelt

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
        super().__init__(env, name,in_edges=in_edges , out_edges=out_edges,  work_capacity=work_capacity, store_capacity=store_capacity, delay=delay)
        self.env = env
        self.name = name
        self.work_capacity = work_capacity
        self.store_capacity = store_capacity
      

        self.in_edge_events={}

        self.node_type = "Joint"

        
        self.in_edges = in_edges
        self.out_edges = out_edges
        self.inbuiltstore = ReservablePriorityReqStore(env, capacity=store_capacity)  # Custom store with reserve capacity
        self.resource = simpy.Resource(env, capacity=min(work_capacity,store_capacity))  # Work capacity
        

        if work_capacity > store_capacity:
            print("Warning: Effective capacity is limited by the minimum of work_capacity and store_capacity.")

        # Start the processes
        self.env.process(self.behaviour())
        self.env.process(self.pushingput())

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
        
    def pushingput(self):
        while True:
            get_token = self.inbuiltstore.reserve_get()
            if isinstance(self.out_edges[0], ConveyorBelt):

                    outstore = self.out_edges[0]
                    put_token = outstore.reserve_put()

                    pe = yield put_token
                    yield get_token
                    item = self.inbuiltstore.get(get_token)
                    outstore.put(pe, item)
                    
            else:
                    outstore = self.out_edges[0].inbuiltstore
                    put_token = outstore.reserve_put()
                    yield self.env.all_of([put_token,get_token])
                    item = self.inbuiltstore.get(get_token)
                    outstore.put(put_token, item)

            print(f"T={self.env.now:.2f}: {self.name} puts item into {self.out_edges[0].name}  ")

    def worker(self, i):
        """Worker process that processes items by combining two items."""
        while True:
            with self.resource.request() as req:
                yield req  # Wait for work capacity
                put_event  = self.inbuiltstore.reserve_put()  # Wait for a reserved slot if needed
                yield put_event
                print(f"T={self.env.now:.2f}: {self.name} worker {i} reserving space for combined item")

                # Retrieve two items from input_store for combining
               
                   
                # Reserve from all input edges
                self.in_edge_events[i] = [
                    (edge, edge.reserve_get() if isinstance(edge, ConveyorBelt) else edge.out_store.reserve_get())
                    for edge in self.in_edges
                ]

                print(f"T={self.env.now:.2f}: {self.name} worker{i} waiting to reserve from {[edge.name for edge, _ in self.in_edge_events[i]]}")

                # Wait for all reservations
                reserve_events = [event for _, event in self.in_edge_events[i]]
                yield self.env.all_of(reserve_events)

                # Perform get() on each edge
                items = []
                for edge, event in self.in_edge_events[i]:
                    if isinstance(edge, ConveyorBelt):
                        item = yield edge.get(reserve_events[event])
                    else:
                        item = edge.out_store.get(event)
                    items.append(item)

                # Now `items` contains all the input items from each edge
                print(f"T={self.env.now:.2f}: {self.name} worker{i} got items: {[item.name for item in items]}")





              

                print(f"T={self.env.now:.2f}: {self.name} worker {i} retrieved items {items[0].name} and {items[1].name} for combining")

                # Simulate processing delay for combining items
                self.delay_time = next(self.delay) if isinstance(self.delay, Generator) else self.delay
                yield self.env.timeout(self.delay_time)

                # Create a combined output item and put it in the combiner's store
                combined_item = Item(name=f"Combined_{items[0].name}_{items[1].name}")
                self.inbuiltstore.put(put_event, combined_item)

                print(f"T={self.env.now:.2f}: {self.name} worker {i} placed combined item {combined_item.name} into its store")

    def behaviour(self):
        """Combiner behavior that creates workers based on the effective capacity."""

        assert self.in_edges is not None and len(self.in_edges) == 2, f"Joint '{self.name}' must have exactly 2 in_edges."
        assert self.out_edges is not None and len(self.out_edges) == 1, f"Joint '{self.name}' must have exactly 1 out_edge."
        cap = min(self.work_capacity, self.store_capacity)
        for i in range(cap):
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay
