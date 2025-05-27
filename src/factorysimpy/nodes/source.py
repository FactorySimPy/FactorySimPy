# @title Source


from typing import Generator
from factorysimpy.nodes.node import Node
from factorysimpy.helper.item import Item

import random

class Source(Node):
    """
    Source class that inherits from Node.
    It generates items at random intervals and puts it into one of its out edges.
    It can be configured to block until it can put an item into the out edge or to discard items if no space is available in the out edge.

    Attributes
    ----------
        state : str
            The current state of the source
        inter_arrival_time : Union[int, float,generator]
            A generator function that yields random delays or processing times for item generation.
        blocking : bool
            If True, the source will block until it can put an item into the out_edge.
        criterion : str
            The criterion for selecting the edge to put the item into. Options are: random, first, last, round_robin, first_available.
        class_statistics : dict
            A dictionary to store statistics about the source's behavior, including current state, last state change time, items generated, items discarded, and time spent in each state.

    Methods
    -------
    
        behaviour(self):
            Simulates the source behavior, generating items at random intervals and placing them in out edge
    """

    def __init__(self, env, id, in_edges=None , out_edges=None,  inter_arrival_time=0,criterion_to_put="first", blocking=False):
        super().__init__( env, id,in_edges , out_edges,  )
        
        self.state = None
        self.blocking = blocking
        self.criterion = criterion_to_put # Criterion to select the edge to put the item into
        self.state = None
        self.class_statistics = {
            "current_state": None,
            "last_state_change_time": None,
            "item_generated": 0,
            "item_discarded": 0,
            "state_times":{}
        }

    
        if isinstance(inter_arrival_time, Generator):
            self.inter_arrival_time = inter_arrival_time
        elif isinstance(inter_arrival_time, tuple) and len(inter_arrival_time) == 2:
            self.inter_arrival_time = self.random_delay_generator(inter_arrival_time)
        elif inter_arrival_time == 0 and not self.blocking:
            raise ValueError("Non-blocking source must have a non-zero inter_arrival_time.")

        elif isinstance(inter_arrival_time, (int, float)):
            self.inter_arrival_time = inter_arrival_time
        else:
            raise ValueError(
                "Invalid inter_arrival_time value. Provide a constant, generator, or a (min, max) tuple."
            )
        
     # Start behavior process
        self.env.process(self.behaviour())

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
        int | float
            
        A random delay time in the given range.
        """
        while True:
            yield random.randint(*delay_range)
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
        
    def get_edge(self, edge_index: int) -> int:
        """
        Returns the index of the edge to put the item into.
        If there are multiple edges, it selects one based on the creiterion chosen by the user.
        
        Parameters
        ----------
        edge_index : int
            
        The index of the edge to select from the out_edges list.

        Returns
        -------
        int
            
        The index of the selected edge.
        """
        if self.criterion == "random":
            return random.randint(0, edge_index - 1)
        elif self.criterion == "first":
            return 0
        elif self.criterion == "last":
            return edge_index - 1
        elif self.criterion == "round_robin":
            if not hasattr(self, 'round_robin_index'):
                self.round_robin_index = 0
            selected_edge = self.round_robin_index % edge_index
            self.round_robin_index += 1
            return selected_edge
        elif self.criterion == "first_available":
            for i in range(edge_index):
                if self.out_edges[i].can_put():
                    return i
            raise ValueError("No available edges to put the item into.")
    
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
        
        i=0
        self.state = "SETUP_STATE"
        
        while True:
            self.update_state_time(self.state, self.env.now)
            if self.state == "SETUP_STATE":
                print(f"T={self.env.now:.2f}: {self.id} is in SETUP_STATE. Waiting for setup time {self.node_setup_time} seconds")
                yield self.env.timeout(self.node_setup_time)
                
                self.state = "GENERATING_STATE"
                self.update_state_time(self.state, self.env.now)
                print(f"T={self.env.now:.2f}: {self.id} is now {self.state}")
            
            elif self.state== "GENERATING_STATE":
                next_arrival_time = next(self.inter_arrival_time) if isinstance(self.inter_arrival_time, Generator) else self.inter_arrival_time
                yield self.env.timeout(next_arrival_time)
                i+=1
                item = Item(f'item{self.id+":"+str(i)}')
                self.class_statistics["item_generated"] +=1
                edgeindex_to_put = self.get_edge(len(self.out_edges))
                out_edge = self.out_edges[edgeindex_to_put]

                if not self.blocking:
                    if out_edge.can_put():   
                        yield self.env.process(self.push_item(item, out_edge))
                    else:
                        print(f"T={self.env.now:.2f}: {self.id}: Discarding {item.id} as no space in out_edge")
                        self.class_statistics["item_discarded"]+=1
                else:  
                    self.state = "BLOCKED_STATE"
                    self.update_state_time(self.state, self.env.now)
                    yield self.env.process(self.push_item(item, out_edge))
                    self.state = "GENERATING_STATE"
                    self.update_state_time(self.state, self.env.now)

            else:
                raise ValueError(f"Unknown state: {self.state} in Source {self.id}")
                   
    



    
