# @title Source



from factorysimpy.nodes.node import Node
from factorysimpy.helper.item import Item
from factorysimpy.utils.utils import get_index_selector



class Source(Node):
    """
    Parameters:
        state (str): Current state of the source node. One of :
                   
            - SETUP_STATE: Initial setup phase before item generation starts.
            - GENERATING_STATE: Actively generating and dispatching items.
            - BLOCKED_STATE: Waiting to transfer item when edge is full (in blocking mode).

        inter_arrival_time (None, int, float, generator, or callable): Time between item generations. Can be:
                
            - None: Used when the setup time depends on parameters like the current state of the object or time.
            - int or float: Used as a constant delay.
            - Callable: A function that returns a delay (int or float).
            - Generator: A generator function yielding delay values over time.  
    
        blocking (bool): If True, the source waits until it can put an item into the out edge.
        out_edge_selection (None or str or callable): Criterion or function for selecting the out edge.
                                              Options include "RANDOM", "FIRST", "LAST", "ROUND_ROBIN", "FIRST_AVAILABLE".

            - None: Used when out edge selction depends on parameters like current state of the object or time.   
            - str: A string that specifies the selection method.
                - "RANDOM": Selects a random out edge.
                - "FIRST": Selects the first out edge.
                - "LAST": Selects the last out edge.
                - "ROUND_ROBIN": Selects out edges in a round-robin manner.
                - "FIRST_AVAILABLE": Selects the first out edge that can accept an item.
            - callable: A function that returns an edge index.

    
    Behavior:
            
    The Source node is responsible for generating items that flow in the simulation model. It operates in two modes: 
    blocking and non-blocking.

    Blocking Mode (`blocking=True`):
        - After each `inter_arrival_time`, the source generates an item.
        - If the selected out edge is full, the source waits until space is available.
        - Once space is available, the item is transferred to the selected edge.
        - `inter_arrival_time` must not be `None`.

    Non-blocking Mode (`blocking=False`):
        - After each `inter_arrival_time`, the source generates an item.
        - If the selected out edge is full, the item is discarded immediately.
        - If space is available, the item is transferred without waiting.
        - `inter_arrival_time` must not be 0.

   
        
    Raises:
        ValueError: If `inter_arrival_time` is 0 in non-blocking mode or if `out_edge_selection` is not a valid type.
        ValueError: If `out_edge_selection` is not a string or callable.
        ValueError: If `out_edges` is not provided or has less than one edge.
        ValueError: If `in_edges` is provided, as Source nodes should not have input edges.
        ValueError: If `out_edges` already has an edge when trying to add a new one.
   


    Output performance metrics:
    The key performance metrics of the Source node is captured in `stats` attribute (dict) during a simulation run. 
        
        last_state_change_time    : Time when the state was last changed.
        num_item_generated        : Total number of items generated.
        num_item_discarded        : Total number of items discarded due to lack of space in out edge.
        total_time_spent_in_states: Dictionary with total time spent in each state.
       
      

    """

    def __init__(self, env, id, in_edges=None, out_edges=None, inter_arrival_time=0, blocking=False, out_edge_selection="FIRST" ):
        super().__init__( env, id,in_edges , out_edges )
        
        self.state = "SETUP_STATE" # Initial state of the source node
        self.blocking = blocking
        self.stats = {
            "last_state_change_time": None,
            "num_item_generated": 0,
            "num_item_discarded": 0,
            "total_time_spent_in_states":{"SETUP_STATE": 0.0, "GENERATING_STATE": 0.0, "BLOCKED_STATE": 0.0}
        }

        if isinstance(out_edge_selection, str):  
            self.out_edge_selection = get_index_selector(out_edge_selection, self, env, edge_type="OUT")
        elif callable(out_edge_selection):
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.out_edge_selection = out_edge_selection
        elif out_edge_selection is None:
            # Optionally, you can check if it's a generator function by calling and checking for __iter__ or __next__
            self.out_edge_selection = out_edge_selection
        else:
            raise ValueError("out_edge_selection must be a string or a callable (function/generator)")
        
        
        
        if inter_arrival_time == 0 and not self.blocking:
            raise ValueError("Non-blocking source must have a non-zero inter_arrival_time.")
        elif callable(inter_arrival_time):
            self.inter_arrival_time = inter_arrival_time      
        elif isinstance(inter_arrival_time, (int, float)):      
            self.inter_arrival_time = inter_arrival_time
        # interarrival_time is None and will be initialized later by the user
        elif inter_arrival_time is None:
            self.inter_arrival_time = inter_arrival_time
        else:
            raise ValueError("inter_arrival_time must be a None, int, float, generator, or callable.")
         # Start behavior process
        self.env.process(self.behaviour())
        
    def reset(self):
        # if self.inter_arrival_time or self.out_edge_selection was initialized to None at the time of object creation 
        # user is expected to set it to valid form before starting the simulation
        
        if self.inter_arrival_time is None:
            raise ValueError("inter_arrival_time should not be None.")
        if self.out_edge_selection is None:
            raise ValueError("out_edge_selection should not be None.")

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
        raise ValueError("Source does not have in_edges. Cannot add any.")

    def add_out_edges(self, edge):
        """
        Adds an out_edge to the source node. Raises an error if the source already has an 
        out_edge or if the edge already exists in the out_edges list.
        
        Args:
            edge (Edge Object): The edge to be added as an out_edge.
        """
        if self.out_edges is None:
            self.out_edges = []

        if len(self.out_edges) >= 1:
            raise ValueError(f"Source '{self.id}' already has 1 out_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Source '{self.id}' out_edges.")
        
   
    
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


    
    def behaviour(self):
        
        #Simulates the source behavior, generating items at random intervals and placing them in out_edge.
        #if blocking is True, it will block until it can put an item into the out_edge.
        #If blocking is False, it will discard the item if no space is available in the out_edge.
        
        
        assert self.in_edges is  None , f"Source '{self.id}' must not have an in_edge."
        assert self.out_edges is not None and len(self.out_edges) >= 1, f"Source '{self.id}' must have atleast 1 out_edge."
        self.reset()
        i=0
        
        
        while True:
            self.update_state(self.state, self.env.now)
            if self.state == "SETUP_STATE":
                print(f"T={self.env.now:.2f}: {self.id} is in SETUP_STATE. Waiting for setup time {self.node_setup_time} seconds")
                node_setup_delay = self.get_delay(self.node_setup_time)
                if not isinstance(node_setup_delay, (int, float)):
                    raise AssertionError("node_setup_time returns an valid value. It should be int or float")
                yield self.env.timeout(node_setup_delay)
                
                self.update_state("GENERATING_STATE", self.env.now)
     
                
                print(f"T={self.env.now:.2f}: {self.id} is now {self.state}")
            
            elif self.state== "GENERATING_STATE":
                next_arrival_time = self.get_delay(self.inter_arrival_time)
                if not isinstance(next_arrival_time, (int, float)):
                    raise AssertionError("inter_arrival_time returns an invalid value. It should be int or float")
                yield self.env.timeout(next_arrival_time)
                i+=1
                item = Item(f'item{self.id+":"+str(i)}')
                self.stats["num_item_generated"] +=1
                #edgeindex_to_put = next(self.out_edge_selection)
                edgeindex_to_put = self._get_out_edge_index()
                out_edge = self.out_edges[edgeindex_to_put]

                if not self.blocking:
                    if out_edge.can_put():   
                        yield self.env.process(self._push_item(item, out_edge))
                    else:
                        print(f"T={self.env.now:.2f}: {self.id}: Discarding {item.id} as no space in out_edge")
                        self.stats["num_item_discarded"]+=1
                else:  
                    self.update_state("BLOCKED_STATE", self.env.now)
               
                    
                    yield self.env.process(self._push_item(item, out_edge))
                    self.update_state("GENERATING_STATE", self.env.now)
                    
                 

            else:
                raise ValueError(f"Unknown state: {self.state} in Source {self.id}")
                   
    



    
