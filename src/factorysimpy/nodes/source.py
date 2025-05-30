# @title Source


from typing import Generator
from factorysimpy.nodes.node import Node
from factorysimpy.helper.item import Item
from factorysimpy.utils.utils import get_index_selector

import random

class Source(Node):
    """
     Attributes
    ----------
        state : str
            Current state of the source node. It can take one of {"SETUP_STATE", "GENERATING_STATE", "BLOCKED_STATE"}.
        inter_arrival_time : int, float, generator, or callable
            Time between item generations. Can be a constant, a generator, or a function returning the delay.
        blocking : bool
            If True, the source blocks until it can put an item into the out edge.
        out_edge_selection : str or callable
            Criterion or function for selecting the out edge. Options include "RANDOM", "FIRST", "LAST", "ROUND_ROBIN", "FIRST_AVAILABLE".
    
    Methods
    -------
    
        behaviour(self):
            Simulates the source behavior, generating items at random intervals and placing them in out edge
    """

    def __init__(self, env, id, in_edges=None , out_edges=None,  inter_arrival_time=0,blocking=False, out_edge_selection="FIRST" ):
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
            
            self.out_edge_selection = get_index_selector(out_edge_selection, self, env)

            
        elif callable(out_edge_selection):
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
        else:
            self.inter_arrival_time = inter_arrival_time
         # Start behavior process
        self.env.process(self.behaviour())
        
    def reset(self):
        if self.inter_arrival_time is None:
            raise ValueError("inter_arrival_time must be set before resetting the source.")

    def get_edge_index(self):
        """
        Returns the next edge index from out_edge_selection, whether it's a generator or a callable.
        """
        
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
        if self.out_edges is None:
            self.out_edges = []

        if len(self.out_edges) >= 1:
            raise ValueError(f"Source '{self.id}' already has 1 out_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Source '{self.id}' out_edges.")
        
   
    
    def push_item(self, item, out_edge):
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
        """
        Simulates the source behavior, generating items at random intervals and placing them in out_edge.
        if blocking is True, it will block until it can put an item into the out_edge.
        If blocking is False, it will discard the item if no space is available in the out_edge.
        
        """
        assert self.in_edges is  None , f"Source '{self.id}' must not have an in_edge."
        assert self.out_edges is not None and len(self.out_edges) >= 1, f"Source '{self.id}' must have atleast 1 out_edge."
        self.reset()
        i=0
        
        
        while True:
            self.update_state(self.state, self.env.now)
            if self.state == "SETUP_STATE":
                print(f"T={self.env.now:.2f}: {self.id} is in SETUP_STATE. Waiting for setup time {self.node_setup_time} seconds")
                node_setup_delay = self.get_delay(self.node_setup_time)
                yield self.env.timeout(node_setup_delay)
                
                self.update_state("GENERATING_STATE", self.env.now)
     
                
                print(f"T={self.env.now:.2f}: {self.id} is now {self.state}")
            
            elif self.state== "GENERATING_STATE":
                next_arrival_time = self.get_delay(self.inter_arrival_time)
                yield self.env.timeout(next_arrival_time)
                i+=1
                item = Item(f'item{self.id+":"+str(i)}')
                self.stats["num_item_generated"] +=1
                #edgeindex_to_put = next(self.out_edge_selection)
                edgeindex_to_put = self.get_edge_index()
                out_edge = self.out_edges[edgeindex_to_put]

                if not self.blocking:
                    if out_edge.can_put():   
                        yield self.env.process(self.push_item(item, out_edge))
                    else:
                        print(f"T={self.env.now:.2f}: {self.id}: Discarding {item.id} as no space in out_edge")
                        self.stats["num_item_discarded"]+=1
                else:  
                    self.update_state("BLOCKED_STATE", self.env.now)
               
                    
                    yield self.env.process(self.push_item(item, out_edge))
                    self.update_state("GENERATING_STATE", self.env.now)
                    
                 

            else:
                raise ValueError(f"Unknown state: {self.state} in Source {self.id}")
                   
    



    
