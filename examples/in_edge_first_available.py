
import simpy,sys, os
import scipy.stats


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
import random

env= simpy.Environment()

def setup_machine_with_ten_buffers_sources(env_for_test):
    # create sources 
    SRC1= Source(env_for_test, id="SRC1", inter_arrival_time=0.5, blocking=True, out_edge_selection=0)
    SRC2= Source(env_for_test, id="SRC2", inter_arrival_time=0.5, blocking=True, out_edge_selection=0)
    SRC3= Source(env_for_test, id="SRC3", inter_arrival_time=0.5, blocking=True, out_edge_selection=0)
    SRC4= Source(env_for_test, id="SRC4", inter_arrival_time=0.5, blocking=True, out_edge_selection=0)
    SRC5= Source(env_for_test, id="SRC5", inter_arrival_time=0.3, blocking=True, out_edge_selection=0)# first arriving
    SRC6= Source(env_for_test, id="SRC6", inter_arrival_time=0.5, blocking=True, out_edge_selection=0)
    SRC7= Source(env_for_test, id="SRC7", inter_arrival_time=0.5, blocking=True, out_edge_selection=0)
    SRC8= Source(env_for_test, id="SRC8", inter_arrival_time=0.5, blocking=True, out_edge_selection=0)
    #SRC9= Source(env_for_test, id="SRC9", inter_arrival_time=0.5, blocking=True, out_edge_selection=0)
    #SRC10= Source(env_for_test, id="SRC10", inter_arrival_time=0.5, blocking=True, out_edge_selection=0)
    
    src_list = [SRC1, SRC2, SRC3, SRC4, SRC5, SRC6, SRC7, SRC8, ]

    # Create input buffers
    BUF1 = Buffer(env_for_test, "BUF1", store_capacity=2)
    BUF2 = Buffer(env_for_test, "BUF2", store_capacity=2)
    BUF3 = Buffer(env_for_test, "BUF3", store_capacity=2)
    BUF4 = Buffer(env_for_test, "BUF4", store_capacity=2)
    BUF5 = Buffer(env_for_test, "BUF5", store_capacity=2)
    BUF6 = Buffer(env_for_test, "BUF6", store_capacity=2)
    BUF7 = Buffer(env_for_test, "BUF7", store_capacity=2)
    BUF8 = Buffer(env_for_test, "BUF8", store_capacity=2)
    #BUF9 = Buffer(env_for_test, "BUF9", store_capacity=2)
    #BUF10 = Buffer(env_for_test, "BUF10", store_capacity=2)

    # Create input buffers for the machine
    in_buf_list= [BUF1, BUF2, BUF3, BUF4, BUF5, BUF6, BUF7, BUF8,  ]

    # Create output buffer
    out_buffer = Buffer(env_for_test, "OutBuffer", store_capacity=2)

    # Create machine
    machine = Machine(
        env=env_for_test,
        id="M1",
        in_edges=[],
        out_edges=[],
        processing_delay=0.2,
        node_setup_time=0,
        work_capacity=1,
        in_edge_selection="FIRST_AVAILABLE",
        out_edge_selection=0
    )
    
    # create source and sink
  
    sink = Sink(env_for_test, id="Sink-1")
    return env_for_test, machine, src_list, in_buf_list, out_buffer, sink


env, machine,src_list, in_buffer_list,  out_buffer, sink = setup_machine_with_ten_buffers_sources(env_for_test=env)
for i in range(len(in_buffer_list)):
    in_buffer_list[i].connect(src_list[i], machine)
    
out_buffer.connect(machine, sink)

env.run(until=20)
print("Simulation completed.")


