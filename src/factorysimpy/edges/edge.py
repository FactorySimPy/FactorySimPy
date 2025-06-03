# @title Edge


import simpy
from factorysimpy.nodes.node import Node


class Edge:
    """
    Edge represents the passive components. It used to connect two nodes and helps to move items between them.
    It is the base class used to model buffers, conveyors, fleets, etc in manufacturing system.

    Parameters:
        state (str): The current state of the edge.
        src_node (Node): The source node connected to this edge.
        dest_node (Node): The destination node connected to this edge.
        delay (int, float, Generator, or callable): Delay after which the item becomes available. It Can be
        
            - int or float: Used as a constant delay.
            - Generator: A generator function yielding delay values.
            - Callable: A function that returns a delay (int or float).

    Raises:
        TypeError: If the type of `env` or `id` is incorrect.
        ValueError: If the `delay` parameter is not a valid type (int, float, generator, or callable).
        ValueError: If the edge is already connected to a source or destination node and reconnect is False.
        ValueError: If the source or destination nodes are not valid Node instances.
       
        

    
    """
    


    def __init__(self, env, id, delay = 0):
        self.env = env
        self.id = id
        self.state = None
        self.src_node = None
        self.dest_node = None
        
         # Type checks
        if not isinstance(env, simpy.Environment):
            raise TypeError("env must be a simpy.Environment instance")
        if not isinstance(id, str):
            raise TypeError("id must be a string")
        


        # Configure delay
        if callable(delay):
            self.delay = delay
        elif hasattr(delay, '__next__'):
            self.delay = delay
        elif isinstance(delay, (int, float)):
            self.delay = delay
    
        else:
            raise ValueError(
                "Invalid delay value. Provide a constant, generator, or a python callable."
            )

   

        
    

    def connect(self, src: Node, dest: Node, reconnect: bool = False):
        if not reconnect:
            if self.src_node or self.dest_node:
                raise ValueError(f"Edge '{self.id}' is already connected source or destination node..")
            if not isinstance(src, Node):
                raise ValueError(f"Source '{src}' is not a valid Node.")
            if not isinstance(dest, Node):
                raise ValueError(f"Destination '{dest}' is not a valid Node.")

        self.src_node = src
        self.dest_node = dest

        # Check source constraints
        print(f"Connecting edge '{self.id}' from '{src.id}' to '{dest.id}'")
        #print(self.dest_node.__class__.__name__)
        if  self.dest_node.__class__.__name__ not in ["Split","Source","Machine"]:
            # Check if out_edges is None or already configured
            
            assert self.src_node.out_edges is None or self in self.src_node.out_edges, (
                f"{self.src_node} is already connected to another edge"
            )
        else:
            # Allow up to 2 connections for Split, accounting for self already being present
            assert self.src_node.out_edges is None or self.src_node.out_edges is not None and len(self.src_node.out_edges) < 2 or self in self.src_node.out_edges, (
                f"{self.src_node} already has more than 2 edges connected"
            )

        if self.dest_node.__class__.__name__ not in ["Joint","Machine"]:
          #print(self.src_node.node_type)
          assert self.dest_node.in_edges is None or self in self.dest_node.in_edges, (f"{self.dest_node.id, self.id} is already connected to {[i.id for i in self.dest_node.in_edges]}")
        else:
          assert self.dest_node.in_edges is None or self.dest_node.in_edges is not None and len(self.dest_node.in_edges) <2 or self in self.dest_node.in_edges,  (f"{self.dest_node} already has more than 2 edges connected")

        # Register edge to nodes
        if src.out_edges is None:
            src.out_edges = []
        if self not in src.out_edges:
            src.out_edges.append(self)

        if dest.in_edges is None:
            dest.in_edges = []
        if self not in dest.in_edges:
            dest.in_edges.append(self)
        print(f"T={self.env.now:.2f}Connected edge '{self.id}' from '{src.id}' to '{dest.id}'  ")

        print(self.id,self.src_node.id,[i.id for i in self.src_node.out_edges])
        print(self.id,self.dest_node.id, [i.id for i in self.dest_node.in_edges])
