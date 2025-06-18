
import simpy,sys, os
import scipy.stats


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
import random

env= simpy.Environment()


def machine_out_edge_selector_func():
  
        v= random.random()
        print(v)
        if v<0.2:
            return 0
        elif v<0.4:
            return 1
        elif v<0.6:
            return 6
        elif v<0.8:
             return 7
        else:
            return 5

def machine_out_edge_selector():
   while True:
        v= random.random()
        print(v)
        if v<0.2:
            yield 0
        elif v<0.4:
            yield 1
        elif v<0.6:
            yield 6
        elif v<0.8:
             yield 7
        else:
            yield 5
func= machine_out_edge_selector()
def setup_machine_with_ten_buffers_sinks(env_for_test):
    # create sources 
    SRC1= Source(env_for_test, id="SRC1", inter_arrival_time=0.5, blocking=True, out_edge_selection=0)
    
    SINK1= Sink(env_for_test, id="SINK1")
    SINK2= Sink(env_for_test, id="SINK2")
    SINK3= Sink(env_for_test, id="SINK3")
    SINK4= Sink(env_for_test, id="SINK4")
    SINK5= Sink(env_for_test, id="SINK5")
    SINK6= Sink(env_for_test, id="SINK6")
    SINK7= Sink(env_for_test, id="SINK7")
    SINK8= Sink(env_for_test, id="SINK8")
    
    sink_list = [SINK1, SINK2, SINK3, SINK4, SINK5, SINK6, SINK7, SINK8]

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
    out_buf_list= [BUF1, BUF2, BUF3, BUF4, BUF5, BUF6, BUF7, BUF8,  ]

    # Create output buffer
    in_buffer = Buffer(env_for_test, "inBuffer", store_capacity=2)

    # Create machine
    machine = Machine(
        env=env_for_test,
        id="M1",
        in_edges=[],
        out_edges=[],
        processing_delay=0.2,
        node_setup_time=0,
        work_capacity=1,
        in_edge_selection=0,
        out_edge_selection=machine_out_edge_selector_func,
    )
    
    # create source and sink
  
    
    return env_for_test, machine, SRC1, out_buf_list, in_buffer, sink_list


env, machine,src, out_buffer_list,  in_buffer, sink_list = setup_machine_with_ten_buffers_sinks(env_for_test=env)
for i in range(len(out_buffer_list)):
    out_buffer_list[i].connect(machine,sink_list[i])
    
in_buffer.connect(src, machine)

env.run(until=20)
print("Simulation completed.")


