
import simpy,sys, os
import scipy.stats


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
import random

#SRC ──> BUF1 ──> MACHINE1 ──┬─> BUF2 ──> MACHINE2 ──> BUF4 ──> SINK
#                            └─> BUF3 ──> MACHINE3 ──> BUF5 ──> SINK



env = simpy.Environment()



# Initializing nodes
SRC= Source(env, id="SRC",  inter_arrival_time=0.46,blocking=True, out_edge_selection=0 )

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

print(f"Machine1 {MACHINE1.id} state times: {MACHINE1.stats}")

print(f"Time-average number of items in  {BUFFER1.id} is {BUFFER1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER2.id} is {BUFFER2.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER3.id} is {BUFFER3.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER4.id} is {BUFFER4.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER5.id} is {BUFFER5.stats['time_averaged_num_of_items_in_buffer']}")


print(f"Sink {SINK.id} received {SINK.stats['num_item_received']} items.")

print(f"Throuphput:{SINK.stats['num_item_received']/env.now}")
tot_cycletime = SINK.stats["total_cycle_time"]
tot_items = SINK.stats["num_item_received"]
print(f"Cycletime, {tot_cycletime/tot_items if tot_items > 0 else 0}")


print(f"Sink {SINK.id} received {SINK.stats['num_item_received']} items.")

machines = [MACHINE1, MACHINE2, MACHINE3]

for machine in machines:
    print("\n" )
    print(f"Machine {machine.id} state times: {machine.stats}")
    print(machine.time_per_work_occupancy)
    print("per_thread_total_time_in_processing_state", machine.per_thread_total_time_in_processing_state)
    print("per_thread_total_time_in_blocked_state", machine.per_thread_total_time_in_blocked_state)
    print("total_time_in_processing_state", machine.stats["num_item_processed"])