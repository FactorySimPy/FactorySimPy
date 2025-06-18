import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
from factorysimpy.constructs.chain import connect_chain_with_source_sink, connect_nodes_with_buffers    

env = simpy.Environment()

#   SRC ──> BUFFER1 ───> MACHINE1 ───> BUFFER2 ──> MACHINE2 ───> BUFFER3 ──> MACHINE3 ───> BUFFER4 ──> SINK




node_kwargs_list = [ {
   
    "node_setup_time": 0,
    "work_capacity": 1,
    "processing_delay": 5,
    "blocking": True,
    "in_edge_selection": "FIRST_AVAILABLE",
    "out_edge_selection": "FIRST_AVAILABLE"
},{
   
    "node_setup_time": 0,
    "work_capacity": 1,
    "processing_delay": 6,
    "blocking": True,
    "in_edge_selection": "FIRST_AVAILABLE",
    "out_edge_selection": "FIRST_AVAILABLE"
},{
   
    "node_setup_time": 0,
    "work_capacity": 1,
    "processing_delay": 7,
    "blocking": True,
    "in_edge_selection": "FIRST_AVAILABLE",
    "out_edge_selection": "FIRST_AVAILABLE"
}, {
   
    "node_setup_time": 0,
    "work_capacity": 1,
    "processing_delay": 7,
    "blocking": True,
    "in_edge_selection": "FIRST_AVAILABLE",
    "out_edge_selection": "FIRST_AVAILABLE"
}

]

edge_kwargs = {
    
    "store_capacity": 1,
    "delay": 0,
    "mode": "LIFO"
}

source_kwargs = {
    
    "inter_arrival_time": 1,
    "blocking": True,
    "out_edge_selection": "FIRST_AVAILABLE"
}
sink_kwargs = {
    "id": "Sink-1"
}


# Example for a chain of 1 machine (count=1)
nodes, edges, src, sink = connect_chain_with_source_sink(
    env,
    count=3,
    node_cls=Machine,
    edge_cls=Buffer,
    source_cls=Source,
    sink_cls=Sink,
    node_kwargs_list=node_kwargs_list,
    edge_kwargs=edge_kwargs,
    source_kwargs = source_kwargs,
    sink_kwargs= sink_kwargs,
    prefix="Machine",
    edge_prefix="Buffer"
)

print([i.id for i in nodes])
print([i.id for i in edges])

machines, buffers = connect_nodes_with_buffers(nodes, edges, src, sink)




env.run(until=100)


print(f"Sink {sink.id} received {sink.stats['num_item_received']} items.")

# Print statistics
print(f"Source {src.id} generated {src.stats['num_item_generated']} items.")
print(f"Throughput of system: {sink.stats['num_item_received'] / env.now:.2f} items per time unit.")