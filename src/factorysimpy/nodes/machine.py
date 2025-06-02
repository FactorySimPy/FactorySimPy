# Machine m input and 1 output without using cancel

from typing import Generator  # Import Generator for type checking


import  random, simpy


from factorysimpy.nodes.node import Node
from factorysimpy.edges.conveyor import ConveyorBelt
from factorysimpy.utils.utils import get_index_selector
from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore  # Import your class








class Machine(Node):
    """
        Machine represents a processing node in a factory simulation.
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
            in_edge_selection (None or str or callable): Criterion or function for selecting the edge.
                                              Options include "RANDOM", "FIRST", "LAST", "ROUND_ROBIN", "FIRST_AVAILABLE".

                - None: None: Used when edge selction depends on parameters like current state of the object or time.   
                - str: A string that specifies the selection method.
                    - "RANDOM": Selects a random edge.
                    - "FIRST": Selects the first edge in the in_edges list.
                    - "LAST": Selects the last edge in the in_edges list .
                    - "ROUND_ROBIN": Selects edges in a round-robin manner.
                    - "FIRST_AVAILABLE": Selects the first out edge that can give an item.
                - callable: A function that returns an edge index.
            out_edge_selection (None or str or callable): Criterion or function for selecting the out edge.
                                              Options include "RANDOM", "FIRST", "LAST", "ROUND_ROBIN", "FIRST_AVAILABLE".

                - None: None: Used when out edge selction depends on parameters like current state of the object or time.   
                - str: A string that specifies the selection method.
                    - "RANDOM": Selects a random out edge in the out_edges list.
                    - "FIRST": Selects the first out edge in the out_edges list.
                    - "LAST": Selects the last out edge in the out_edges list.
                    - "ROUND_ROBIN": Selects out edges in a round-robin manner.
                    - "FIRST_AVAILABLE": Selects the first out edge that can accept an item.
                - callable: A function that returns an edge index.
                

        

        Raises:
            AssertionError: If the Machine has no input or output edges.
            
    """

    def __init__(self, env, id, in_edges=None, out_edges=None,node_setup_time=0, work_capacity=1, store_capacity=1 ,processing_delay=0,in_edge_selection="FIRST",out_edge_selection="FIRST"):
        super().__init__(env, id,in_edges, out_edges, node_setup_time)
    
        self.store_capacity = store_capacity
        self.work_capacity = work_capacity
        self.in_edge_events={}
        self.item_to_process={}
        self.triggered_item={}
     
        self.stats = {
            "last_state_change_time": None,
            "num_item_processed": 0,
            "total_time_spent_in_states":{"SETUP_STATE": 0.0,"IDLE_STATE": 0.0, "PROCESSING_STATE": 0.0, "BLOCKED_STATE": 0.0}
        }

        self.inbuiltstore = ReservablePriorityReqStore(env, capacity=store_capacity)  # Custom store with reserve capacity
        self.resource = simpy.Resource(env, capacity=min(work_capacity,store_capacity))  # Work capacity
        if work_capacity > store_capacity:
            print("Warning: Effective capacity is limited by the minimum of work_capacity and store_capacity.")


        # Initialize processing delay 
        if callable(processing_delay):
            self.processing_delay = processing_delay 
        elif isinstance(processing_delay, (int, float)):
            self.processing_delay = processing_delay
        elif processing_delay is None:
            self.processing_delay = None
        else:
            raise ValueError(
                "processing_delay must be a None, int, float, generator, or callable."
            )
        
        # Initialize in_edge_selection and out_edge_selection
        if isinstance(in_edge_selection, str):  
            self.out_edge_selection = get_index_selector(in_edge_selection, self, env, "OUT")
        elif callable(in_edge_selection):
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.in_edge_selection = in_edge_selection
        elif out_edge_selection is None:
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.in_edge_selection = in_edge_selection
        else:
            raise ValueError("in_edge_selection must be a None, string or a callable (function/generator)")
        
        
        if isinstance(out_edge_selection, str):  
            self.out_edge_selection = get_index_selector(out_edge_selection, self, env, "IN")
        elif callable(out_edge_selection):
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.out_edge_selection = out_edge_selection
        elif out_edge_selection is None:
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.out_edge_selection = out_edge_selection
        else:
            raise ValueError("out_edge_selection must be a None, string or a callable (function/generator)")  
        
        self.env.process(self.behaviour())
      
    def reset(self):
            if self.processing_delay is None:
                raise ValueError("Processing delay cannot be None.")
            if self.in_edge_selection is None:
                raise ValueError("in_edge_selection should not be None")
            if self.out_edge_selection is None:
                raise ValueError("out_edge_selection should not be None.")
        

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
        
        # if len(self.in_edges) >= self.num_in_edges:
        #     raise ValueError(f"Machine'{self.id}' already has {self.num_in_edges} in_edges. Cannot add more.")
        
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

        # if len(self.out_edges) >= 1:
        #     raise ValueError(f"Machine '{self.id}' already has 1 out_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Machine '{self.id}' out_edges.")
        
    def _get_out_edge_index(self):
        
        #Returns the next edge index from out_edge_selection, whether it's a generator or a callable.
        
        
        if hasattr(self.out_edge_selection, '__next__'):
            # It's a generator
            return next(self.out_edge_selection)
        elif callable(self.out_edge_selection):
            # It's a function (pass self and env if needed)
            return self.out_edge_selection(self, self.env)
        else:
            raise ValueError("out_edge_selection must be a generator or a callable.") 
        
    def _get_in_edge_index(self):
        
        #Returns the next edge index from in_edge_selection, whether it's a generator or a callable.
        
        
        if hasattr(self.in_edge_selection, '__next__'):
            # It's a generator
            return next(self.in_edge_selection)
        elif callable(self.in_edge_selection):
            # It's a function (pass self and env if needed)
            return self.in_edge_selection(self, self.env)
        else:
            raise ValueError("in_edge_selection must be a generator or a callable.") 
    
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

    def _push_item(self, item, out_edge):
        if out_edge.__class__.__name__ == "ConveyorBelt":                 
                put_token = out_edge.reserve_put()
                pe = yield put_token
                y=out_edge.put(pe, item)
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts {item.id} item into {out_edge.id}  ")
        elif out_edge.__class__.__name__ == "Buffer":
                outstore = out_edge.inbuiltstore
                put_token = outstore.reserve_put()
                yield put_token
                y=outstore.put(put_token, item)
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts item into {self.out_edges[0].id} inbuiltstore {y} ")
        else:
                raise ValueError(f"Unsupported edge type: {out_edge.__class__.__name__}")
        
    def _pull_item(self,i, in_edge):
        if in_edge.__class__.__name__ == "ConveyorBelt":
                get_token = in_edge.reserve_get()
                gtoken = yield get_token
                self.item_to_process[i]=yield in_edge.get(gtoken)
                if self.item_to_process[i]:
                    print(f"T={self.env.now:.2f}: {self.id} gets item {self.item_to_process[i].id} from {in_edge.id}  ")
                
        elif in_edge.__class__.__name__ == "Buffer":
                outstore = in_edge.out_store
                get_token = outstore.reserve_get()
                yield get_token
                self.item_to_process[i] =outstore.get(get_token)
                if self.item_to_process[i]:
                    print(f"T={self.env.now:.2f}: {self.id} gets item {self.item_to_process[i].id} from {in_edge.id} ")
        else:
                raise ValueError(f"Unsupported edge type: {in_edge.__class__.__name__}")



    def worker(self, i):
        #Worker process that processes items with resource and reserve handling."""
        self.reset()
        while True:
            print(f"T={self.env.now:.2f}: {self.id} worker{i} started processing")
            if self.state == "SETUP_STATE":
                print(f"T={self.env.now:.2f}: {self.id} worker{i} is in SETUP_STATE")
                node_setup_delay = self.get_delay(self.node_setup_time)
                if not isinstance(node_setup_delay, (int, float)):
                    raise AssertionError("node_setup_time returns an valid value. It should be int or float")
                yield self.env.timeout(node_setup_delay)
                self.update_state("IDLE_STATE", self.env.now)
            
            elif self.state == "IDLE_STATE":
                print(f"T={self.env.now:.2f}: {self.id} worker{i} is in IDLE_STATE")
                P1 = self.inbuiltstore.reserve_put()
                yield P1
                print(f"T={self.env.now:.2f}: {self.id} worker{i} reserved put slot")

                # Wait for the next item to process
                edgeindex_to_get = self._get_in_edge_index()
                in_edge = self.in_edges[edgeindex_to_get]
                yield self.env.process(self._pull_item(i,in_edge))
                self.update_state("PROCESSING_STATE", self.env.now)

            elif self.state == "PROCESSING_STATE":
                 if self.item_to_process[i] is None:
                   raise RuntimeError(f"{self.id} worker{i} - No item to process!")
                 next_processing_time = self.get_delay(self.processing_delay)
                 if not isinstance(next_processing_time, (int, float)):
                        raise AssertionError("processing_delay returns an valid value. It should be int or float")
                 yield self.env.timeout(next_processing_time)
                 self.stats["num_item_processed"] += 1
                 print(f"T={self.env.now:.2f}: {self.id} worker{i} processed item: {self.item_to_process[i].id}")
                 out_edge_index_to_put = self._get_out_edge_index()
                 outedge_to_put = self.out_edges[out_edge_index_to_put]
                 self.update_state("BLOCKED_STATE", self.env.now)
                 yield self.env.process(self._push_item(self.item_to_process[i], outedge_to_put))
                 self.update_state("IDLE_STATE", self.env.now)
            else:
                raise ValueError(f"Invalid state: {self.state} for worker {i} in Machine {self.id}")    
            
          
                
                

    def behaviour(self):
        #Machine behavior that creates workers based on the effective capacity."""
        
        
        assert self.in_edges is not None and len(self.in_edges) >= 1, f"Machine '{self.id}' must have atleast 1 in_edge."
        assert self.out_edges is not None and len(self.out_edges) >= 1, f"Machine '{self.id}' must have atleast 1 out_edge."
        cap = min(self.store_capacity, self.work_capacity)
        for i in range(cap):
            print(f"T={self.env.now:.2f}: {self.id} creating worker {i+1}")
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay

