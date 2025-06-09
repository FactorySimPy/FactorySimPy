import random

def get_index_selector(sel_type, node, env, edge_type="OUT"):
    """
    Returns a generator that yields selected indices from the node's edge list.

    Args:
    
        sel_type (str): The selection strategy. One of: 'RANDOM', 'FIRST', 'LAST', 'ROUND_ROBIN', 'FIRST_AVAILABLE'.
        node (object): The node object containing in_edges or out_edges.
        env (simpy.Environment): The simulation environment.
        edge_type (str, optional): Whether to select from 'out_edges' or 'in_edges'. Default is 'OUT'.

    Returns:

        generator: A generator yielding selected indices from the specified edge list.

    Raises:

        ValueError: If sel_type is not a valid selection strategy.
  
    """
    edge_type = edge_type.lower()
    strategies = {
        "RANDOM": Random,
        "FIRST": First,
        "LAST": Last,
        "ROUND_ROBIN": RoundRobin,
        "FIRST_AVAILABLE": FirstAvailable
    }

    if sel_type not in strategies:
        raise ValueError(
            f"Invalid selection type: {sel_type}. Must be one of: {', '.join(strategies.keys())}."
        )
    #print(edge_type)
    return strategies[sel_type](node, env, edge_type)

def Random(node, env, edge_type):
    while True:
    
        edges = getattr(node, f"{edge_type}_edges")
        yield random.randint(0, len(edges) - 1)

def RoundRobin(node, env, edge_type):
    i = 0
    while True:
        edges = getattr(node, f"{edge_type}_edges")
        yield i
        i = (i + 1) % len(edges)

def First(node, env, edge_type):
    while True:
        yield 0

def Last(node, env, edge_type):
    while True:
        edges = getattr(node, f"{edge_type}_edges")
        yield len(edges) - 1

def FirstAvailable1(node, env, edge_type):
    while True:
        edges = getattr(node, f"{edge_type}_edges")
        for i in range(len(edges)):
            if edges[i].can_put():
                yield i
            if i== len(edges) - 1:
                i = -1

def FirstAvailable(node, env, edge_type):
    """
    Generator that yields the index of the first available edge in a node's edge list.

    Args:
        node (object): The node object containing edges.
        env (simpy.Environment): The simulation environment.
        edge_type (str): Type of edges to check ('in_edges' or 'out_edges').

    Yields:
        int: Index of the first available edge.

    """
    event = env.event()
    setup_FirstAvailable(node, env, edge_type, event)
    return event

def setup_FirstAvailable(node, env, edge_type,event):
    
    first_available = do_FirstAvailable(node, env, edge_type)
    k=next(first_available)
    event.succeed(k)


def do_FirstAvailable(node, env, edge_type):
    while True:
        i=0
        edges = getattr(node, f"{edge_type}_edges")
        num_edges = len(edges)
        while i < num_edges:
            if edges[i].can_put():
                yield i
            if i== num_edges - 1:
                i == 0
            else:
                i += 1
