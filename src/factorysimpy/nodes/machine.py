# Machine m input and 1 output without using cancel

from typing import Generator  # Import Generator for type checking


import  random, simpy


from factorysimpy.nodes.node import Node
from factorysimpy.edges.conveyor import ConveyorBelt
from factorysimpy.edges.buffer import Buffer
from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore  # Import your class


from typing import Generator





class Machine(Node):
    """
        Machine class representing a processing node in a factory simulation.
        Inherits from the Node class.
        This Machine can have multiple input edges and  output edges.

        Parameters:
            inbuiltstore (ReservablePriorityReqStore): Internal storage used for buffering items after processing.
            store_capacity (int): Maximum capacity of the internal storage.
            work_capacity (int): Maximum number of items that can be processed simultaneously.
            processing_delay (None, int, float, Generator, Callable): Delay for processing items. Can be:
                
                - None: Used when the processing time depends on parameters like the current state or time.
                - int or float: Used as a constant delay.
                - Generator: A generator function yielding delay values over time.
                - Callable: A function that returns a delay (int or float).
            out_edge_selection (None or str or callable): Criterion or function for selecting the out edge.
                                              Options include "RANDOM", "FIRST", "LAST", "ROUND_ROBIN", "FIRST_AVAILABLE".

                - None: None: Used when out edge selction depends on parameters like current state of the object or time.   
                - str: A string that specifies the selection method.
                    - "RANDOM": Selects a random out edge.
                    - "FIRST": Selects the first out edge.
                    - "LAST": Selects the last out edge.
                    - "ROUND_ROBIN": Selects out edges in a round-robin manner.
                    - "FIRST_AVAILABLE": Selects the first out edge that can accept an item.
                - callable: A function that returns an edge index.
                

        

        Raises:
            AssertionError: If the Machine has no input or output edges.
            
    """

    def __init__(self, env, id, in_edges=None, out_edges=None,node_setup_time=0, work_capacity=1, store_capacity=1 ,processing_delay=0):
        super().__init__(env, id,in_edges, out_edges, node_setup_time=node_setup_time)
    
        self.store_capacity = store_capacity
        self.work_capacity = work_capacity
        self.in_edge_events={}
        self.itemprocessed={}
        self.triggered_item={}
        self.in_edges = in_edges
        self.out_edges = out_edges
        self.stats= {
            "current_state": None,
            "last_state_change_time": None,
            "num_item_processed": 0,
            "num_item_discarded": 0,
            "total_time_spent_in_state":{}
        }
        self.inbuiltstore = ReservablePriorityReqStore(env, capacity=store_capacity)  # Custom store with reserve capacity
        self.resource = simpy.Resource(env, capacity=min(work_capacity,store_capacity))  # Work capacity
        if work_capacity > store_capacity:
            print("Warning: Effective capacity is limited by the minimum of work_capacity and store_capacity.")


        # Initialize delay as a generator or a constant
        if isinstance(processing_delay, Generator):
            self.processing_delay = processing_delay 
        elif isinstance(processing_delay, (int, float)):
            self.processing_delay = processing_delay
        elif callable(processing_delay):
            self.processing_delay = processing_delay
        elif processing_delay is None:
            self.processing_delay = None
        else:
            raise ValueError(
                "Invalid delay value. Provide a constant(int or float) or generator or python function or None."
            )
        
        def reset(self):
            if self.processing_delay is None:
                raise ValueError("Processing delay cannot be None.")
            if self.out_edge_selection is None:
                raise ValueError("out_edge_selection should not be None.")
        # Start the behaviour process
        self.env.process(self.behaviour())
        self.env.process(self.pushingput())

    def update_state(self, new_state: str, current_time: float):
        """
        Update node state and track the time spent in the previous state.
        
        Args:
            new_state (str): The new state to transition to. Must be one of "SETUP_STATE", "GENERATING_STATE", "BLOCKED_STATE".
            current_time (float): The current simulation time.

        """
        
        if self.state is not None and self.stats["last_state_change_time"] is not None:
            elapsed = current_time - self.stats["last_state_change_time"]

            self.stats["total_time_spent_in_states"][self.state] = (
                self.stats["total_time_spent_in_states"].get(self.state, 0.0) + elapsed
            )
        self.state = new_state
        self.stats["last_state_change_time"] = current_time
        
 

       
        
    


    def add_in_edges(self, edge):
        """
        Adds an in_edge to the node. Raises an error if the edge already exists in the in_edges list.
        
        Args:
            edge (Edge Object) : The edge to be added as an in_edge.
            """
        if self.in_edges is None:
            self.in_edges = []
        
        if len(self.in_edges) >= self.num_in_edges:
            raise ValueError(f"Machine'{self.id}' already has {self.num_in_edges} in_edges. Cannot add more.")
        
        if edge not in self.in_edges:
            self.in_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Machine '{self.id}' in_edges.")

    def add_out_edges(self, edge):
        """
        Adds an out_edge to the node. Raises an error if the edge already exists in the out_edges list.
        
        Args:
            edge (Edge Object) : The edge to be added as an out_edge.
        """
        if self.out_edges is None:
            self.out_edges = []

        if len(self.out_edges) >= 1:
            raise ValueError(f"Machine '{self.id}' already has 1 out_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Machine '{self.id}' out_edges.")
        
   
    
    def pushingput(self):
        while True:
            get_token = self.inbuiltstore.reserve_get()
            if isinstance(self.out_edges[0], ConveyorBelt):

                    outstore = self.out_edges[0]
                    put_token = outstore.reserve_put()

                    pe = yield put_token
                    yield get_token
                    item = self.inbuiltstore.get(get_token)
                    yield outstore.put(pe, item)
                    
            else:
                    outstore = self.out_edges[0].inbuiltstore
                    put_token = outstore.reserve_put()
                    yield self.env.all_of([put_token,get_token])
                    item = self.inbuiltstore.get(get_token)
                    outstore.put(put_token, item)

            print(f"T={self.env.now:.2f}: {self.id} puts item into {self.out_edges[0].id}  ")



    def worker(self, i):
        #Worker process that processes items with resource and reserve handling."""
        self.reset()
        while True:
            print(f"T={self.env.now:.2f}: {self.id} worker{i} started processing")
            # with self.resource.request() as req:
            #     assert len(self.inbuiltstore.items) + len(self.inbuiltstore.reservations_put) <= self.store_capacity, (
            #         f'Resource util exceeded: {len(self.inbuiltstore.items)}, {len(self.inbuiltstore.reservations_put)}'
            #     )
            #     yield req  # Wait for work capacity
            print(f"T={self.env.now:.2f}: {self.id} worker{i} acquired resource")
            P1 = self.inbuiltstore.reserve_put()
            yield P1
            print(f"T={self.env.now:.2f}: {self.id} worker{i} reserved put slot")

            start_wait = self.env.now

            # Only initialize if not already set or all previous events consumed
            if i not in self.in_edge_events or not self.in_edge_events[i]:
                self.in_edge_events[i] = [
                    (edge, edge.reserve_get() if isinstance(edge, ConveyorBelt) else edge.out_store.reserve_get())
                    for edge in self.in_edges
                ]

            event_list = [e for _, e in self.in_edge_events[i]]
            print(f"T={self.env.now:.2f}: {self.id} worker{i} waiting on input events from {[edge.id for edge, _ in self.in_edge_events[i]]}")

            result = yield self.env.any_of(event_list)

            # Identify triggered event and corresponding edge
            triggered = next(((edge, e) for edge, e in self.in_edge_events[i] if e.triggered), (None, None))
            edge_used, triggered_event = triggered

            if edge_used is None:
                raise RuntimeError(f"{self.id} worker{i} - No triggered event found!")

            # Remove the triggered pair from the event list
            #print(result, triggered_event)
            self.in_edge_events[i].remove((edge_used, triggered_event))

            # Get the item from the appropriate store
            if isinstance(edge_used, ConveyorBelt):
                self.itemprocessed[i] =  yield edge_used.get(result[triggered_event])

                #print(self.itemprocessed[i])

            else:
                self.itemprocessed[i] = edge_used.out_store.get(triggered_event)

            wait_time = self.env.now - start_wait
            print(f"T={self.env.now:.2f}: {self.id} worker{i} waited {wait_time:.2f} time units for item from {edge_used.id}")
            print(f"T={self.env.now:.2f}: {self.id} worker{i} processing item: {self.itemprocessed[i].id}")

            # Simulate processing time
            self.processing_time = next(self.processing_delay) if isinstance(self.processing_delay, Generator) else self.processing_delay
            yield self.env.timeout(self.processing_time)

            # Put item into internal store
            self.inbuiltstore.put(P1, self.itemprocessed[i])
            print(f"T={self.env.now:.2f}: {self.id} worker{i} placed item into internal store")

                
                

    def behaviour(self):
        #Machine behavior that creates workers based on the effective capacity."""
        
        
        assert self.in_edges is not None and len(self.in_edges) >= 1, f"Machine '{self.id}' must have atleast 1 in_edge."
        assert self.out_edges is not None and len(self.out_edges) >= 1, f"Machine '{self.id}' must have atleast 1 out_edge."
        cap = min(self.store_capacity, self.work_capacity)
        for i in range(cap):
            print(f"T={self.env.now:.2f}: {self.id} creating worker {i+1}")
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay

