import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
from factorysimpy.constructs.chain import connect_chain_with_source_sink, connect_nodes_with_buffers    
import random
env = simpy.Environment()

def generate_gaussian(mu, sigma):
    while True:
     yield random.gauss(mu, sigma)

def generate_uniform(a, b):
    while True:
        yield random.uniform(a, b)

def generate_exponential(lambd):
    while True:
        yield random.expovariate(lambd)

def generate_gamma(alpha, beta):
    while True:
        yield random.gammavariate(alpha, beta)

def generate_lognorm(mu, sigma):
    while True:
        yield random.lognormvariate(mu, sigma)
    

M1_processing_delay=generate_gaussian(2, 0.5)
M2_processing_delay=generate_uniform(1, 2)
M3_processing_delay=generate_exponential(1)
M4_processing_delay=generate_gamma(2, 1)
M5_processing_delay=generate_lognorm(0, 0.1)
M6_processing_delay=generate_gaussian(4.5, 0.3)
M7_processing_delay=generate_uniform(0.5, 1.5)
M8_processing_delay=generate_exponential(0.5)
M9_processing_delay=generate_gamma(1, 0.5)
M10_processing_delay=generate_lognorm(0, 0.2)


node_kwargs_list = [{
    "id": "M1",
    "node_setup_time": 0,
    "work_capacity": 1,
    "processing_delay": M1_processing_delay,
    "in_edge_selection": "FIRST_AVAILABLE",
    "out_edge_selection": "FIRST_AVAILABLE"
}, {"id": "M2",
   
    "node_setup_time": 0,
    "work_capacity": 1,
    "processing_delay": 0.8,
    "in_edge_selection": "FIRST_AVAILABLE",
    "out_edge_selection": "FIRST_AVAILABLE"
}]

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
    "id": "Sink1"
}


# Example for a chain of 1 machine (count=1)
nodes, edges, src, sink = connect_chain_with_source_sink(
    env,
    count=5,
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


machines, buffers = connect_nodes_with_buffers(nodes, edges, src, sink)




env.run(until=100)