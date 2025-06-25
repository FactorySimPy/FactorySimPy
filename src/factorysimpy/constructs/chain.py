def connect_chain(env, count, node_cls, edge_cls,
                  node_kwargs=None, edge_kwargs=None,
                  node_kwargs_list=None, edge_kwargs_list=None,
                  prefix="Node", edge_prefix="Edge"):
    nodes = []
    edges = []

    for i in range(count):
        print(i)
        kwargs = node_kwargs_list[i] if node_kwargs_list else node_kwargs or {"processing_delay": 0.8,"blocking": True}
        node_name = f"{prefix}_{i+1}"
        if "id" in kwargs:
            node_name = kwargs["id"]
            del kwargs["id"]
        node = node_cls(env=env, id=node_name, **kwargs)
        nodes.append(node)

    for i in range(count + 1):
    
        kwargs = edge_kwargs_list[i] if edge_kwargs_list else edge_kwargs or {}
        edge_name = f"{edge_prefix}_{i+1}"
        if "id" in kwargs:
            edge_name = kwargs["id"]
            del kwargs["id"]
        edge = edge_cls(env=env, id=edge_name, **kwargs)
        edges.append(edge)

        #nodes[i].out_edge = edge
        #nodes[i+1].in_edge = edge

    return nodes, edges

def connect_chain_with_source_sink(env, count, node_cls, edge_cls,
                                    node_kwargs=None, edge_kwargs=None,
                                    node_kwargs_list=None, edge_kwargs_list=None,
                                    prefix="Node", edge_prefix="Edge",
                                    source_cls=None, sink_cls=None,
                                    source_kwargs=None, sink_kwargs=None):
    nodes, edges = connect_chain(env, count, node_cls, edge_cls,
                                    node_kwargs, edge_kwargs,
                                    node_kwargs_list, edge_kwargs_list,
                                    prefix, edge_prefix)
    if source_cls:
        source_kwargs = source_kwargs or {"inter_arrival_time": 1, "blocking": True, }
        src_name ="Source"
        if "id" in source_kwargs:
            src_name = source_kwargs["id"]
            del source_kwargs["id"]
        source = source_cls(env=env, id=src_name, **source_kwargs)
        #source.out_edge = edges[0]
        #nodes[0].in_edge = edges[0]
        nodes.insert(0, source)
        #edges.insert(0, None)
    else:
        source = None

    if sink_cls:
        sink_kwargs = sink_kwargs or {}
        sink_name = "Sink"
        if "id" in sink_kwargs:
            sink_name = sink_kwargs["id"]
            del sink_kwargs["id"]
        sink = sink_cls(env=env, id=sink_name, **sink_kwargs)
        #sink.in_edge = edges[-1]
        #nodes[-1].out_edge = edges[-1]
        nodes.append(sink)
        #edges.append(None)
    else:
        sink = None

    #print([i.id for i in nodes])
    #print([i.id for i in edges])

    return nodes, edges, source, sink


def connect_nodes_with_buffers(machines, buffers, src, sink):
    """
    Connects source, machines, buffers, and optionally a sink in the following order:
    src -> buffer1 -> machine1 -> buffer2 -> machine2 -> ... -> bufferN -> sink

    Args:
        src: Source node
        machines: List of machine nodes
        buffers: List of buffer edges (should be len(machines) - 1) inlcuding source and sink
        sink: Optional sink node

    Returns:
        List of all nodes and buffers in connection order
    """
    assert len(buffers) == len(machines) - 1, "Number of buffers must be one more than number of machines"


    # Connect intermediate machines and buffers
    for i in range(1, len(machines)):
        buffers[i-1].connect(machines[i-1], machines[i])

    
        

    # Return all nodes and buffers for reference
    
    return machines, buffers