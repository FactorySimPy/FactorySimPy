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
                Machine behavior that creates workers based on the effective capacity.

            add_in_edges(self, edge):
                Adds an input edge to the Machine.
            add_out_edges(self, edge):
                Adds an output edge to the Machine.
            
        Raises     
        -------

            ValueError
                If the Machine already has the maximum number of input or output edges.
            AssertionError
                If the Machine does not have at least 1 input edge or 1 output edge in the behaviour function.
            AssertionError
                If the Machine's work_capacity > store_capacity.
    """

    def __init__(self, env, id, in_edges=None, out_edges=None, work_capacity=1, store_capacity=1, node_setup_time=0,processing_delay=0):
        super().__init__(env, id,in_edges, out_edges, node_setup_time=node_setup_time)
    
        self.store_capacity = store_capacity
        self.work_capacity = work_capacity
        self.in_edge_events={}
        self.itemprocessed={}
        self.triggered_item={}
        self.in_edges = in_edges
        self.out_edges = out_edges
        self.class_statistics = {
            "current_state": None,
            "last_state_change_time": None,
            "item_processed": 0,
            "item_discarded": 0,
            "state_times":{}
        }
        self.inbuiltstore = ReservablePriorityReqStore(env, capacity=store_capacity)  # Custom store with reserve capacity
        self.resource = simpy.Resource(env, capacity=min(work_capacity,store_capacity))  # Work capacity
        if work_capacity > store_capacity:
            print("Warning: Effective capacity is limited by the minimum of work_capacity and store_capacity.")


        # Initialize delay as a generator or a constant
        if isinstance(processing_delay, Generator):
            self.processing_delay = processing_delay
        elif isinstance(processing_delay, tuple) and len(processing_delay) == 2:
            self.processing_delay = self.random_delay_generator(processing_delay)
      

        elif isinstance(processing_delay, (int, float)):
            self.processing_delay = processing_delay
        else:
            raise ValueError(
                "Invalid delay value. Provide a constant, generator, or a (min, max) tuple."
            )
        # Start the behaviour process
        self.env.process(self.behaviour())
        self.env.process(self.pushingput())

    def update_state_time(self, new_state: str, current_time: float):
        """
        Update node state and track the time spent in the previous state.
        """
        print(self.class_statistics)
        if self.class_statistics["current_state"] is not None and self.class_statistics["last_state_change_time"] is not None:
            elapsed = current_time - self.class_statistics["last_state_change_time"]

            self.class_statistics["state_times"][self.class_statistics["current_state"]] = (
                self.class_statistics["state_times"].get(self.class_statistics["current_state"], 0.0) + elapsed
            )

        self.class_statistics["current_state"] = new_state
        self.class_statistics["last_state_change_time"] = current_time
        
    def random_delay_generator(self, delay_range: tuple) -> Generator:
        """
        Yields random delays within a specified range.

        Parameters
        ----------
        delay_range : tuple
            A (min, max) tuple for random delay values.

        Yields
        ------
        int
            A random delay time in the given range.
        """
        while True:
            yield random.randint(*delay_range)
  

       
        
    


    def add_in_edges(self, edge):
        if self.in_edges is None:
            self.in_edges = []
        
        if len(self.in_edges) >= self.num_in_edges:
            raise ValueError(f"Machine'{self.id}' already has {self.num_in_edges} in_edges. Cannot add more.")
        
        if edge not in self.in_edges:
            self.in_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Machine '{self.id}' in_edges.")

    def add_out_edges(self, edge):
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
        """Worker process that processes items with resource and reserve handling."""
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
        """Machine behavior that creates workers based on the effective capacity."""
        
        
        assert self.in_edges is not None and len(self.in_edges) >= 1, f"Machine '{self.id}' must have atleast 1 in_edge."
        assert self.out_edges is not None and len(self.out_edges) >= 1, f"Machine '{self.id}' must have atleast 1 out_edge."
        cap = min(self.store_capacity, self.work_capacity)
        for i in range(cap):
            print(f"T={self.env.now:.2f}: {self.id} creating worker {i+1}")
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay

