import simpy,sys, os
import scipy.stats


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
import random

#SRC ──> BUF1 ──> MACHINE1 ───> BUF2 ──>SINK
                        



env = simpy.Environment()



# Initializing nodes
SRC= Source(env, id="SRC",  inter_arrival_time=0.2,blocking=True, out_edge_selection=0 )

#src= Source(env, id="Source-1",  inter_arrival_time=0.2,blocking=True,out_edge_selection=0 )
MACHINE1 = Machine(env, id="MACHINE1",node_setup_time=0,work_capacity=2,blocking=True, processing_delay=0.5,in_edge_selection=0,out_edge_selection="ROUND_ROBIN")

MACHINE2 = Machine(env, id="MACHINE2",node_setup_time=0,work_capacity=1,blocking=True, processing_delay=3,in_edge_selection=0,out_edge_selection="ROUND_ROBIN")
SINK= Sink(env, id="SINK")

# Initializing edges
BUFFER1 = Buffer(env, id="BUFFER1", capacity=5, delay=0, mode="FIFO")

BUFFER2 = Buffer(env, id="BUFFER2", capacity=1, delay=0, mode="FIFO")

BUFFER3 = Buffer(env, id="BUFFER3", capacity=5, delay=0, mode="FIFO")
# Adding connections
BUFFER1.connect(SRC,MACHINE1)
BUFFER2.connect(MACHINE1,MACHINE2)
BUFFER3.connect(MACHINE2,SINK)



time=10
env.run(until=time)
SRC.update_final_state_time(time)
print(MACHINE1.state)
#MACHINE1.check_thread_state_and_update_machine_state()
MACHINE1.update_final_state_time(time)
BUFFER1.update_final_buffer_avg_content(time)
BUFFER2.update_final_buffer_avg_content(time)   
SINK.update_final_state_time(time)


print("Simulation completed.")
# Print statistics
print(f"SRC {SRC.id} stats: {SRC.stats}")
print(f"SINK {SINK.id} stats: {SINK.stats}")
#print(f"Machine1 {MACHINE1.id} state times: {MACHINE1.stats}")

print(f"Time-average number of items in  {BUFFER1.id} is {BUFFER1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUFFER2.id} is {BUFFER2.stats['time_averaged_num_of_items_in_buffer']}")



print(f"Sink {SINK.id} received {SINK.stats['num_item_received']} items.")

print(f"Throuphput:{SINK.stats['num_item_received']/env.now}")
tot_cycletime = SINK.stats["total_cycle_time"]
tot_items = SINK.stats["num_item_received"]
print(f"Cycletime, {tot_cycletime/tot_items if tot_items > 0 else 0}")


print(f"Sink {SINK.id} received {SINK.stats['num_item_received']} items.")

import numpy as np

print("Machine1",np.array(MACHINE1.time_per_work_occupancy)/env.now)
for i in MACHINE1.stats['total_time_spent_in_states']:
    print(f"Machine1 {MACHINE1.id} state times: {i} - {MACHINE1.stats['total_time_spent_in_states'][i]/time}")

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

buffers = [BUFFER1, BUFFER2]

metric.append("Time avg content in buffers  ")
model.append("---")
for buf in buffers:
    metric.append(buf.id)
    print(f"Time-average number of items in  {buf.id} is {buf.stats['time_averaged_num_of_items_in_buffer']}")
    model.append(buf.stats['time_averaged_num_of_items_in_buffer'])



print(f"SRC {SRC.id} state times: {SRC.stats}")

import pandas as pd




stats_list=[metric, model]
stats_rows = list(zip(*stats_list))
# Create DataFrame and save to CSV
stats_df = pd.DataFrame(stats_rows, columns=["Metric", "Model"])
stats_df.to_csv("machine_model1_stats_ref.csv", index=False)