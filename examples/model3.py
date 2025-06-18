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

##  SRC1 ──> BUFFER1 ──┐
#                      │
#   SRC2 ──> BUFFER2 ──┴─> MACHINE1 ──┬─> BUFFER3 ──> SINK1
#      │                              │
#      └─> BUFFER5 ──> SINK3          └─> BUFFER4 ──> SINK2
#                                         



env = simpy.Environment()


    





# Initializing nodes
SRC1= Source(env, id="SRC1",  inter_arrival_time=0.2,blocking=True, out_edge_selection="FIRST_AVAILABLE" )
SRC2= Source(env, id="SRC2",  inter_arrival_time=0.2,blocking=True, out_edge_selection=0)
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection=0,out_edge_selection=0)
SINK1= Sink(env, id="SINK1")
SINK2= Sink(env, id="SINK2")
SINK3= Sink(env, id="SINK3")







# Initializing edges
# Initializing edges
BUF1 = Buffer(env, id="BUF1", store_capacity=2, delay=0)
BUF2 = Buffer(env, id="BUF2", store_capacity=1, delay=0)
BUF3 = Buffer(env, id="BUF3", store_capacity=1, delay=2)
BUF4 = Buffer(env, id="BUF4", store_capacity=1, delay=2)
BUF5 = Buffer(env, id="BUF5", store_capacity=1, delay=0)




# Adding connections
BUF1.connect(SRC1,MACHINE1)
BUF2.connect(SRC2,MACHINE1)
BUF3.connect(MACHINE1,SINK1)
BUF4.connect(MACHINE1,SINK2)
BUF5.connect(SRC2,SINK3)



env.run(until=10)
print("Simulation completed.")
# Print statistics
print(f"Source generated {SRC1.stats['num_item_generated']}")
print(f"Source discarded {SRC1.stats['num_item_discarded']}")
print(f"Machine {MACHINE1.id} state times: {MACHINE1.stats}")

print(f"Time-average number of items in  {BUF1.id} is {BUF1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF2.id} is {BUF2.stats['time_averaged_num_of_items_in_buffer']}")


print(f"Sink {SINK1.id} received {SINK1.stats['num_item_received']} items.")
print(f"Sink {SINK2.id} received {SINK2.stats['num_item_received']} items.")
print(f"Sink {SINK3.id} received {SINK3.stats['num_item_received']} items.")


print(MACHINE1.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", MACHINE1.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",MACHINE1.per_thread_total_time_in_blocked_state)
