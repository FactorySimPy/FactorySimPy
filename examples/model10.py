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

##  SRC1 ──> BUFFER1 ──┐
#                      │
#   SRC2 ──> BUFFER2 ──┴─> MACHINE1 ───> BUFFER3───> MACHINE2 ──┬─> BUFFER4 ──> MACHINE3 ───> BUFFER8───>SINK1
#                                                               │
#                                                               └─> BUFFER5 ──> MACHINE4 ───> BUFFER9───>SINK2
#                                                               │
#                                                               └─> BUFFER6 ──> MACHINE5 ───> BUFFER10───>SINK3                                         
#                                                               │
#                                                               └─> BUFFER7 ──> MACHINE6 ───> BUFFER11───>SINK4


env = simpy.Environment()


    





# Initializing nodes
SRC1= Source(env, id="SRC1",  inter_arrival_time=0.5,blocking=True, out_edge_selection="FIRST_AVAILABLE" )
SRC2= Source(env, id="SRC2",  inter_arrival_time=0.2,blocking=True, out_edge_selection="FIRST_AVAILABLE")
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=1,blocking=True, processing_delay=0.41,in_edge_selection="ROUND_ROBIN",out_edge_selection="FIRST_AVAILABLE")
MACHINE2 = Machine(env, id="MACHINE2",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="ROUND_ROBIN")
MACHINE3 = Machine(env, id="MACHINE3",work_capacity=1,blocking=True, processing_delay=0.6,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE")
MACHINE4 = Machine(env, id="MACHINE4",work_capacity=1,blocking=True, processing_delay=0.2,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE")
MACHINE5 = Machine(env, id="MACHINE5",work_capacity=1,blocking=True, processing_delay=0.5,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE")
MACHINE6 = Machine(env, id="MACHINE6",work_capacity=1,blocking=True, processing_delay=0.4,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE")
SINK1= Sink(env, id="SINK1")
SINK2= Sink(env, id="SINK2")
SINK3= Sink(env, id="SINK3")
SINK4= Sink(env, id="SINK4")


# Initializing edges
BUF1 = Buffer(env, id="BUF1", capacity=1, delay=0)
BUF2 = Buffer(env, id="BUF2", capacity=1, delay=0)
BUF3 = Buffer(env, id="BUF3", capacity=1, delay=0)
BUF4 = Buffer(env, id="BUF4", capacity=1, delay=0)
BUF5 = Buffer(env, id="BUF5", capacity=1, delay=0)
BUF6 = Buffer(env, id="BUF6", capacity=1, delay=0)
BUF7 = Buffer(env, id="BUF7", capacity=1, delay=0)
BUF8 = Buffer(env, id="BUF8", capacity=1, delay=0)
BUF9 = Buffer(env, id="BUF9", capacity=1, delay=0)
BUF10 = Buffer(env, id="BUF10", capacity=1, delay=0)
BUF11 = Buffer(env, id="BUF11", capacity=1, delay=0)


# Adding connections
BUF1.connect(SRC1,MACHINE1)
BUF2.connect(SRC2,MACHINE1)
BUF3.connect(MACHINE1,MACHINE2)
BUF8.connect(MACHINE2,MACHINE6)
BUF9.connect(MACHINE2,MACHINE5)
BUF10.connect(MACHINE2,MACHINE4)
BUF11.connect(MACHINE2,MACHINE3)
BUF4.connect(MACHINE6,SINK1)
BUF5.connect(MACHINE5,SINK2)
BUF6.connect(MACHINE4,SINK3)
BUF7.connect(MACHINE3,SINK4)

time=100
env.run(until=time)
SOURCES=[SRC1,SRC2]
BUFFERS=[BUF1,BUF2,BUF3,BUF4,BUF5,BUF6,BUF7,BUF8,BUF9,BUF10,BUF11]
SINKS=[SINK1,SINK2,SINK3,SINK4]
MACHINES= [MACHINE1, MACHINE2, MACHINE3, MACHINE4, MACHINE5, MACHINE6]

SRC1.update_final_state_time(time)
SRC2.update_final_state_time(time)
for machine in MACHINES:
    machine.update_final_state_time(time)
for buffer in BUFFERS:
    buffer.update_final_buffer_avg_content(time)
for sink in SINKS:
    sink.update_final_state_time(time)

print("Simulation completed.")

# with open('model_outputs\model10.csv', 'w', newline='') as f:
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
print(f"Source1 generated {SRC1.stats['num_item_generated']}")

print(f"Source2 generated {SRC2.stats['num_item_generated']}")




print(f"Time-average number of items in  {BUF1.id} is {BUF1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF2.id} is {BUF2.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF3.id} is {BUF3.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF4.id} is {BUF4.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF5.id} is {BUF5.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF6.id} is {BUF6.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF7.id} is {BUF7.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF8.id} is {BUF8.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF9.id} is {BUF9.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF10.id} is {BUF10.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF11.id} is {BUF11.stats['time_averaged_num_of_items_in_buffer']}")

print(f"Sink {SINK1.id} received {SINK1.stats['num_item_received']} items.")
print(f"Sink {SINK2.id} received {SINK2.stats['num_item_received']} items.")
print(f"Sink {SINK3.id} received {SINK3.stats['num_item_received']} items.")
print(f"Sink {SINK4.id} received {SINK4.stats['num_item_received']} items.")


tot_cycletime = SINK1.stats["total_cycle_time"]+ SINK2.stats["total_cycle_time"] + SINK3.stats["total_cycle_time"]+ SINK4.stats["total_cycle_time"]  
tot_items = SINK1.stats["num_item_received"]+SINK2.stats["num_item_received"] + SINK3.stats["num_item_received"]+SINK4.stats["num_item_received"]
print(f"Cycletime, {tot_cycletime/tot_items if tot_items > 0 else 0}")
print(f"Throuphput:{tot_items/env.now}")


for machine in MACHINES:
    print("\n" )
    print(f"Machine {machine.id} state times: {machine.stats}")
    print(machine.time_per_work_occupancy)
    print("per_thread_total_time_in_processing_state", machine.per_thread_total_time_in_processing_state)
    print("per_thread_total_time_in_blocked_state", machine.per_thread_total_time_in_blocked_state)
    print("total_items processed", machine.stats["num_item_processed"])