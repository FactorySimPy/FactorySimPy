
import simpy,sys, os
import scipy.stats


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
import random

#SRC ──> BUF1 ──> MACHINE1 ──┬─> BUF2 ──> MACHINE2 ──> BUF4 ──> SINK1
#                            └─> BUF3 ──> MACHINE3 ──> BUF5 ──> SINK2



env = simpy.Environment()

def generate_gaussian_distribution(mean=0, std_dev=1):
   
    return random.gauss(mu=mean,sigma= std_dev)


# Initializing nodes
SRC= Source(env, id="SRC",  inter_arrival_time=generate_gaussian_distribution(0.4,0.02),blocking=True, out_edge_selection=0 )

#src= Source(env, id="Source-1",  inter_arrival_time=0.2,blocking=True,out_edge_selection=0 )
MACHINE1 = Machine(env, id="MACHINE1",node_setup_time=0,work_capacity=2,blocking=True, processing_delay=0.9,in_edge_selection=0,out_edge_selection="ROUND_ROBIN")
MACHINE2 = Machine(env, id="MACHINE2",node_setup_time=0,work_capacity=1,blocking=True, processing_delay=3.2,in_edge_selection="RANDOM",out_edge_selection="FIRST_AVAILABLE")
MACHINE3 = Machine(env, id="MACHINE3",node_setup_time=0,work_capacity=1,blocking=True, processing_delay=2.54,in_edge_selection="FIRST_AVAILABLE",out_edge_selection=0)
SINK= Sink(env, id="SINK")

# Initializing edges
BUFFER1 = Buffer(env, id="BUFFER1", store_capacity=2, delay=1, mode="FIFO")

BUFFER2 = Buffer(env, id="BUFFER2", store_capacity=3, delay=0, mode="FIFO")
BUFFER3 = Buffer(env, id="BUFFER3", store_capacity=3, delay=0, mode="LIFO")

BUFFER4 = Buffer(env, id="BUFFER4", store_capacity=1, delay=0, mode="FIFO")
BUFFER5 = Buffer(env, id="BUFFER5", store_capacity=1, delay=0, mode="FIFO")
# Adding connections
BUFFER1.connect(SRC,MACHINE1)
BUFFER2.connect(MACHINE1,MACHINE2)
BUFFER3.connect(MACHINE1,MACHINE3)
BUFFER4.connect(MACHINE2,SINK)
BUFFER5.connect(MACHINE3,SINK)



env.run(until=100)
print("Simulation completed.")
# Print statistics

print(f"Machine {MACHINE1.id} state times: {MACHINE1.stats}")

print(f"Time-average number of items in  {BUFFER1.id} is {BUFFER1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER2.id} is {BUFFER2.stats['time_averaged_num_of_items_in_buffer']}")


print(f"Sink {SINK.id} received {SINK.stats['num_item_received']} items.")

print(MACHINE1.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", MACHINE1.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",MACHINE1.per_thread_total_time_in_blocked_state)
