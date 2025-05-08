# @title Edge

from typing import Optional, Union, Generator
import random
import simpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.split import Split
from factorysimpy.nodes.joint import Joint



class Edge:
    """
      Edge class representing a connection between nodes in a simulation environment.
      This class is used to connect a source node  to a destination node.
      Attributes
      ----------

      state : str
          The current state of the edge.
      src_node : Node
          The source node connected to this edge.
      dest_node : Node
          The destination node connected to this edge.
      delay : int | float | Generator
          Delay after which the item becomes available;
          Delay as a constant, a generator, or a range (tuple).

      Methods
      -------
      connect(self, src, dest, reconnect=False):
          Connects the edge to a source and destination node.
      Raises
      ------
      ValueError
          If the edge is already connected to a source or destination node and reconnect is False.
          If the source or destination nodes are not valid Node instances.
          If the source node is not a Split or the destination node is not a Joint.
          If the edge is already connected to the source or destination node.
      """
    


    def __init__(self, env: simpy.Environment, name: str, delay: Union[int, float, tuple, Generator] = 0):
        self.env = env
        self.name = name
        self.state: Optional[str] = None
        self.src_node: Optional[Node] = None
        self.dest_node: Optional[Node] = None
        
         # Type checks
        if not isinstance(env, simpy.Environment):
            raise TypeError("env must be a simpy.Environment instance")
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        


        # Configure delay
        if isinstance(delay, Generator):
            self.delay = delay
        elif isinstance(delay, tuple) and len(delay) == 2:
            self.delay = self.random_delay_generator(delay)
        elif isinstance(delay, (int, float)):
            self.delay = delay
        else:
            raise ValueError(
                "Invalid delay value. Provide a constant, generator, or a (min, max) tuple."
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
        int
            A random delay time in the given range.
        """
        while True:
            yield random.randint(*delay_range)

        
       

    def connect(self, src: Node, dest: Node, reconnect: bool = False):
        if not reconnect:
            if self.src_node or self.dest_node:
                raise ValueError(f"Edge '{self.name}' is already connected source or destination node..")
            if not isinstance(src, Node):
                raise ValueError(f"Source '{src}' is not a valid Node.")
            if not isinstance(dest, Node):
                raise ValueError(f"Destination '{dest}' is not a valid Node.")

        self.src_node = src
        self.dest_node = dest

        # Check source constraints
        if not isinstance(self.src_node, Split):
            # Check if out_edges is None or already configured
            
            assert self.src_node.out_edges is None or self in self.src_node.out_edges, (
                f"{self.src_node} is already connected to another edge"
            )
        else:
            # Allow up to 2 connections for Split, accounting for self already being present
            assert self.src_node.out_edges is not None and len(self.src_node.out_edges) < 2 or self in self.src_node.out_edges, (
                f"{self.src_node} already has more than 2 edges connected"
            )

        if not isinstance(self.dest_node, Joint):
          
          assert self.dest_node.in_edges is None or self in self.dest_node.in_edges, (f"{self.dest_node} is already connected")
        else:
          assert self.dest_node.in_edges is not None and len(self.dest_node.in_edges) <2 or self in self.dest_node.in_edges,  (f"{self.dest_node} already has more than 2 edges connected")

        # Register edge to nodes
        if src.out_edges is None:
            src.out_edges = []
        if self not in src.out_edges:
            src.out_edges.append(self)

        if dest.in_edges is None:
            dest.in_edges = []
        if self not in dest.in_edges:
            dest.in_edges.append(self)
        print(f"T={self.env.now:.2f}Connected edge '{self.name}' from '{src.name}' to '{dest.name}'  ")
