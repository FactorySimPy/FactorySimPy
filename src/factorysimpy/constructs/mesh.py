

def connect_mesh(env, rows, cols, node_cls, edge_cls,
                                  node_kwargs=None, edge_kwargs=None,
                                  node_kwargs_grid=None, edge_kwargs_grid=None,
                                  prefix="M", edge_prefix="B",
                                  source_cls=None, sink_cls=None,
                                  source_kwargs=None, sink_kwargs=None):
    """
    Builds a mesh/grid of nodes connected with buffers.
    Each node is connected to its right and down neighbor.

    Returns:
        mesh_nodes: 2D list of nodes (rows x cols)
        edge_dict: dict of buffers by (from_node.id, to_node.id)
    """
    node_kwargs = node_kwargs or {}
    edge_kwargs = edge_kwargs or {}

    mesh_nodes = []
    edge_dict = {}

    def get_kwargs(grid, r, c, default):
        if grid and r < len(grid) and c < len(grid[r]):
            return grid[r][c]
        return default

    # Create nodes (machines)
    for r in range(rows):
        row = []
        for c in range(cols):
            kwargs = get_kwargs(node_kwargs_grid, r, c, node_kwargs)
            node_id = f"{prefix}_{r+1}_{c+1}"
            node = node_cls(env=env, id=node_id, **kwargs)
            row.append(node)
        mesh_nodes.append(row)

    # Helper to create and connect edges
    def create_edge(from_node, to_node, r, c):
        kwargs = get_kwargs(edge_kwargs_grid, r, c, edge_kwargs)
        edge_id = f"{edge_prefix}_{from_node.id}_{to_node.id}"
        edge = edge_cls(env=env, id=edge_id, **kwargs)
        edge.connect(from_node, to_node)
        edge_dict[(from_node.id, to_node.id)] = edge

    # Create buffers (edges) to right and down
    for r in range(rows):
        for c in range(cols):
            from_node = mesh_nodes[r][c]
            if c + 1 < cols:
                create_edge(from_node, mesh_nodes[r][c+1], r, c)
            if r + 1 < rows:
                create_edge(from_node, mesh_nodes[r+1][c], r, c)

    return mesh_nodes,edge_dict




def connect_mesh_with_source_sink(env, rows, cols, node_cls, edge_cls,
                                  node_kwargs=None, edge_kwargs=None,
                                  node_kwargs_grid=None, edge_kwargs_grid=None,
                                  prefix="M", edge_prefix="B",
                                  source_cls=None, sink_cls=None,
                                  source_kwargs=None, sink_kwargs=None):
    """
    Builds a mesh/grid of nodes connected with buffers.
    Source sends to first row, Sink collects from last row.

    Returns:
        mesh_nodes: 2D list of nodes (rows x cols)
        edge_dict: dict of buffers by (from_node.id, to_node.id)
        source, sink: optional
    """
    node_kwargs = node_kwargs or {}
    edge_kwargs = edge_kwargs or {}
    source_kwargs = source_kwargs or {}
    sink_kwargs = sink_kwargs or {}

    mesh_nodes = []
    edge_dict = {}

    # Create nodes (machines)
    for r in range(rows):
        row = []
        for c in range(cols):
            kwargs = node_kwargs_grid[r][c] if node_kwargs_grid else node_kwargs
            node_id = f"{prefix}_{r+1}_{c+1}"
            node = node_cls(env=env, id=node_id, **kwargs)
            row.append(node)
        mesh_nodes.append(row)

    # Create buffers (edges) to right and down
    for r in range(rows):
        for c in range(cols):
            from_node = mesh_nodes[r][c]

            # Connect right
            if c + 1 < cols:
                to_node = mesh_nodes[r][c+1]
                edge_id = f"{edge_prefix}_{from_node.id}_{to_node.id}"
                kwargs = edge_kwargs_grid[r][c] if edge_kwargs_grid else edge_kwargs
                edge = edge_cls(env=env, id=edge_id, **kwargs)
                edge.connect(from_node, to_node)
                edge_dict[(from_node.id, to_node.id)] = edge

            # Connect down
            if r + 1 < rows:
                to_node = mesh_nodes[r+1][c]
                edge_id = f"{edge_prefix}_{from_node.id}_{to_node.id}"
                kwargs = edge_kwargs_grid[r][c] if edge_kwargs_grid else edge_kwargs
                edge = edge_cls(env=env, id=edge_id, **kwargs)
                edge.connect(from_node, to_node)
                edge_dict[(from_node.id, to_node.id)] = edge

    # Optional source
    source = None
    if source_cls:
        source = source_cls(env=env, id="Source", **source_kwargs)
        for c in range(cols):
            to_node = mesh_nodes[0][c]
            edge_id = f"{edge_prefix}_SRC_{to_node.id}"
            edge = edge_cls(env=env, id=edge_id, **edge_kwargs)
            edge.connect(source, to_node)
            edge_dict[(source.id, to_node.id)] = edge

    # Optional sink
    sink = None
    if sink_cls:
        sink = sink_cls(env=env, id="Sink", **sink_kwargs)
        for c in range(cols):
            from_node = mesh_nodes[rows-1][c]
            edge_id = f"{edge_prefix}_{from_node.id}_SINK"
            edge = edge_cls(env=env, id=edge_id, **edge_kwargs)
            edge.connect(from_node, sink)
            edge_dict[(from_node.id, sink.id)] = edge

    return mesh_nodes, edge_dict, source, sink


