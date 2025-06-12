import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
from factorysimpy.constructs.chain import connect_chain_with_source_sink, connect_nodes_with_buffers    

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
sink_kwargs = {
    "id": "Sink-1"
}


# Example for a chain of 1 machine (count=1)
nodes, edges, src, sink = connect_chain_with_source_sink(
    env,
    count=5,
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


machines, buffers = connect_nodes_with_buffers(nodes, edges, src, sink)




env.run(until=100)