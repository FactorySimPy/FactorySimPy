# @title Split
import random
from typing import Generator
import simpy

from factorysimpy.base.reservable_priority_req_filter_store import ReservablePriorityReqFilterStore  # Import your class
from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore  # Import your class
from factorysimpy.nodes.node import Node
from factorysimpy.edges.conveyor import ConveyorBelt
from factorysimpy.edges.buffer import Buffer
from factorysimpy.utils.utils import get_index_selector

from factorysimpy.helper.item import Item


class Split(Node):
    """
    Split class representing a processing node that can split an incoming item in a factory simulation.
    
    Attributes
    ----------
   
    
   
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
    def __init__(self, env, id,in_edges=None, out_edges=None, node_setup_time=0, work_capacity=1, store_capacity=1 ,processing_delay=0,in_edge_selection="FIRST",out_edge_selection="FIRST"):
        super().__init__(env, id, in_edges , out_edges, node_setup_time)
    
        self.work_capacity = work_capacity
        self.store_capacity = store_capacity
   
       
       
        self.inbuiltstore = ReservablePriorityReqFilterStore(env, capacity=store_capacity)  # Custom store with reserve capacity
        self.inbuiltstoreA = ReservablePriorityReqStore(env, capacity=int(store_capacity/2))  # Custom store with reserve capacity
        self.inbuiltstoreB = ReservablePriorityReqStore(env, capacity=store_capacity-int(store_capacity/2))  # Custom store with reserve capacity
        self.resource = simpy.Resource(env, capacity=min(work_capacity,store_capacity))  # Work capacity
        self.stats = {
            "last_state_change_time": None,
            "num_item_processed": 0,
            "total_time_spent_in_states":{"SETUP_STATE": 0.0,"IDLE_STATE": 0.0, "PROCESSING_STATE": 0.0, "BLOCKED_STATE": 0.0}
        }

        if work_capacity>store_capacity :
            print("Warning: Effective capacity is limited by the minimum of work_capacity and store_capacity.")
        
        
        # Initialize processing delay 
        if callable(processing_delay):
            self.processing_delay = processing_delay 
        elif isinstance(processing_delay, (int, float)):
            self.processing_delay = processing_delay
        elif processing_delay is None:
            self.processing_delay = None
        else:
            raise ValueError("processing_delay must be a None, int, float, generator, or callable.")
        
        if isinstance(in_edge_selection, str):  
            self.out_edge_selection = get_index_selector(in_edge_selection, self, env)
        elif callable(in_edge_selection):
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.in_edge_selection = in_edge_selection
        elif out_edge_selection is None:
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.in_edge_selection = in_edge_selection
        else:
            raise ValueError("in_edge_selection must be a None, string or a callable (function/generator)")
        

        if isinstance(out_edge_selection, str):  
            self.out_edge_selection = get_index_selector(out_edge_selection, self, env)
        elif callable(out_edge_selection):
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.out_edge_selection = out_edge_selection
        elif out_edge_selection is None:
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.out_edge_selection = out_edge_selection
        else:
            raise ValueError("out_edge_selection must be a string or a callable (function/generator)")

         
        # Start the behaviour process
        self.env.process(self.behaviour())
        self.env.process(self.pushing_puta())
        self.env.process(self.pushing_putb())
    
    def reset(self):
            if self.processing_delay is None:
                raise ValueError("Processing delay cannot be None.")
            if self.in_edge_selection is None:
                raise ValueError("in_edge_selection should not be None")
            if self.out_edge_selection is None:
                raise ValueError("out_edge_selection should not be None.")

    def update_state(self, new_state: str, current_time: float):
        """
        Update state and track the time spent in the previous state.
        
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
        if self.in_edges is None:
            self.in_edges = []

        # if len(self.in_edges) >= 1:
        #     raise ValueError(f"Split '{self.name}' already has 1 in_edge. Cannot add more.")

        if edge not in self.in_edges:
            self.in_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Split '{self.id}' in_edges.")

    def add_out_edges(self, edge):
        if self.out_edges is None:
            self.out_edges = []

        if len(self.out_edges) >= 2:
            raise ValueError(f"Split '{self.id}' already has 2 out_edges. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Split '{self.id}' out_edges.")
    def pushing_puta(self):
        """Pushes items to the first output edge."""
        while True:
           
            #get_token = self.inbuiltstore.reserve_get(filter=lambda item: item.name.endswith('_a'))  # Wait for a reserved slot if needed 
            get_token = self.inbuiltstoreA.reserve_get()
            if isinstance(self.out_edges[0], ConveyorBelt):

                    outstore = self.out_edges[0]
                    put_token = outstore.reserve_put()

                    pe = yield put_token
                    yield get_token
                    item = self.inbuiltstoreA.get(get_token)
                    outstore.put(pe, item)
                    
            else:
                    outstore = self.out_edges[0].inbuiltstore
                    put_token = outstore.reserve_put()
                    yield self.env.all_of([get_token,put_token])
                    #yield self.env.all_of([put_token,get_token])
                    item = self.inbuiltstoreA.get(get_token)
                    outstore.put(put_token, item)

            print(f"T={self.env.now:.2f}: {self.name} puts item into {self.out_edges[0].name}  ")


    def pushing_putb(self):
        """Pushes items to the first output edge."""
    
        while True:
            #get_token = self.inbuiltstore.reserve_get(filter=lambda item: item.name.endswith('_b'))  # Wait for a reserved slot if needed 
            get_token = self.inbuiltstoreB.reserve_get()
            if isinstance(self.out_edges[1], ConveyorBelt):

                    outstore = self.out_edges[1]
                    put_token = outstore.reserve_put()

                    pe = yield put_token
                    yield get_token
                    item = self.inbuiltstoreB.get(get_token)
                    outstore.put(pe, item)
                    
            else:
                    outstore = self.out_edges[1].inbuiltstore
                    put_token = outstore.reserve_put()
                    yield self.env.all_of([get_token,put_token])
                    item = self.inbuiltstoreB.get(get_token)
                    outstore.put(put_token, item)

            print(f"T={self.env.now:.2f}: {self.name} puts item into {self.out_edges[0].name}  ")
    def worker(self, i):
        """Worker process that sorts and splits items based on a split ratio."""
        while True:
            with self.resource.request() as req:
                yield req  # Wait for work capacity
                
                #storetoget = self.in_edges[0] if isinstance(self.in_edges[0], ConveyorBelt) else self.in_edges[0].out_store
                if isinstance(self.in_edges[0], ConveyorBelt):
                    storetoget = self.in_edges[0]
                    get_token =  storetoget.reserve_get()
                    ge = yield get_token
                    item = yield storetoget.get(ge)
            
                else :
                    storetoget = self.in_edges[0].out_store
                    get_token =  storetoget.reserve_get()
                    yield get_token
                    item = storetoget.get(get_token)
        
                # Create a combined output item and put it in the combiner's store
                if random.random()<self.rule:
                    put_token = self.inbuiltstoreA.reserve_put()
                    print(f"T={self.env.now:.2f}: {self.name } worker{i} is reserving an space in its store")
                    yield put_token
                    print(f"T={self.env.now:.2f}: {self.name } worker{i} is reserved an space in its store")
                    if isinstance(self.in_edges[0], ConveyorBelt):
                        storetoget = self.in_edges[0]
                        get_token =  storetoget.reserve_get()
                        ge = yield get_token
                        item = yield storetoget.get(ge)
                
                    else :
                        storetoget = self.in_edges[0].out_store
                        get_token =  storetoget.reserve_get()
                        yield get_token
                        item = storetoget.get(get_token)
                    print(f"T={self.env.now:.2f}: {self.name }worker {i} received item {item.name}  for splitting")
                    
                    # Simulate processing delay for combining items
                    self.delay_time = next(self.delay) if isinstance(self.delay, Generator) else self.delay
                    yield self.env.timeout(self.delay_time)

                    split_item = Item(name=f"{item.name}_a")
                    self.inbuiltstoreA.put(put_token, split_item)
                else:
                    put_token = self.inbuiltstoreB.reserve_put()
                    print(f"T={self.env.now:.2f}: {self.name } worker{i} is reserving an space in its store")
                    yield put_token
                    print(f"T={self.env.now:.2f}: {self.name } worker{i} is reserved an space in its store")
                    if isinstance(self.in_edges[0], ConveyorBelt):
                        storetoget = self.in_edges[0]
                        get_token =  storetoget.reserve_get()
                        ge = yield get_token
                        item = yield storetoget.get(ge)
                
                    else :
                        storetoget = self.in_edges[0].out_store
                        get_token =  storetoget.reserve_get()
                        yield get_token
                        item = storetoget.get(get_token)
                    print(f"T={self.env.now:.2f}: {self.name } worker {i} received item {item.name}  for splitting")
                    
                    # Simulate processing delay for combining items
                    self.delaytime = next(self.delay)
                    yield self.env.timeout(self.delaytime)

                    split_item = Item(name=f"{item.name}_b")
                    self.inbuiltstoreB.put(put_token, split_item)
                #self.inbuiltstore.put(put_token, split_item)


                print(f"T={self.env.now:.2f}: {self.name} worker {i} placed split item {split_item.name} into store")

    def behaviour(self):
        """Splitter behavior that creates workers based on the effective capacity."""

        assert self.in_edges is not None and len(self.in_edges) == 1, f"Split '{self.name}' must have exactly 1 in_edge."
        assert self.out_edges is not None and len(self.out_edges) == 2, f"Split '{self.name}' must have exactly 2 out_edges."


        cap = min(self.work_capacity, self.store_capacity)
        for i in range(cap):
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay

