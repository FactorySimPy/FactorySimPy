import random

def get_index_selector(sel_type,obj, env):
    """
    Returns a function that selects the index from a given object.

    Parameters
    ----------
    index : int or str
        The index to select.

    Returns
    -------
    function
        A function that takes an object and returns the value at the specified index.
    """
    if sel_type == "RANDOM":
        sel = Random(obj,env) 
        return sel
    elif sel_type == "FIRST":
        sel = First(obj,env)
        return sel
    elif sel_type == "LAST":
        sel = Last(obj,env)
        return sel
    elif sel_type == "ROUND_ROBIN":
        sel = RoundRobin(obj,env)
        return sel
    elif sel_type == "FIRST_AVAILABLE":
        sel = FirstAvailable(obj,env)
        return sel
    else:
        raise ValueError(f"Invalid selection type: {sel_type}. Must be one of: RANDOM, FIRST, LAST, ROUND_ROBIN, FIRST_AVAILABLE.")
    
    

def Random(node,env):
    """
    Generator function that yields a random index from the given object.
    Parameters
    ----------      
    node : node object
        The object from which out_edges list is to be taken
    env : simpy.Environment
        The simulation environment.
    Yields
    -------
    int
        A random index from the object.
    """
    num_edges = len(node.out_edges)
    while True:
        yield random.randint(0,num_edges-1)

def RoundRobin(node, env):
    num_edges=len(node.out_edges)
    edge=0
    while True:
        yield edge
        
        edge=(edge+1)%num_edges

def First(node, env):
    """
    Generator function that yields the first index from the given object.
    
    Parameters
    ----------
    node : node object
        The object from which out_edges list is to be taken
    env : simpy.Environment
        The simulation environment.
        
    Yields
    -------
    int
        The first index (0) from the object.
    """
    while True:
        yield 0
def Last(node, env):
    """ 
    Generator function that yields the last index from the given object.
    Parameters
    ----------
    node : node object
        The object from which out_edges list is to be taken
    env : simpy.Environment
        The simulation environment.
    Yields
    -------
    int
        The last index from the object.
    """
    num_edges = len(node.out_edges)
    while True:
        yield num_edges - 1
def FirstAvailable(node, env):
    """
    Generator function that yields the first available index from the given object.
    Parameters
    ----------
    node : node object
        The object from which out_edges list is to be taken     
    env : simpy.Environment
        The simulation environment.
    Yields

    -------
    int
        The first available index from the object.
    """
    num_edges = len(node.out_edges)
    while True:
        for i in range(num_edges):
            print(f"{env.now:.2f}Checking edge {i} for availability")
            if node.out_edges[i].can_put():
                print(i)
                yield i
    
        