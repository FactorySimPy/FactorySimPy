# to test buffers blocking behavior of buffer

import simpy,sys, os
import scipy.stats
import csv
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
import random

#   SRC1 ──> BUFFER1 ──> MACHINE1 ──>BUFFER4──────┬         
#                                                 │ 
#   SRC2 ──> BUFFER2 ───> MACHINE2───>BUFFER5───>MACHINE4 ───> BUFFER7 ───>MACHINE5 ───> BUFFER8 ──> SINK1
#                                                     │
#  MACHINE5 ──> BUFFER3 ───> MACHINE3 ───>BUFFER6   ──┘         


env = simpy.Environment()

# Initializing nodes
SRC1= Source(env, id="SRC1",  inter_arrival_time=0.2,blocking=True, out_edge_selection="FIRST_AVAILABLE" )
SRC2= Source(env, id="SRC2",  inter_arrival_time=0.2,blocking=True, out_edge_selection="FIRST_AVAILABLE" )


MACHINE1 = Machine(env, id="MACHINE1",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE")
MACHINE2 = Machine(env, id="MACHINE2",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE")
MACHINE3 = Machine(env, id="MACHINE3",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE")


MACHINE4 = Machine(env, id="MACHINE4",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection="ROUND_ROBIN",out_edge_selection="FIRST_AVAILABLE")
MACHINE5 = Machine(env, id="MACHINE5",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE")

SINK= Sink(env, id="SINK")


# Initializing edges
BUF1 = Buffer(env, id="BUF1", capacity=1, delay=0)
BUF2 = Buffer(env, id="BUF2", capacity=1, delay=0)
BUF3 = Buffer(env, id="BUF3", capacity=1, delay=0)
BUF4 = Buffer(env, id="BUF4", capacity=1, delay=0)
BUF5 = Buffer(env, id="BUF5", capacity=1, delay=0)
BUF6 = Buffer(env, id="BUF6", capacity=1, delay=0)
BUF7 = Buffer(env, id="BUF7", capacity=1, delay=0)
BUF8 = Buffer(env, id="BUF8", capacity=1, delay=3)


# Adding connections
BUF1.connect(SRC1,MACHINE1)
BUF2.connect(SRC2,MACHINE2)
BUF3.connect(MACHINE5,MACHINE3)
BUF4.connect(MACHINE1,MACHINE4)
BUF5.connect(MACHINE2,MACHINE4)
BUF6.connect(MACHINE3,MACHINE4)
BUF7.connect(MACHINE4,MACHINE5)
BUF8.connect(MACHINE5,SINK)

time=100
env.run(until=time)
print("Simulation completed.")

SOURCES=[SRC1,SRC2]
MACHINES=[MACHINE1,MACHINE2,MACHINE3,MACHINE4,MACHINE5]
BUFFERS=[BUF1,BUF2,BUF3,BUF4,BUF5,BUF6,BUF7,BUF8]
SINKS=[SINK]

for source in SOURCES:
    source.update_final_state_time(time)
for machine in MACHINES:
    machine.update_final_state_time(time)
for buffer in BUFFERS:
    buffer.update_final_buffer_avg_content(time)
for sink in SINKS:
    sink.update_final_state_time(time)

# with open('model_outputs\model6.csv', 'w', newline='') as f:
#     writer = csv.writer(f)
#     tot_cycletime=0
#     tot_items=0
#     for sink in SINKS:
#         tot_cycletime += sink.stats["total_cycle_time"]
#         tot_items += sink.stats["num_item_received"]
#     cycletime= tot_cycletime/tot_items if tot_items > 0 else 0
#     throughput= tot_items/env.now
#     writer.writerow([throughput])
#     writer.writerow([cycletime])
    
#     for buffer in BUFFERS:
#         writer.writerow([buffer.stats['time_averaged_num_of_items_in_buffer']])

#     for machine in MACHINES:
#         writer.writerow([machine.stats['total_time_spent_in_states']['IDLE_STATE']])
#         writer.writerow([machine.stats['total_time_spent_in_states']['PROCESSING_STATE']])
#         writer.writerow([machine.stats['total_time_spent_in_states']['BLOCKED_STATE']])
#         writer.writerow([machine.per_thread_total_time_in_processing_state])
#         writer.writerow([machine.per_thread_total_time_in_blocked_state])
#         writer.writerow([machine.time_per_work_occupancy])

#     for source in SOURCES:
#         writer.writerow([source.stats['num_item_generated']])
#         writer.writerow([source.stats['total_time_spent_in_states']['GENERATING_STATE']])
#         writer.writerow([source.stats['total_time_spent_in_states']['BLOCKED_STATE']])

#     for sink in SINKS:
#         writer.writerow([sink.stats['num_item_received']])


# Print statistics
print(f"Source generated {SRC1.stats['num_item_generated']}")
print(f"Total items generated {SRC1.stats['num_item_generated'] + SRC2.stats['num_item_generated'] }")

print(f"Time-average number of items in  {BUF1.id} is {BUF1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF2.id} is {BUF2.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF3.id} is {BUF3.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF4.id} is {BUF4.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF5.id} is {BUF5.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF6.id} is {BUF6.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF7.id} is {BUF7.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF8.id} is {BUF8.stats['time_averaged_num_of_items_in_buffer']}")

print(f"Sink {SINK.id} received {SINK.stats['num_item_received']} items.")

print(f"Throuphput:{SINK.stats['num_item_received']/env.now}")
tot_cycletime = SINK.stats["total_cycle_time"]
tot_items = SINK.stats["num_item_received"]
print(f"Cycletime, {tot_cycletime/tot_items if tot_items > 0 else 0}")


machines= [MACHINE1, MACHINE2, MACHINE3, MACHINE4, MACHINE5]
for machine in machines:
    print("/" * 20)
    print(f"Machine {machine.id} state times: {machine.stats}")
    print(machine.time_per_work_occupancy)
    print("per_thread_total_time_in_processing_state", machine.per_thread_total_time_in_processing_state)
    print("per_thread_total_time_in_blocked_state", machine.per_thread_total_time_in_blocked_state)
    print("total_time_in_processing_state", machine.stats["num_item_processed"])