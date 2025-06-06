# Machine m input and 1 output without using cancel

from factorysimpy.nodes.node import Node
from factorysimpy.utils.utils import get_index_selector
from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore  # Import your class


class Machine(Node):
    """
        Machine represents a processing node in a factory simulation.
        This Machine can have multiple input edges and  output edges.

        Parameters:
            state (str): Current state of the source node. One of :
                   
                - SETUP_STATE: Initial setup phase before machine starts to operate.
                - IDLE_STATE: Waiting to receive an item and there is space avilable in the inbuiltstore
                - PROCESSING_STATE: Actively processing items.
                - BLOCKED_STATE: when the inbuiltstore is full and it is unable to get objects for processing.
           
            store_capacity (int): Maximum capacity of the internal storage.
            work_capacity (int): Maximum number of items that can be processed simultaneously.
            processing_delay (None, int, float, Generator, Callable): Delay for processing items. Can be:
                
                - None: Used when the processing time depends on parameters of the node object (like current state of the object) or environment. 
                - int or float: Used as a constant delay.
                - Generator: A generator function yielding delay values over time.
                - Callable: A function that returns a delay (int or float).
            in_edge_selection (None or str or callable): Criterion or function for selecting the edge.
                                              Options include "RANDOM", "FIRST", "LAST", "ROUND_ROBIN", "FIRST_AVAILABLE".

                - None: None: Used when edge selction depends on parameters of the node object (like current state of the object) or environment. 
                - str: A string that specifies the selection method.
                    - "RANDOM": Selects a random edge.
                    - "FIRST": Selects the first edge in the in_edges list.
                    - "LAST": Selects the last edge in the in_edges list .
                    - "ROUND_ROBIN": Selects edges in a round-robin manner.
                    - "FIRST_AVAILABLE": Selects the first out edge that can give an item.
                - callable: A function that returns an edge index.
            out_edge_selection (None or str or callable): Criterion or function for selecting the out edge.
                                              Options include "RANDOM", "FIRST", "LAST", "ROUND_ROBIN", "FIRST_AVAILABLE".

                - None: None: Used when out edge selction depends on parameters of the node object (like current state of the object) or environment.   
                - str: A string that specifies the selection method.
                    - "RANDOM": Selects a random out edge in the out_edges list.
                    - "FIRST": Selects the first out edge in the out_edges list.
                    - "LAST": Selects the last out edge in the out_edges list.
                    - "ROUND_ROBIN": Selects out edges in a round-robin manner.
                    - "FIRST_AVAILABLE": Selects the first out edge that can accept an item.
                - callable: A function that returns an edge index.
                

        Behavior:
            The machine node represents components that process or modify the items that flow in the simulation model. It can have multiple incoming edges
            and multiple outgoing edge. Edge from whcih the item comes in and the edge to which processes item is pushed is decided using the method specified
            in the parameter `in_edge_selection` and `out_edge_selection`. Machine will transition through the states- `SETUP_STATE`, `PROCESSING_STATE`, `IDLE_STATE` AND 
            `BLOCKED_STATE`. The machine has a blocking behavior and gets blocked when it has `store_capacity` number of items in its store and the out edge is full and 
            cannot accept the item that is being pushed by the machine

        Raises:
            AssertionError: If the Machine has no input or output edges.
        Output performance metrics:
        The key performance metrics of the Machine node is captured in `stats` attribute (dict) during a simulation run. 
            
            last_state_change_time    : Time when the state was last changed.
            num_item_processed        : Total number of items generated.
            total_time_spent_in_states: Dictionary with total time spent in each state.
                
    """

    def __init__(self, env, id, in_edges=None, out_edges=None,node_setup_time=0, work_capacity=1,processing_delay=0,blocking=False,in_edge_selection="FIRST",out_edge_selection="FIRST"):
        super().__init__(env, id,in_edges, out_edges, node_setup_time)
        
        self.state = {} 
        self.work_capacity = work_capacity
        self.blocking = blocking
        self.item_in_process={}
        self.stats={}
       
     
        

        

        # Initialize processing delay 
        if callable(processing_delay):
            self.processing_delay = processing_delay 
        elif hasattr(processing_delay, '__next__'):
            # It's a generator
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
            self.in_edge_selection = get_index_selector(in_edge_selection, self, env, "IN")
        elif callable(in_edge_selection):
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.in_edge_selection = in_edge_selection
        elif in_edge_selection is None:
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.in_edge_selection = in_edge_selection
        else:
            raise ValueError("in_edge_selection must be a None, string or a callable (function/generator)")
        
        
        if isinstance(out_edge_selection, str):  
            self.out_edge_selection = get_index_selector(out_edge_selection, self, env, "OUT")
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
        

    
        
 
    def update_state(self,i, new_state: str, current_time: float):
        """
        Update node state and track the time spent in the previous state.
        
        Args:
            new_state (str): The new state to transition to. Must be one of "SETUP_STATE", "GENERATING_STATE", "BLOCKED_STATE".
            current_time (float): The current simulation time.

        """
        
        if self.state[i] is not None and self.stats[i]["last_state_change_time"] is not None:
            elapsed = current_time - self.stats[i]["last_state_change_time"]

            self.stats[i]["total_time_spent_in_states"][self.state[i]] = (
                self.stats[i]["total_time_spent_in_states"].get(self.state[i], 0.0) + elapsed
            )
        self.state[i] = new_state
        self.stats[i]["last_state_change_time"] = current_time

        
    


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
    
   

    def _push_item(self, i, out_edge):
        """
        It picks a processed item from the store and pushes it to the specified out_edge.
        The out_edge can be a ConveyorBelt or Buffer.
        Args:
            i (int): Index of the worker processing the item.
            out_edge (Edge Object): The edge to which the item will be pushed.


        """
       
        if out_edge.__class__.__name__ == "ConveyorBelt":                 
                put_token = out_edge.reserve_put()
                pe = yield put_token
                self.item_in_process[i].update_node_event(self.id, self.env, "exit")
                
                y=out_edge.put(pe, self.item_in_process[i])
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts {self.item_in_process[i].id} item into {out_edge.id}  ")
        elif out_edge.__class__.__name__ == "Buffer":
                outstore = out_edge.inbuiltstore
                put_token = outstore.reserve_put()
                yield put_token
                self.item_in_process[i].update_node_event(self.id, self.env, "exit")
                y=outstore.put(put_token, self.item_in_process[i])
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts item into {out_edge.id}")
        else:
                raise ValueError(f"Unsupported edge type: {out_edge.__class__.__name__}")
        
    def _pull_item(self,i, in_edge):
        """
        It pulls an item from the specified in_edge and assigns it to the worker for processing.
        Args:
            i (int): Index of the worker that will process the item.
            in_edge (Edge Object): The edge from which the item will be pulled.

        """
        if in_edge.__class__.__name__ == "ConveyorBelt":
                get_token = in_edge.reserve_get()
                gtoken = yield get_token
                self.item_in_process[i]=yield in_edge.get(gtoken)
                self.item_in_process[i].update_node_event(self.id, self.env, "entry")
              
                if self.item_in_process[i]:
                    print(f"T={self.env.now:.2f}: {self.id} gets item {self.item_in_process[i].id} from {in_edge.id}  ")
                
        elif in_edge.__class__.__name__ == "Buffer":
                outstore = in_edge.inbuiltstore
                get_token = outstore.reserve_get()
                yield get_token
                self.item_in_process[i] =outstore.get(get_token)
                self.item_in_process[i].update_node_event(self.id, self.env, "entry")
                if self.item_in_process[i]:
                    print(f"T={self.env.now:.2f}: {self.id} gets item {self.item_in_process[i].id} from {in_edge.id} ")
        else:
                raise ValueError(f"Unsupported edge type: {in_edge.__class__.__name__}")



    def worker(self, i):
        #Worker process that processes items with resource and reserve handling."""
        self.reset()
        while True:
            #print(f"T={self.env.now:.2f}: {self.id} worker{i} started processing")
            if self.state[i] == "SETUP_STATE":
                
                print(f"T={self.env.now:.2f}: {self.id} worker{i} is in SETUP_STATE")
                yield self.env.timeout(self.node_setup_time)# always an int or float
                self.update_state(i,"IDLE_STATE", self.env.now)
            
            elif self.state[i] == "IDLE_STATE":
                print(f"T={self.env.now:.2f}: {self.id} worker{i} is in IDLE_STATE")
        
                # Wait for the next item to process
                edgeindex_to_get = self._get_in_edge_index()
                in_edge = self.in_edges[edgeindex_to_get]
                yield self.env.process(self._pull_item(i,in_edge))
                
                self.update_state(i,"PROCESSING_STATE", self.env.now)

            elif self.state[i] == "PROCESSING_STATE":
                 if self.item_in_process[i] is None:
                   raise RuntimeError(f"{self.id} worker{i} - No item to process!")
                 next_processing_time = self.get_delay(self.processing_delay)
                 if not isinstance(next_processing_time, (int, float)):
                        raise AssertionError("processing_delay returns an valid value. It should be int or float")
                 yield self.env.timeout(next_processing_time)
                 self.stats[i]["num_item_processed"] += 1
                 print(f"T={self.env.now:.2f}: {self.id} worker{i} processed item: {self.item_in_process[i].id}")
                 out_edge_index_to_put = self._get_out_edge_index()
                 outedge_to_put = self.out_edges[out_edge_index_to_put]
                 self.update_state(i,"BLOCKED_STATE", self.env.now)
                 # Check if the out_edge can accept the item
                 if self.blocking :
                    yield self.env.process(self._push_item(self.item_in_process[i], outedge_to_put))
                 else:
                    # Check if the out_edge can accept the item
                    if outedge_to_put.can_put():
                        yield self.env.process(self._push_item(i, outedge_to_put))
                    else:
                        print(f"T={self.env.now:.2f}: {self.id} worker{i} is discarding item {self.item_in_process[i].id} because out_edge {outedge_to_put.id} is full.")
                        self.stats[i]["num_item_discarded"] += 1  # Decrement processed count if item is discarded
                        self.item_in_process[i].set_destruction(self.id, self.env)
                        self.item_in_process[i] = None  # Clear the processed item
                 self.update_state(i,"IDLE_STATE", self.env.now)
                 self.item_in_process[i] = None  # Clear the processed item
                 # process items and put in inbuiltstore. 
                 # Pull_items will take the items and push it to next component.
                 
                 
            else:
                raise ValueError(f"Invalid state: {self.state[i]} for worker {i} in Machine {self.id}")    
            
          
                
                

    def behaviour(self):
        #Machine behavior that creates workers based on the effective capacity."""
        
        
        assert self.in_edges is not None and len(self.in_edges) >= 1, f"Machine '{self.id}' must have atleast 1 in_edge."
        assert self.out_edges is not None and len(self.out_edges) >= 1, f"Machine '{self.id}' must have atleast 1 out_edge."
        
        for i in range(self.work_capacity):
            print(f"T={self.env.now:.2f}: {self.id} creating worker {i+1}")
            self.state[i+1] = "SETUP_STATE" # Initialize state for each worker
            self.item_in_process[i+1] = None  # Initialize item to process for each worker
            
            # Initialize stats for each worker
            self.stats[i+1] = {
                        "last_state_change_time": None,
                        "num_item_processed": 0,
                        "num_item_discarded": 0,
                        "total_time_spent_in_states":{"SETUP_STATE": 0.0,"IDLE_STATE": 0.0, "PROCESSING_STATE": 0.0, "BLOCKED_STATE": 0.0}
                    }
            #starting worker process
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay

