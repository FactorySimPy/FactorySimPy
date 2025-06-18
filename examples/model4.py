# to test buffers blocking behavior of buffer

import simpy,sys, os
import scipy.stats

import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
import random

#   SRC1 ──> BUFFER1 ──> MACHINE1 ──>BUFFER4──────┬         
#                                                 │ 
#   SRC2 ──> BUFFER2 ───> MACHINE2───>BUFFER5───>MACHINE4 ───> BUFFER7 ───>MACHINE4 ───> BUFFER8 ──> SINK1
#                                                  │
#   SRC3 ──> BUFFER3 ───> MACHINE3 ───>BUFFER6   ──┘         



env = simpy.Environment()





# Initializing nodes
SRC1= Source(env, id="SRC1",  inter_arrival_time=0.2,blocking=True, out_edge_selection="FIRST_AVAILABLE" )
SRC2= Source(env, id="SRC2",  inter_arrival_time=0.2,blocking=True, out_edge_selection="FIRST_AVAILABLE" )
SRC3= Source(env, id="SRC3",  inter_arrival_time=0.2,blocking=True, out_edge_selection="FIRST_AVAILABLE" )

MACHINE1 = Machine(env, id="MACHINE1",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection=0,out_edge_selection=0)
MACHINE2 = Machine(env, id="MACHINE2",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection=0,out_edge_selection=0)
MACHINE3 = Machine(env, id="MACHINE3",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection=0,out_edge_selection=0)


MACHINE4 = Machine(env, id="MACHINE3",work_capacity=3,blocking=True, processing_delay=0.5,in_edge_selection="ROUND_ROBIN",out_edge_selection=0)
MACHINE5 = Machine(env, id="MACHINE3",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection=0,out_edge_selection=0)

SINK1= Sink(env, id="SINK1")










# Initializing edges
# Initializing edges
BUF1 = Buffer(env, id="BUF1", store_capacity=1, delay=0)
BUF2 = Buffer(env, id="BUF2", store_capacity=1, delay=0)
BUF3 = Buffer(env, id="BUF3", store_capacity=1, delay=2)
BUF4 = Buffer(env, id="BUF4", store_capacity=1, delay=2)
BUF5 = Buffer(env, id="BUF5", store_capacity=1, delay=0)
BUF6 = Buffer(env, id="BUF6", store_capacity=1, delay=0)
BUF7 = Buffer(env, id="BUF5", store_capacity=1, delay=0)
BUF8 = Buffer(env, id="BUF6", store_capacity=1, delay=0)


# Adding connections
BUF1.connect(SRC1,MACHINE1)
BUF2.connect(SRC2,MACHINE2)
BUF3.connect(SRC3,MACHINE3)

BUF4.connect(MACHINE1,MACHINE4)
BUF5.connect(MACHINE2,MACHINE4)
BUF6.connect(MACHINE3,MACHINE4)
BUF7.connect(MACHINE4,MACHINE5)
BUF8.connect(MACHINE5,SINK1)




env.run(until=100)
print("Simulation completed.")
# Print statistics
print(f"Source generated {SRC1.stats['num_item_generated']}")
print(f"Source discarded {SRC1.stats['num_item_discarded']}")
print(f"Machine {MACHINE4.id} state times: {MACHINE4.stats}")

print(f"Time-average number of items in  {BUF1.id} is {BUF1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF2.id} is {BUF2.stats['time_averaged_num_of_items_in_buffer']}")


print(f"Sink {SINK1.id} received {SINK1.stats['num_item_received']} items.")


print(MACHINE4.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", MACHINE4.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",MACHINE4.per_thread_total_time_in_blocked_state)
