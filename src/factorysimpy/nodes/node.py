from typing import Generator, Optional, Union, Any
import simpy
import random


class Node:
    """     
    Base class to represent an active entity in a manufacturing system,
    such as machines, splits, or joints.

    Parameters:
        id (str): Identifier for the node.
        node_setup_time (None, int, float, Callable, or Generator, optional): Initial setup time for the node. Can be:
                
            - None: Used when the setup time depends on parameters like current state or time.
            - int or float: Used as a constant delay.
            - Callable: A function that returns a delay (int or float).
            - Generator: A generator function yielding delay values over time.  
        in_edges (list, optional): List of input edges connected to the node. Default is None.
        out_edges (list, optional): List of output edges connected to the node. Default is None.

    Raises:
        TypeError: If the type of `env` or `id` is incorrect.
        ValueError: If `node_setup_time` input is invalid.
    """
    
    def __init__(self,env,id, in_edges: Optional[list] = None, out_edges: Optional[list] = None, node_setup_time: Union[int, float,] = 0,):
   
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

        if isinstance(node_setup_time, Generator):
            self.node_setup_time = node_setup_time
        elif isinstance(node_setup_time, (int, float)):
            self.node_setup_time = node_setup_time
        elif node_setup_time is None:
            self.node_setup_time = None
        else:
            raise ValueError(
                "Invalid node_setup_time value. Provide a None constant ( int or float), generator, or a callable."
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
            return next(delay)
        elif callable(delay):
            # Function
            return delay()
        else:
            # int or float
            return delay
    

    def add_in_edges(self, edge: Any):
        #Override this method in subclasses.
        raise NotImplementedError("add_in_edges must be implemented in a subclass.")

    def add_out_edges(self):
        
        #Override this method in subclasses
        
        raise NotImplementedError("add_out_edges must be implemented in a subclass.")

    def behaviour(self):
        #Override this method in subclasses
        
        raise NotImplementedError("behaviour must be implemented in a subclass.")
