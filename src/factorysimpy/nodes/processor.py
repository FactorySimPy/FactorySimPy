# Processor m input and 1 output without using cancel

from typing import Generator  # Import Generator for type checking


import simpy


from factorysimpy.nodes.node import Node
from factorysimpy.edges.conveyor import ConveyorBelt
from factorysimpy.edges.buffer import Buffer
from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore  # Import your class


from typing import Generator
import simpy




class Processor(Node):
    """
            Processor class representing a processing node in a factory simulation.
            Inherits from the Node class.
            This processor can have multiple input edges and a single output edge.

            Attributes
            ----------
            in_edge_events : dict
                Dictionary to track input events for each worker.
            triggered_item : dict
                Tracks which input event triggered for each worker.
            itemprocessed : dict
                Tracks item currently being processed by each worker.
            inbuiltstore : ReservablePriorityReqStore
                Internal storage used for item buffering.
            resource : simpy.Resource
                SimPy resource modeling concurrent work capacity.

            Methods     
            -------
        
            worker(self, i):
                Worker process that processes items with resource and reserve handling.
            behaviour(self):
                Processor behavior that creates workers based on the effective capacity.

            add_in_edges(self, edge):
                Adds an input edge to the processor.
            add_out_edges(self, edge):
                Adds an output edge to the processor.
            
        Raises
            -------
            ValueError
                If the processor already has the maximum number of input or output edges.
            AssertionError
                If the processor does not have at least 1 input edge or 1 output edge in the behaviour function.
            AssertionError
                If the processor's work_capacity > store_capacity.
            """

    def __init__(self, env, name, in_edges=None, out_edges=None, work_capacity=1, store_capacity=1, delay=1):
        super().__init__(env, name,in_edges, out_edges,  work_capacity=work_capacity, store_capacity=store_capacity, delay=delay)
        self.env = env
        self.name = name
        self.store_capacity = store_capacity
        self.work_capacity = work_capacity
        self.in_edge_events={}

        self.itemprocessed={}
        self.triggered_item={}
        self.in_edges = in_edges
        self.out_edges = out_edges
        self.inbuiltstore = ReservablePriorityReqStore(env, capacity=store_capacity)  # Custom store with reserve capacity
        self.resource = simpy.Resource(env, capacity=min(work_capacity,store_capacity))  # Work capacity
        if work_capacity > store_capacity:
            print("Warning: Effective capacity is limited by the minimum of work_capacity and store_capacity.")
  

       
        
        # Start the behaviour process
        self.env.process(self.behaviour())
        self.env.process(self.pushingput())


    def add_in_edges(self, edge):
        if self.in_edges is None:
            self.in_edges = []
        
        if len(self.in_edges) >= self.num_in_edges:
            raise ValueError(f"Processor'{self.name}' already has {self.num_in_edges} in_edges. Cannot add more.")
        
        if edge not in self.in_edges:
            self.in_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Processor '{self.name}' in_edges.")

    def add_out_edges(self, edge):
        if self.out_edges is None:
            self.out_edges = []

        if len(self.out_edges) >= 1:
            raise ValueError(f"Processor '{self.name}' already has 1 out_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Processor '{self.name}' out_edges.")
        
    def _getedge(self, edge):
        attr_map = {
            ConveyorBelt: "belt",
            Buffer: "out_store"
        }
        # Default to 'inbuiltstore' if not matched
        attr_name = next((v for k, v in attr_map.items() if isinstance(edge, k)), "inbuiltstore")
        #print(f"Processor: {self.name} - Edge: {edge.name} - Attribute: {attr_name}  {getattr(edge, attr_name)}")
        return getattr(edge, attr_name)
    
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




    def worker(self,i):
        """Worker process that processes items with resource and reserve handling."""
        while True:

            with self.resource.request() as req:
                assert len(self.inbuiltstore.items)+len(self.inbuiltstore.reservations_put)<=self.store_capacity, (f'Resource util exceeded{self.inbuiltstore.items[1],{len(self.inbuiltstore.items)},len(self.inbuiltstore.reservations_put)}')
                yield req  # Wait for work capacity

                P1 = self.inbuiltstore.reserve_put()  # Wait for a reserved slot if needed
                yield P1
                print(f"T={self.env.now:.2f}: {self.name} worker{i} yielded reserve_put from {self.name}")

                start_wait = self.env.now
                #checks if worker i is not added in the dictionary. or if there are no triggered events inside the  in_edge_events for the worker
                #Else it will use previously triggered events
                if i not in self.in_edge_events or not self.in_edge_events[i]:
            
                    self.in_edge_events[i] = [edge.reserve_get() if isinstance(edge, ConveyorBelt) else edge.out_store.reserve_get() for edge in self.in_edges]

                print(f"T={self.env.now:.2f}: {self.name} worker{i} waiting on input edges")
                  

                #waiting for one of the events to trigger
                k= self.env.any_of(self.in_edge_events[i])  # Wait for a reserved slot if needed# """A :class:`~simpy.events.Condition` event that is triggered if any of
                print(f"T={self.env.now:.2f}: {self.name} worker{i} waiting to yield reserve_get from {[edge.name for edge in self.in_edges]}")
                yield k
                

                # Find the first triggered item and remove it from the list
                self.triggered_item[i] = next((event for event in self.in_edge_events[i] if event.triggered), None)
                if self.triggered_item[i]:
                   self.in_edge_events[i].remove(self.triggered_item[i])


                # Yield the triggered item
                if self.triggered_item[i]:
                    #print(f"T={self.env.now:.2f}: {self.name} worker{i} triggered item is {self.triggered_item[i]}")
                    self.itemprocessed[i] = self.triggered_item[i].resourcename.get(self.triggered_item[i]) # event corresponding to reserve_get is in self.triggered_item[i]

                wait_time = self.env.now - start_wait
                print(f"T={self.env.now:.2f}: {self.name} worker{i} waiting time to get an item from source is {wait_time}")
                #self.monitor.record_waiting_time(wait_time)
                #assert self.store.itemcount[1]+len(self.store.reservations_put)<=self.c, (f'Resource util exceeded {self.store.itemcount[1]}+{len(self.store.reservation.users)}<={self.c}')
                print(f"T={self.env.now:.2f}: {self.name} worker{i} yielded items {self.itemprocessed}")
                print(f"T={self.env.now:.2f}: {self.name} worker{i} Worker got an item and is processing -{ self.itemprocessed[i].name}")

                #self.monitor.record_start(self.env.now)


                # Simulate processing delay

                self.delay_time = next(self.delay) if isinstance(self.delay, Generator) else self.delay
                
                #print("hahaha",self.delay_time)
                yield self.env.timeout(self.delay_time)
                self.inbuiltstore.put(P1, self.itemprocessed[i])
                #self.monitor.record_end(self.env.now)
                print(f"T={self.env.now:.2f}: {self.name} worker{i} puts item into its store ")
                
                

    def behaviour(self):
        """Processor behavior that creates workers based on the effective capacity."""
        
        
        assert self.in_edges is not None and len(self.in_edges) >= 1, f"Processor '{self.name}' must have atleast 1 in_edge."
        assert self.out_edges is not None and len(self.out_edges) >= 1, f"Processor '{self.name}' must have atleast 1 out_edge."
        cap = min(self.store_capacity, self.work_capacity)
        for i in range(cap):
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay

