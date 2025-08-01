import simpy,sys, os
import scipy.stats


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
import random

env = simpy.Environment()



# Initializing nodes
SRC= Source(env, id="SRC",  inter_arrival_time=0,blocking=True, out_edge_selection="FIRST_AVAILABLE")
BUFFER1 = Buffer(env, id="BUFFER1", capacity=2, delay=0, mode="FIFO")
MACHINE1 = Machine(env, id="MACHINE1",node_setup_time=0,work_capacity=2,blocking=True, processing_delay=0.5,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE")
BUFFER2 = Buffer(env, id="BUFFER2", capacity=1, delay=1, mode="FIFO")
SINK= Sink(env, id="SINK")

BUFFER1.connect(SRC,MACHINE1)
BUFFER2.connect(MACHINE1,SINK)

time=2
env.run(until=time)
SRC.update_final_state_time(time)
MACHINE1.update_final_state_time(time)
SINK.update_final_state_time(time)

print("Simulation completed.")
# Print statistics
print(f"SRC {SRC.id} stats: {SRC.stats}")
print(f"Machine1 {MACHINE1.id} state times: {MACHINE1.stats}")
print(f"SINK {SINK.id} stats: {SINK.stats}")

print(f"Time-average number of items in  {BUFFER1.id} is {BUFFER1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER2.id} is {BUFFER2.stats['time_averaged_num_of_items_in_buffer']}")

print(f"Throuphput:{SINK.stats['num_item_received']/env.now}")
tot_cycletime = SINK.stats["total_cycle_time"]
tot_items = SINK.stats["num_item_received"]
print(f"Cycletime, {tot_cycletime/tot_items if tot_items > 0 else 0}")


print(f"Sink {SINK.id} received {SINK.stats['num_item_received']} items.")

print(f"Buffer {BUFFER1.id} stats: {BUFFER1.stats}")
print(f"Buffer {BUFFER2.id} stats: {BUFFER2.stats}")
