from typing import Generator, Optional, Union, Any
import simpy
import random


class Node:
    """
            Base class to represent an active entity in a manufacturing system,
            such as machines, splits, or joints.
        

            Attributes
            ----------
            
                id: str 
                    Identifier for the node.
                node_setup_time : int | float | Generator
                    initial setup time for node as a constant, a generator, or a range (tuple).
                in_edges : list, optional
                    List of input edges connected to the node.
                out_edges : list, optional
                    List of output edges connected to the node.

            Raises
            -------

                TypeError
                    If type of `env` or `id` are incorrect.
                ValueError
                    If node_setup_time inputs are invalid.
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
        elif isinstance(node_setup_time, tuple) and len(node_setup_time) == 2:
            self.node_setup_time = self.random_delay_generator(node_setup_time)
        elif isinstance(node_setup_time, (int, float)):
            self.node_setup_time = node_setup_time
        else:
            raise ValueError(
                "Invalid node_setup_time value. Provide a constant, generator, or a (min, max) tuple."
            )
    

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

    def add_in_edges(self, edge: Any):
        #Override this method in subclasses.
        raise NotImplementedError("add_in_edges must be implemented in a subclass.")

    def add_out_edges(self):
        
        #Override this method in subclasses
        
        raise NotImplementedError("add_out_edges must be implemented in a subclass.")

    def behaviour(self):
        #Override this method in subclasses
        
        raise NotImplementedError("behaviour must be implemented in a subclass.")
