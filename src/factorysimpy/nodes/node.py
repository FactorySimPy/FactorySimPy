from typing import Generator, Optional, Union, Any
import simpy
import random


class Node:
    """
    Base class to represent an active entity in a manufacturing system,
    such as processors, splits, or joints.

    Attributes
    ----------
    
    name : str
        Identifier for the node.
    work_capacity : int
        Number of simultaneous operations the node can perform.
    store_capacity : int
        Capacity of internal storage.
    delay : int | float | Generator
        Processing delay as a constant, a generator, or a range (tuple).
    in_edges : list, optional
        List of input edges connected to the node.
    out_edges : list, optional
        List of output edges connected to the node.

    Raises
    ------
    TypeError
        If types of `env` or `name` are incorrect.
    ValueError
        If capacities or delay inputs are invalid.
    """

    def __init__(
        self,
        env: simpy.Environment,
        name: str,
        in_edges: Optional[list] = None,
        out_edges: Optional[list] = None,
        work_capacity: int = 1,
        store_capacity: int = 1,
        delay: Union[int, float, tuple, Generator] = 0,
    ):
        # Type checks
        if not isinstance(env, simpy.Environment):
            raise TypeError("env must be a simpy.Environment instance")
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not isinstance(work_capacity, int) or work_capacity < 0:
            raise ValueError("work_capacity must be a non-negative integer")
        if not isinstance(store_capacity, int) or store_capacity <= 0:
            raise ValueError("store_capacity must be a positive integer")

        self.env = env
        self.name = name
        self.work_capacity = work_capacity
        self.store_capacity = store_capacity
        self.in_edges = in_edges
        self.out_edges = out_edges

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

    def add_in_edges(self, edge: Any):
        """
        Add an input edge to the node.

        Parameters
        ----------
        edge : any
            The edge to add as an input edge.

        Raises
        ------
        NotImplementedError
            This base method should be overridden in derived classes.
        """
        raise NotImplementedError("add_in_edges must be implemented in a subclass.")

    def add_out_edges(self, edge: Any):
        """
        Add an output edge to the node.

        Parameters
        ----------
        edge : any
            The edge to add as an output edge.

        Raises
        ------
        NotImplementedError
            This base method should be overridden in derived classes.
        """
        raise NotImplementedError("add_out_edges must be implemented in a subclass.")

    def behaviour(self):
        """
        Define the main behavior of the node.

        Raises
        ------
        NotImplementedError
            This base method should be overridden in derived classes.
        """
        raise NotImplementedError("behaviour must be implemented in a subclass.")
