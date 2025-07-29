# @title Edge


import simpy
from factorysimpy.nodes.node import Node


class Edge:
    """
    Edge represents the passive components. It used to connect two nodes and helps to move items between them.
    It is the base class used to model buffers, conveyors, fleets, etc in manufacturing system.

    Parameters:
        id (str): unique identifier for the edge
        src_node (Node): reference to the source node connected to this edge.
        dest_node (Node): reference to the destination node connected to this edge.
       

    Raises:
        TypeError: If the type of `env` or `id` is incorrect.
        ValueError: If the `delay` parameter is not a valid type (int, float, generator, or callable).
        ValueError: If the edge is already connected to a source or destination node and reconnect is False.
        ValueError: If the source or destination nodes are not valid Node instances.
       
        

    
    """
    


    def __init__(self, env, id, capacity):
        self.env = env
        self.id = id
        self.src_node = None
        self.dest_node = None
        self.capacity = capacity
        
         # Type checks
        if not isinstance(env, simpy.Environment):
            raise TypeError("env must be a simpy.Environment instance")
        if not isinstance(id, str):
            raise TypeError("id must be a string")
        if not isinstance(self.capacity, int) or self.capacity <= 0:
            raise ValueError("capacity must be a positive integer")
        
        assert self.src_node is None, f"Edge '{self.id}' must have a source node."
        assert self.dest_node is None, f"Edge '{self.id}' must have a destination node."
        assert self.id is not None, "Edge id cannot be None."
        assert self.capacity is not None, "Edge capacity cannot be None."
        


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

   
    def get_delay(self,delay):
        """
        Returns value based on the type of parameter `delay` provided.

        Args:
             delay (int, float, generator, or callable): The delay time, which can be:
             
                - int or float: Used as a constant delay.
                - generator: A generator instance yielding delay values.
                - callable: A function that returns a delay values.

        Returns:
               Returns a constant delay if `delay` is an int or float, a value yielded  if `delay` is a generator, or the value returned from a Callable function if `delay` is callable.
        """
        if hasattr(delay, '__next__'):
            # Generator instance
            val = next(delay)
        elif callable(delay):
            # Function
            val = delay()
        else:
            # int or float
            val = delay

        assert val >= 0, "Delay must be non-negative"
        return val


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

    def connect(self, src: Node, dest: Node, reconnect: bool = False):
        """
        Connects this edge to a source node and a destination node.

        This method checks that both `src` and `dest` are valid Node objects and that the edge is not already connected,
        unless `reconnect` is set to True. It also registers this edge in the `out_edges` of the source node and the
        `in_edges` of the destination node.

        Args:
            src (Node): The source node to connect.
            dest (Node): The destination node to connect.
            reconnect (bool, optional): If True, allows reconnection even if the edge is already connected. Defaults to False.

        Raises:
            ValueError: If the edge is already connected and `reconnect` is False.
            ValueError: If `src` or `dest` is not a valid Node instance.
        """
        
        if not reconnect:
            if self.src_node or self.dest_node:
                raise ValueError(f"Edge '{self.id}' is already connected source or destination node.")
            if not isinstance(src, Node):
                raise ValueError(f"Source '{src}' is not a valid Node.")
            if not isinstance(dest, Node):
                raise ValueError(f"Destination '{dest}' is not a valid Node.")

        self.src_node = src
        self.dest_node = dest

        # Register edge to nodes
        if src.out_edges is None:
            src.out_edges = []
        if self not in src.out_edges:
            src.out_edges.append(self)

        if dest.in_edges is None:
            dest.in_edges = []
        if self not in dest.in_edges:
            dest.in_edges.append(self)
        print(f"T={self.env.now:.2f}: Connected edge '{self.id}' from '{src.id}' to '{dest.id}'  ")

        
    
    def get_occupancy(self):
        #Override this method in subclasses
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def get_ready_items(self):
        
        #Override this method in subclasses
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def can_put(self):

        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def can_get(self):
        #Override this method in subclasses
        raise NotImplementedError("This method should be implemented in subclasses.")
    
