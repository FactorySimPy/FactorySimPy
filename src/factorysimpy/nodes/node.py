import simpy



class Node:
    """     
    Base class to represent an active entity in a manufacturing system,
    such as machines, splits, or joints.

    Parameters:
        id (str): Identifier for the node.
        node_setup_time ( int, or float, optional): Initial setup time for the node. Can be:
        
            - int or float: Used as a constant delay. 
        in_edges (list, optional): List of input edges connected to the node. 
        out_edges (list, optional): List of output edges connected to the node. 

    Raises:
        TypeError: If the type of `env` or `id` is incorrect.
        ValueError: If `node_setup_time` input is invalid.
    """
    
    def __init__(self,env,id, in_edges = None, out_edges = None, node_setup_time= 0):
   
        # Type checks
        if not isinstance(env, simpy.Environment):
            raise TypeError("env must be a simpy.Environment instance")
        if not isinstance(id, str):
            raise TypeError("name must be a string")
        self.env = env
        self.id = id # Identifier for the node.
        self.node_setup_time = node_setup_time # Time taken to set up the node.
        self.in_edges = in_edges # List of input edges connected to the node.
        self.out_edges = out_edges #List of output edges connected to the node.

       
        if isinstance(node_setup_time, (int, float)):
            self.node_setup_time = node_setup_time
        else:
            raise ValueError(
                "Invalid node_setup_time value. Provide constant ( int or float)."
            )
        
       
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

    def add_in_edges(self, edge):
        #Override this method in subclasses.
        raise NotImplementedError("add_in_edges must be implemented in a subclass.")

    def add_out_edges(self):
        
        #Override this method in subclasses
        
        raise NotImplementedError("add_out_edges must be implemented in a subclass.")

    def behaviour(self):
        #Override this method in subclasses
        
        raise NotImplementedError("behaviour must be implemented in a subclass.")
