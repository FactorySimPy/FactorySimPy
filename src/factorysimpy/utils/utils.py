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
        
        "ROUND_ROBIN": RoundRobin,
       
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


