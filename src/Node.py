# @title Node
import simpy
import random
import logging

# Setup logger (optional, based on your environment)



class Node:
    """
    A class to represent a node in a production line or process flow.

    Attributes
    ----------
    env : simpy.Environment
        The simulation environment.
    name : str
        The name of the node (station).
    id : any
        An identifier for the node.
    work_capacity : int
        The capacity of the resource at this node for active processing.
    store_capacity : int
        The capacity for storing items in the node's internal storage.
    delay : generator function or int
        A generator for random delays or processing times.

    Methods
    -------
    __init__(self, env, name, id, work_capacity=1, store_capacity=1, delay=0):
        Constructs a Node with the provided parameters.

    random_delay_generator(self, delay_range):
        A generator function that yields random delays within the provided range.

         Raises
        ------
        TypeError
            If 'env' is not a simpy.Environment instance, or 'name' is not a string.
        ValueError
            If 'working_capacity' or 'storage_capacity' are not positive integers.

    """

    def __init__(self, env, name,  work_capacity=1, store_capacity=1, delay=0):

        #obj_dict[comp_id] = Processor(env, item['id'], 121, 3,2,2)

        # Type checking
        if not isinstance(env, simpy.Environment):
            raise TypeError("env must be a simpy.Environment instance")
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not isinstance(work_capacity, int) or work_capacity < 0:
            raise ValueError("work_capacity must be a non-negative integer")
        if not isinstance(store_capacity, int) or store_capacity <= 0:
            raise ValueError("store_capacity must be a positive integer")
        #if not isinstance(delay, tuple) or len(delay) != 2:
         #   raise ValueError("delay must be a tuple with two numeric values")

        self.env = env
        self.name = name

        self.work_capacity = work_capacity
        self.store_capacity = store_capacity
        self.in_edges=None
        self.out_edges=None


        # Delay generator

        # Check if delay is a generator function or a tuple
        if callable(delay):
            self.delay = delay  # Use the provided generator function
        else:
            self.delay = self.random_delay_generator(delay)  # Default to random delay generator

        # Logging node creation details
        #logger.info(f"{self.env.now}: Node created: {self.name} with Work Capacity: {self.work_capacity} and Storage Capacity: {self.store_capacity}")

    def random_delay_generator(self, delay_range):
        """
        Generator function to yield random delays within a specified range.

        Parameters
        ----------
        delay_range : tuple
            A tuple (min, max) specifying the range for random delay times.

        Yields
        ------
        int
            A random delay time within the given range.
        """
        while True:
            #yield random.randint(delay_range[0], delay_range[1])
            #yield random.random()
            yield random.randint(1,3)

    def add_in_edges(self,edge):
      if self.in_edges is None:
        self.in_edges=[]
    #   if isinstance(self,Joint):
    #     assert len(self.in_edges)<2  , (f"edges are already added")
    #     if edge not in self.in_edges:
    #       self.in_edges.append(edge)
    #   elif isinstance(self,Processor):
    #     print("MinputProcessor can have moe than 1 in_edges")
    #     if edge not in self.in_edges:
    #       self.in_edges.append(edge)
      
      if len(self.in_edges)>1:
            print(f"More than 1 in edge added")
      if edge not in self.in_edges:
            self.in_edges.append(edge)

    def add_out_edges(self,edge):
      if self.out_edges is None:
        self.out_edges=[]
    #   if isinstance(self,Split):
    #     assert len(self.out_edges)<2  , (f"edges are already added")
    #     if edge not in self.out_edges:
    #       self.out_edges.append(edge)
    #   else:
      if len(self.out_edges)>1:
            print(f"More than 1 out edge added")
      if edge not in self.out_edges:
           self.out_edges.append(edge)




