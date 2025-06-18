
import simpy,sys, os
import scipy.stats


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


#SRC1 ──> BUF1 ──┐
#                ├─> MACHINE1 ──> BUF3 ──> SINK
#SRC2 ──> BUF2 ──┘


env = simpy.Environment()


# Initializing nodes
SRC1= Source(env, id="SRC1",  inter_arrival_time=1,blocking=True, out_edge_selection=0 )
SRC2= Source(env, id="SRC2",  inter_arrival_time=1,blocking=True, out_edge_selection=0)
#src= Source(env, id="Source-1",  inter_arrival_time=0.2,blocking=True,out_edge_selection=0 )
MACHINE1 = Machine(env, id="MACHINE1",node_setup_time=0,work_capacity=2,blocking=True, processing_delay=1,in_edge_selection="ROUND_ROBIN",out_edge_selection=0)

SINK= Sink(env, id="SINK")

# Initializing edges
BUFFER1 = Buffer(env, id="BUFFER1", store_capacity=5, delay=0.5, mode="FIFO")
BUFFER2 = Buffer(env, id="BUFFER2", store_capacity=5, delay=0.5, mode="FIFO")
BUFFER3 = Buffer(env, id="BUFFER3", store_capacity=1, delay=0.5, mode="FIFO")
# Adding connections
BUFFER1.connect(SRC1, MACHINE1)
BUFFER2.connect(SRC2, MACHINE1)
BUFFER3.connect(MACHINE1, SINK)




env.run(until=100)

print("Simulation completed.")
# Print statistics

print(f"Machine {MACHINE1.id} state times: {MACHINE1.stats}")

print(f"Time-average number of items in  {BUFFER1.id} is {BUFFER1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER2.id} is {BUFFER2.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER3.id} is {BUFFER3.stats['time_averaged_num_of_items_in_buffer']}")


print(f"Sink {SINK.id} received {SINK.stats['num_item_received']} items.")

print(f"Throuphput:{SINK.stats['num_item_received']/env.now}")
tot_cycletime = SINK.stats["total_cycle_time"]
tot_items = SINK.stats["num_item_received"]
print(f"Cycletime, {tot_cycletime/tot_items if tot_items > 0 else 0}")

print(MACHINE1.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", MACHINE1.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",MACHINE1.per_thread_total_time_in_blocked_state)
