# @title Source

import simpy

from factorysimpy.nodes.node import Node
from factorysimpy.helper.item import Item
from factorysimpy.helper.pallet import Pallet
from factorysimpy.utils.utils import get_edge_selector



class Source(Node):
    """
    Parameters:
        state (str): Current state of the source node. One of :
                   
            - SETUP_STATE: Initial setup phase before item generation starts.
            - GENERATING_STATE: Actively generating and dispatching items.
            - BLOCKED_STATE: Waiting to transfer item when edge is full (in blocking mode).

        inter_arrival_time (None, int, float, generator, or callable): Time between item generations. Can be:
                
            - None: Used when the setup time depends on parameters of the node object (like current state of the object) or environment. 
            - int or float: Used as a constant delay.
            - Callable: A function that returns a delay (int or float).
            - Generator: A generator function yielding delay values over time.  
        
        flow_item_type (str): Type of item to be generated. Default is "item". Can be 
            
            - "item" : Smallest unit of discrete item and it cannot hold other items inside. 
            - "pallet" : Entities that can store multiple smaller units of items 
    
        blocking (bool): If True, the source waits until it can put an item into the out edge.
        out_edge_selection (None or str or callable): Criterion or function for selecting the out edge.
                                              Options include "RANDOM", "FIRST", "LAST", "ROUND_ROBIN", "FIRST_AVAILABLE".

            - None: Used when out edge selection depends on parameters of the node object (like current state of the object) or environment.    
            - str: A string that specifies the selection method.
                - "RANDOM": Selects a random out edge.
                - "ROUND_ROBIN": Selects out edges in a round-robin manner.
                - "FIRST_AVAILABLE": Selects the first out edge that can accept an item.
            - callable: A function that returns an edge index.

    
    Behavior:
            
    The Source node is responsible for generating items that flow in the simulation model. It operates in two modes: 
    blocking and non-blocking.

    when `blocking=True`:
        - After each `inter_arrival_time`, the source generates an item.
        - If the selected out edge is full, the source waits until space is available.
        - Once space is available, the item is transferred to the selected edge.
        - `inter_arrival_time` must not be `None`.

    when `blocking=False`:
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

    def __init__(self, env, id, in_edges=None, out_edges=None, item_length=1, flow_item_type = "item", inter_arrival_time=0, blocking=False, out_edge_selection="FIRST_AVAILABLE" ):
        super().__init__( env, id,in_edges , out_edges )
        
        self.state = "SETUP_STATE" # Initial state of the source node
        self.blocking = blocking
        self.item_length = item_length
        self.out_edge_selection = out_edge_selection  # Selection strategy for out edges
        self.flow_item_type = flow_item_type # Type of item to be generated, default is "item"
        self.stats = {
            "last_state_change_time": None,
            "num_item_generated": 0,
            "num_item_discarded": 0,
            "total_time_spent_in_states":{"SETUP_STATE": 0.0, "GENERATING_STATE": 0.0, "BLOCKED_STATE": 0.0}
        }
        

        
        
        
        if inter_arrival_time == 0 and not self.blocking:
            raise ValueError("Non-blocking source must have a non-zero inter_arrival_time.")
        elif callable(inter_arrival_time):
            self.inter_arrival_time = inter_arrival_time  
        elif hasattr(inter_arrival_time, '__next__'):
            self.inter_arrival_time = inter_arrival_time    
        elif isinstance(inter_arrival_time, (int, float)):      
            self.inter_arrival_time = inter_arrival_time
        # interarrival_time is None and will be initialized later by the user
        elif inter_arrival_time is None:
            self.inter_arrival_time = inter_arrival_time
        else:
            #print("GGG",inter_arrival_time)
            raise ValueError("inter_arrival_time must be a None, int, float, generator, or callable.")
         # Start behavior process
        self.env.process(self.behaviour())
        
    def reset(self):
        # if self.inter_arrival_time or self.out_edge_selection was initialized to None at the time of object creation 
        # user is expected to set it to valid form before starting the simulation
        
        # Initialize out_edge_selection

        # Initialize out_edge_selection
        #checking if parameter is int and if so it should belong to a valid range
        if isinstance(self.out_edge_selection, int):
            assert 0 <= self.out_edge_selection < len(self.out_edges), f"out_edge_selection must be in range 0 to {len(self.out_edges)-1}"
        #checking if parameter is "FIRST_AVAILABLE". If so it is handled in the class logic.
        elif self.out_edge_selection == "FIRST_AVAILABLE":
            # Special handling in class logic, use as is
            pass
        #checking if out_edge_selection is a string, then it is converted to a generator using get_edge_selector function.
        # Names of the methods are passed as strings. These methods are inbuilt and available.
        elif isinstance(self.out_edge_selection, str):
            self.out_edge_selection = get_edge_selector(self.out_edge_selection, self, self.env, "OUT")
        
        #checking if out_edge_selection is a callable or a generator. If so, it is used as is.
        # it is treated in get_out_edge_index method
        elif callable(self.out_edge_selection) or hasattr(self.out_edge_selection, '__next__'):
            # Use as is (function or generator)
            pass
        else:
            raise ValueError("out_edge_selection must be None, string, int, or a callable (function/generator)")

       

        if self.inter_arrival_time is None:
            raise ValueError("inter_arrival_time should not be None.")
        if self.out_edge_selection is None:
            raise ValueError("out_edge_selection should not be None.")
        
    

    def _get_out_edge_index(self):
        
            
   
        if isinstance(self.out_edge_selection, int):
            return self.out_edge_selection
        elif hasattr(self.out_edge_selection, '__next__'):
            # It's a generator
            val = next(self.out_edge_selection)
            return val
           
        elif callable(self.out_edge_selection):
            # It's a function (pass self and env if needed)
            #return self.out_edge_selection(self, self.env)
            val = self.out_edge_selection()
            
            return val
        
        else:
            raise ValueError("out_edge_selection must be a generator or a callable.")    
                
 

    

    
   

    def _push_item(self, item_to_push, out_edge):
        """
        It picks a processed item from the store and pushes it to the specified out_edge.
        The out_edge can be a ConveyorBelt or Buffer.
        Args:
            item_to_push (BaseFlowItem Object): Item to be pushed.
            out_edge (Edge Object): The edge to which the item will be pushed.


        """
       
        if out_edge.__class__.__name__ == "ConveyorBelt":                 
                put_token = out_edge.reserve_put()
                pe = yield put_token
                item_to_push.update_node_event(self.id, self.env, "exit")
                
                y=out_edge.put(pe, item_to_push)
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts {item_to_push.id} item into {out_edge.id}  ")
        elif out_edge.__class__.__name__ in ["Buffer", "Fleet"]:
                outstore = out_edge
                put_token = outstore.reserve_put()
                yield put_token
                item_to_push.update_node_event(self.id, self.env, "exit")
                y=outstore.put(put_token, item_to_push)
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts item into {out_edge.id}")
        else:
                raise ValueError(f"Unsupported edge type: {out_edge.__class__.__name__}")


    
        
 
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
        if out_edge.__class__.__name__ == "ConveyorBelt1":

                            
                put_token = out_edge.reserve_put()

                yield put_token
                item.set_creation(self.id, self.env)
                item.timestamp_node_exit = self.env.now
                y=out_edge.put(put_token, item)
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts {item.id} item into {out_edge.id}  ")
                
        elif out_edge.__class__.__name__ in ["Buffer", "Fleet", "ConveyorBelt"]:
                outstore = out_edge
                put_token = outstore.reserve_put()
                yield put_token
                item.set_creation(self.id, self.env)
                            
                item.timestamp_node_exit = self.env.now
                y=outstore.put(put_token, item)
                if y:
                    print(f"T={self.env.now:.2f}: {self.id} puts item into {out_edge.id} ")
        else:
                raise ValueError(f"Unsupported edge type: {out_edge.__class__.__name__}")

    def update_state(self, new_state: str, current_time: float):
        """
        Update node state and track the time spent in the previous state.
        
        Args:
            i (int): The index of the worker thread to update the state for.
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

    def update_final_state_time(self, simulation_end_time):
        duration = simulation_end_time- self.stats["last_state_change_time"]
        
        #checking threadstates and updating the machine state
        if self.state is not None and self.stats["last_state_change_time"] is not None:
            duration = simulation_end_time- self.stats["last_state_change_time"]
            self.stats["total_time_spent_in_states"][self.state] = (
                self.stats["total_time_spent_in_states"].get(self.state, 0.0) + duration
            )
        
    
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
                
                yield self.env.timeout(self.node_setup_time)
                
                self.update_state("GENERATING_STATE", self.env.now)
     
                
                print(f"T={self.env.now:.2f}: {self.id} is now {self.state}")
            
            elif self.state== "GENERATING_STATE":
                next_arrival_time = self.get_delay(self.inter_arrival_time)
                if not isinstance(next_arrival_time, (int, float)):
                    raise AssertionError("inter_arrival_time returns an invalid value. It should be int or float")
                yield self.env.timeout(next_arrival_time)
                i+=1
                if self.flow_item_type == "item":
                    item = Item(f'item_{self.id+"_"+str(i)}')
                    item.length = self.item_length
                else:
                    item = Pallet(f'pallet_{self.id+"_"+str(i)}')
                    item.length = self.item_length
                #item.set_creation(self.id, self.env)
                self.stats["num_item_generated"] +=1
                #edgeindex_to_put = next(self.out_edge_selection)



                if self.out_edge_selection == "FIRST_AVAILABLE":

                    if self.blocking:
                        self.update_state("BLOCKED_STATE", self.env.now)
                        #print(self.env.now,"GEttingbloccccccked")
                        blocking_start_time = self.env.now
                    
                        #self.out_edge_events = [edge.reserve_put() if edge.__class__.__name__ == "ConveyorBelt" else edge.inbuiltstore.reserve_put() for edge in self.out_edges]
                        self.out_edge_events = [edge.reserve_put() for edge in self.out_edges]
                        triggered_out_edge_events = self.env.any_of(self.out_edge_events)
                        yield triggered_out_edge_events  # Wait for any in_edge to be available
                        

                        # Find the first triggered event
                        chosen_put_event = next((event for event in self.out_edge_events if event.triggered), None)
                        edge_index = self.out_edge_events.index(chosen_put_event)  # Get the index of the chosen event
                        self.out_edge_events.remove(chosen_put_event)  # Remove the chosen event from the list
                        if chosen_put_event is None:
                            raise ValueError(f"{self.id} - No in_edge available for processing!")
                        
                        #cancelling already triggered out_edge events
                        for event in self.out_edge_events:
                            
                            event.resourcename.reserve_put_cancel(event)
                        #print(f"T={self.env.now:.2f}: {self.id} yielded 11111111from {self.out_edges[edge_index].id} ")
                        #putting the item in the chosen out_edge
                        item.set_creation(self.id, self.env)
                        item.timestamp_node_exit = self.env.now
                        #print(chosen_put_event.requesting_process, self)
                        itemput=self.out_edges[edge_index].put(chosen_put_event, item)
                        #itemput = chosen_put_event.resourcename.put(chosen_put_event, item)  # put the item to the chosen out_edge
                        #print(f"T={self.env.now:.2f}: {self.id} placed 222222 from {self.out_edges[edge_index].id} ")
                        #print(f"T={self.env.now:.2f}: {self.id} puts item {item.id} into {chosen_put_event.resourcename} {item.timestamp_creation} ")
                
                        if isinstance(itemput, simpy.events.Process):
                            
                            yield itemput # Wait for the item to be available
                            #print("yaay")
                        else:
                            item1 = itemput
                            print(f"T={self.env.now:.2f}: {self.id} {item.id} pushed to buffer {self.out_edges[edge_index].id} ")
                        
                        #print(f"T={self.env.now:.2f}: {self.id} BLOCKED to generated after {self.env.now - blocking_start_time:.2f} seconds")
                        self.update_state("GENERATING_STATE", self.env.now)  # Update state back to GENERATING_STATE
                        #print(self.env.now,"releases")
                       

                    else:
                        out_edge_index_to_put = None
                        for edge in self.out_edges:
                            if edge.can_put():
                                out_edge_to_put = edge
                                break
                        
                        if out_edge_to_put is not None:
                            blocking_start_time = self.env.now
                            self.update_state("BLOCKED_STATE", self.env.now)
                            
                            yield self.env.process(self._push_item(item, out_edge_to_put))  
                            #print(f"T={self.env.now:.2f}: {self.id} BLOCKED to generated after {self.env.now - blocking_start_time:.2f} seconds")
                            self.update_state("GENERATING_STATE", self.env.now)  # Update state back to GENERATING_STATE

                            
                        else:               
                            print(f"T={ self.env.now:.2f}: {self.id} is discarding item {item.id} because out_edge {edge.id} is full.")
                            self.stats["num_item_discarded"] += 1  # Decrement processed count if item is discarded


                        
                        
                    


                else:
                    print(f"T={self.env.now:.2f}: {self.id} generated item: {item.id}")
                    out_edge_index_to_put = self._get_out_edge_index()
                    if out_edge_index_to_put is None:
                        raise ValueError(f"{self.id} - No out_edge available for processing!")
                    if out_edge_index_to_put < 0 or out_edge_index_to_put >= len(self.out_edges):
                        raise IndexError(f"{self.id}  - Invalid edge index {out_edge_index_to_put} for out_edges.")
                    outedge_to_put = self.out_edges[out_edge_index_to_put]

                    if self.blocking:
                        blocking_start_time = self.env.now
                        print(f"T={self.env.now:.2f}: {self.id} is in BLOCKED_STATE")
                        self.update_state("BLOCKED_STATE", self.env.now)
                        
                        yield self.env.process(self._push_item(item, outedge_to_put))
                        #print(f"T={self.env.now:.2f}: {self.id} BLOCKED to generated after {self.env.now - blocking_start_time:.2f} seconds")
                        self.update_state("GENERATING_STATE", self.env.now)  # Update state back to GENERATING_STATE
                        
                    else:
                        # Check if the out_edge can accept the item
                        if outedge_to_put.can_put():
                            blocking_start_time = self.env.now
                            
                            yield self.env.process(self._push_item(item, outedge_to_put))
                            
                        else:
                            print(f"T={self.env.now:.2f}: {self.id} is discarding item {item.id} because out_edge {outedge_to_put.id} is full.")
                            self.stats["num_item_discarded"] += 1
               
                    
                



                
                
               
                 

            else:
                raise ValueError(f"Unknown state: {self.state} in Source {self.id}")
                   
    



    
