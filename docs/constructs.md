### Constructs
<hr style="height:2px;border:none;color:blue; background-color:grey;" />

**About**

Constructs in FactorySimPy are utility functions that help you quickly build common network topologies of nodes and edges, such as chains of machines with buffers, or more complex arrangements. They automate the instantiation and connection of nodes (like sources, machines, sinks) and edges (like buffers), reducing boilerplate code and making your simulation scripts more concise and less error-prone.

**Key Functions**

- `connect_chain`: Creates a chain of nodes (e.g., machines) and  edges (e.g., buffers).
- `connect_chain_with_source_sink`: Extends `connect_chain` by adding a source node at the beginning and a sink node at the end.
- `connect_nodes_with_buffers`: Connects a list of machines and buffers in sequence, optionally including a source and sink.

**Usage Example**

Suppose you want to create a simple production line:  
`Source → Buffer1 → Machine1 → Buffer2 → Machine2 → Buffer3 → Sink`

You can do this easily with constructs:

```python
import simpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
from factorysimpy.constructs.chain import connect_chain_with_source_sink

env = simpy.Environment()

# Define parameters for each component
source_kwargs = {"inter_arrival_time": 1.0, "blocking": True}
node_kwargs = {"work_capacity": 1, "processing_delay": 2.0, "in_edge_selection": "FIRST", "out_edge_selection": "FIRST"}
edge_kwargs = {"store_capacity": 5, "delay": 0.5, "mode": "FIFO"}
sink_kwargs = {}

# Create a chain with 2 machines, 3 buffers, a source, and a sink
nodes, edges, src, sink = connect_chain_with_source_sink(
    env,
    count=2,
    node_cls=Machine,
    edge_cls=Buffer,
    source_cls=Source,
    sink_cls=Sink,
    node_kwargs=node_kwargs,
    edge_kwargs=edge_kwargs,
    source_kwargs=source_kwargs,
    sink_kwargs=sink_kwargs
)

machines, buffers = connect_nodes_with_buffers(machines, buffers, src, sink)

# Now, nodes and edges are connected in order and connected:
# src -> edges[0] -> nodes[1] -> edges[1] -> nodes[2] -> edges[2] -> sink

env.run(until=20)
```

**Custom Connections**

If you want to connect a list of machines and buffers you created yourself, use `connect_nodes_with_buffers`:

```python
machines = [Machine(env, id=f"M{i}", **node_kwargs) for i in range(2)]
buffers = [Buffer(env, id=f"BUF{i}", **edge_kwargs) for i in range(3)]
src = Source(env, id="SRC", **source_kwargs)
sink = Sink(env, id="SINK", **sink_kwargs)

# Connect: src -> BUF0 -> M0 -> BUF1 -> M1 -> BUF2 -> sink
machines, buffers = connect_nodes_with_buffers(machines, buffers, src, sink)
```


**Example**

- [A simple example with constructs](examples.md/#example-with-constructs)

<hr style="height:4px;border:none;color:blue; background-color:grey;" />