import simpy,sys, os
import scipy.stats


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.edges.continuous_conveyor import ConveyorBelt

from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
import random

#SRC ──> BUF1 ──> MACHINE1 ───> BUF2 ──>SINK
                        



env = simpy.Environment()



# Initializing nodes
SRC1= Source(env, id="SRC1",  inter_arrival_time=0.2,blocking=True, out_edge_selection=0 )
SRC2= Source(env, id="SRC2",  inter_arrival_time=0.3,blocking=True, out_edge_selection=0 )
SRC3= Source(env, id="SRC3",  inter_arrival_time=0.2,blocking=True, out_edge_selection=0 )

#src= Source(env, id="Source-1",  inter_arrival_time=0.2,blocking=True,out_edge_selection=0 )
CONVEYORBELT= ConveyorBelt(env, id="CONVEYORBELT1", capacity=5, speed=1, length=1, accumulating=0)
MACHINE3 = Machine(env, id="MACHINE3", node_setup_time=0, work_capacity=1, blocking=True, processing_delay=.5, in_edge_selection="ROUND_ROBIN", out_edge_selection="FIRST_AVAILABLE")
SINK= Sink(env, id="SINK")
#SPLITTER= Splitter(env, id="Splitter1", node_setup_time=0, blocking=True, processing_delay=0.5, in_edge_selection="FIRST_AVAILABLE", out_edge_selection="ROUND_ROBIN")
MACHINE1 = Machine(env, id="MACHINE1", node_setup_time=0, work_capacity=1, blocking=True, processing_delay=5, in_edge_selection="ROUND_ROBIN", out_edge_selection="FIRST_AVAILABLE")
MACHINE2 = Machine(env, id="MACHINE2", node_setup_time=0, work_capacity=1, blocking=True, processing_delay=0.5, in_edge_selection="ROUND_ROBIN", out_edge_selection="FIRST_AVAILABLE")

# Initializing edges
BUFFER1 = Buffer(env, id="BUFFER1", capacity=5, delay=0, mode="FIFO")
BUFFER2 = Buffer(env, id="BUFFER2", capacity=5, delay=0, mode="FIFO")

BUFFER4 = Buffer(env, id="BUFFER4", capacity=5, delay=0, mode="FIFO")
BUFFER5 = Buffer(env, id="BUFFER5", capacity=5, delay=0, mode="FIFO")
BUFFER6 = Buffer(env, id="BUFFER6", capacity=5, delay=0, mode="FIFO")
BUFFER7 = Buffer(env, id="BUFFER7", capacity=5, delay=0, mode="FIFO")

# Adding connections
BUFFER1.connect(SRC1,MACHINE3)
BUFFER2.connect(SRC2,MACHINE3)
CONVEYORBELT.connect(MACHINE3,MACHINE1)
BUFFER4.connect(MACHINE1,MACHINE2)

BUFFER7.connect(SRC3,MACHINE2)

BUFFER6.connect(MACHINE2,MACHINE1)
BUFFER5.connect(MACHINE2,SINK)


time=1000
env.run(until=time)
print("BUFFER1 items", BUFFER1.get_occupancy())
print("BUFFER2 items", BUFFER2.get_occupancy())
#print("BUFFER3 items", BUFFER3.get_occupancy())
print("BUFFER4 items", BUFFER4.get_occupancy())

SRC1.update_final_state_time(time)
MACHINE3.update_final_state_time(time)
BUFFER1.update_final_buffer_avg_content(time)
BUFFER2.update_final_buffer_avg_content(time)
CONVEYORBELT.update_final_conveyor_avg_content(time)
BUFFER4.update_final_buffer_avg_content(time)
BUFFER5.update_final_buffer_avg_content(time)
BUFFER6.update_final_buffer_avg_content(time)
BUFFER7.update_final_buffer_avg_content(time)
SINK.update_final_state_time(time)


print("Simulation completed.")
# Print statistics
print(f"SRC {SRC1.id} stats: {SRC1.stats}")
print(f"SINK {SINK.id} stats: {SINK.stats}")
#print(f"Machine1 {MACHINE1.id} state times: {MACHINE1.stats}")

print(f"Time-average number of items in  {BUFFER1.id} is {BUFFER1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER2.id} is {BUFFER2.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {CONVEYORBELT.id} is {CONVEYORBELT.stats['time_averaged_num_of_items_in_conveyor']}")
print(f"Time-average number of items in  {BUFFER4.id} is {BUFFER4.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER5.id} is {BUFFER5.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER6.id} is {BUFFER6.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER7.id} is {BUFFER7.stats['time_averaged_num_of_items_in_buffer']}")


print(f"Sink {SINK.id} received {SINK.stats['num_item_received']} items.")

print(f"Throuphput:{SINK.stats['num_item_received']/env.now}")
tot_cycletime = SINK.stats["total_cycle_time"]
tot_items = SINK.stats["num_item_received"]
print(f"Cycletime, {tot_cycletime/tot_items if tot_items > 0 else 0}")


print(f"Sink {SINK.id} received {SINK.stats['num_item_received']} items.")

import numpy as np

print("Machine1",np.array(MACHINE1.time_per_work_occupancy)/env.now)
print("per_thread_total_time_in_processing_state:MACHINE1", MACHINE1.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state:MACHINE1",MACHINE1.per_thread_total_time_in_blocked_state)

print(f"Machine1 {MACHINE1.id} state times: {MACHINE1.stats}")

machines =[MACHINE1]

metric=[]
model=[]
metric.append("Simulation time (sec)")
model.append(env.now)
metric.append("Cycle time (sec)")
model.append(tot_cycletime/tot_items if tot_items > 0 else 0) 
metric.append("Throughput (items/sec)")
model.append(SINK.stats['num_item_received'] / env.now) 

metric.append("Utilization")
model.append("---")

for machine in machines:
    print("\n" )
    print(f"Machine {machine.id} state times: {machine.stats['total_time_spent_in_states']}")
    for i in machine.stats['total_time_spent_in_states']:
        metric.append(f"{machine.id} - {i}")
        model.append(machine.stats['total_time_spent_in_states'][i])
    if machine.time_per_work_occupancy:
        for i in range(len(machine.time_per_work_occupancy)):
            metric.append(f"{machine.id}- with {i} worker threads")
            model.append(machine.time_per_work_occupancy[i])
    print(machine.time_per_work_occupancy)
    #print(machine.stats['in_edge_selection'],machine.stats['out_edge_selection'])
    print("per_thread_total_time_in_processing_state", machine.per_thread_total_time_in_processing_state)
    print("per_thread_total_time_in_blocked_state", machine.per_thread_total_time_in_blocked_state)
    print("total_items_processed", machine.stats["num_item_processed"])

buffers = [BUFFER1, BUFFER2, BUFFER4, BUFFER5, BUFFER6, BUFFER7]

metric.append("Time avg content in buffers  ")
model.append("---")
for buf in buffers:
    metric.append(buf.id)
    print(f"Time-average number of items in  {buf.id} is {buf.stats['time_averaged_num_of_items_in_buffer']}")
    model.append(buf.stats['time_averaged_num_of_items_in_buffer'])
metric.append("Time avg content in CONVEYORBELT  ")
metric.append(CONVEYORBELT.id)
print(f"Time-average number of items in  {CONVEYORBELT.id} is {CONVEYORBELT.stats['time_averaged_num_of_items_in_conveyor']}")
model.append(CONVEYORBELT.stats['time_averaged_num_of_items_in_conveyor'])



print(f"SRC {SRC2.id} state times: {SRC2.stats}")

import pandas as pd




stats_list=[metric, model]
stats_rows = list(zip(*stats_list))
# Create DataFrame and save to CSV
stats_df = pd.DataFrame(stats_rows, columns=["Metric", "Model"])
stats_df.to_csv("machine_model_conveyor_stats_ref_acc_0_6.csv", index=False)