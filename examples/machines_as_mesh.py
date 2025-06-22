import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
#from factorysimpy.constructs.chain import connect_chain_with_source_sink, connect_nodes_with_buffers    
from factorysimpy.constructs.mesh import connect_mesh
env = simpy.Environment()

node_kwargs = {
   
    "node_setup_time": 0,
    "work_capacity": 1,
    "processing_delay": 0.8,
    "in_edge_selection": "FIRST_AVAILABLE",
    "out_edge_selection": "FIRST_AVAILABLE"
}

edge_kwargs = {
    
    "store_capacity": 4,
    "delay": 0,
    "mode": "LIFO"
}

source_kwargs = {
    
    "inter_arrival_time": 1,
    "blocking": True,
    "out_edge_selection": "FIRST_AVAILABLE"
}

sink_kwargs = {}



nodes, edges, = connect_mesh(
    env,
    rows=2,
    cols=2,
    node_cls=Machine,
    edge_cls=Buffer,
    source_cls=Source,
    sink_cls=Sink,
    node_kwargs=node_kwargs,
    edge_kwargs=edge_kwargs,
    source_kwargs = source_kwargs,
    sink_kwargs= sink_kwargs,
    prefix="Machine",
    edge_prefix="Buffer"
)

#print("Nodes and Edges created:")
print (edges)
for edge in edges:
    print(f"Edge ID: {edge.id}, "
          f"in_node: {edge.in_node.id if edge.in_node else None}, "
          f"out_node: {edge.out_node.id if edge.out_node else None}, "
          f"store_capacity: {edge.store_capacity}, "
          f"delay: {edge.delay}, "
          f"mode: {edge.mode}")

#print(nodes)
for row in nodes:
    print("row",row)
    for node in row:
        print(
    f"Node ID: {node.id}, "
    f"in_edges: {[edge.id for edge in node.in_edges] if node.in_edges else []}, "
    f"out_edges: {[edge.id for edge in node.out_edges] if node.out_edges else []}"
)



SRC = Source(env, id="Source", inter_arrival_time=1, blocking=True, out_edge_selection="FIRST_AVAILABLE")
SINK = Sink(env, id="Sink")
Buffer_SRC_M11 = Buffer(env, id="Buffer_SRC_M11", store_capacity=4, delay=0, mode="LIFO")
Buffer_M22_SINK = Buffer(env, id="Buffer_M22_SINK", store_capacity=4, delay=0, mode="LIFO")
Buffer_SRC_M11.connect(SRC, nodes[0][0])
Buffer_M22_SINK.connect(nodes[1][1], SINK)

env.run(until=1)
print("Simulation completed.")
print(f"Num items produced: {SRC.stats['num_item_generated']}")
print(f"Num items finished: {SINK.stats['num_item_received']}")