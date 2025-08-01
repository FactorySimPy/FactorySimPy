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


MACHINE4 = Machine(env, id="MACHINE4",work_capacity=3,blocking=True, processing_delay=0.5,in_edge_selection="ROUND_ROBIN",out_edge_selection=0)
MACHINE5 = Machine(env, id="MACHINE5",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection=0,out_edge_selection=0)

SINK1= Sink(env, id="SINK1")










# Initializing edges
# Initializing edges
BUF1 = Buffer(env, id="BUF1", capacity=1, delay=0)
BUF2 = Buffer(env, id="BUF2", capacity=1, delay=0)
BUF3 = Buffer(env, id="BUF3", capacity=1, delay=2)
BUF4 = Buffer(env, id="BUF4", capacity=1, delay=2)
BUF5 = Buffer(env, id="BUF5", capacity=1, delay=0)
BUF6 = Buffer(env, id="BUF6", capacity=1, delay=0)
BUF7 = Buffer(env, id="BUF7", capacity=1, delay=0)
BUF8 = Buffer(env, id="BUF8", capacity=1, delay=0)


# Adding connections
BUF1.connect(SRC1,MACHINE1)
BUF2.connect(SRC2,MACHINE2)
BUF3.connect(SRC3,MACHINE3)

BUF4.connect(MACHINE1,MACHINE4)
BUF5.connect(MACHINE2,MACHINE4)
BUF6.connect(MACHINE3,MACHINE4)
BUF7.connect(MACHINE4,MACHINE5)
BUF8.connect(MACHINE5,SINK1)




time=100
env.run(until=time)
SRC1.update_final_state_time(time)
SRC2.update_final_state_time(time)
SRC3.update_final_state_time(time)
MACHINE1.update_final_state_time(time)
MACHINE2.update_final_state_time(time)
MACHINE3.update_final_state_time(time)
MACHINE4.update_final_state_time(time)
MACHINE5.update_final_state_time(time)
SINK1.update_final_state_time(time)
print("Simulation completed.")
# Print statistics

print(f"Source {SRC1.id} state times: {SRC1.stats}")
print(f"Source {SRC2.id} state times: {SRC2.stats}")
print(f"Source {SRC3.id} state times: {SRC3.stats}")

print(f"Machine {MACHINE1.id} state times: {MACHINE1.stats}")
print(f"Machine {MACHINE2.id} state times: {MACHINE2.stats}")
print(f"Machine {MACHINE3.id} state times: {MACHINE3.stats}")
print(f"Machine {MACHINE4.id} state times: {MACHINE4.stats}")
print(f"Machine {MACHINE5.id} state times: {MACHINE5.stats}")


print(f"Time-average number of items in  {BUF1.id} is {BUF1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF2.id} is {BUF2.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF3.id} is {BUF3.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF4.id} is {BUF4.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF5.id} is {BUF5.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF6.id} is {BUF6.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF7.id} is {BUF7.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF8.id} is {BUF8.stats['time_averaged_num_of_items_in_buffer']}")


print(f"Sink {SINK1.id} received {SINK1.stats['num_item_received']} items.")

print(f"MACHINE {MACHINE1.id}")
print(MACHINE1.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", MACHINE1.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",MACHINE1.per_thread_total_time_in_blocked_state)

print(f"MACHINE {MACHINE2.id}")
print(MACHINE2.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", MACHINE2.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",MACHINE2.per_thread_total_time_in_blocked_state)

print(f"MACHINE {MACHINE3.id}")
print(MACHINE3.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", MACHINE3.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",MACHINE3.per_thread_total_time_in_blocked_state)

print(f"MACHINE {MACHINE4.id}")
print(MACHINE4.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", MACHINE4.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",MACHINE4.per_thread_total_time_in_blocked_state)

print(f"MACHINE {MACHINE5.id}")
print(MACHINE5.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", MACHINE5.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",MACHINE5.per_thread_total_time_in_blocked_state)


print(f"Sink {SINK1.id} state times: {SINK1.stats}")
print(f"Throuphput:{SINK1.stats['num_item_received']/env.now}")
tot_cycletime = SINK1.stats["total_cycle_time"]
tot_items = SINK1.stats["num_item_received"]
print(f"Cycletime, {tot_cycletime/tot_items if tot_items > 0 else 0}")