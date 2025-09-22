
import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


env = simpy.Environment()

def distribution_generator(loc=4.0, scale=5.0, size=1):
    while True:
        delay = scipy.stats.expon.rvs(loc=0.0,scale=0.5,size=1)
        yield delay[0]

# Initializing nodes
src= Source(env, id="Source-1",  inter_arrival_time=5,blocking=True, out_edge_selection="FIRST_AVAILABLE" )
#src= Source(env, id="Source-1",  inter_arrival_time=0.2,blocking=True,out_edge_selection=0 )
m1 = Machine(env, id="M1",node_setup_time=0,work_capacity=1, processing_delay=2,in_edge_selection="FIRST_AVAILABLE",out_edge_selection="FIRST_AVAILABLE")

sink= Sink(env, id="Sink-1")

# Initializing edges
buffer1 = Buffer(env, id="Buffer-1", capacity=4, delay=0, mode="LIFO")
buffer2 = Buffer(env, id="Buffer-2", capacity=1, delay=4, mode="FIFO")

# Adding connections
buffer1.connect(src,m1)

buffer2.connect(m1,sink)


env.run(until=500)

print("Time spent in each machine state:")
for state, duration in m1.stats["total_time_spent_in_states"].items():
    print(f"  {state:<30}: {duration:.2f}")

# Compute mutually exclusive sums
groupA_states = ["SETUP_STATE", "IDLE_STATE", "ATLEAST_ONE_PROCESSING_STATE", "ALL_ACTIVE_BLOCKED_STATE"]
groupB_states = ["SETUP_STATE", "IDLE_STATE", "ALL_ACTIVE_PROCESSING_STATE", "ATLEAST_ONE_BLOCKED_STATE"]

sum_groupA = sum(m1.stats["total_time_spent_in_states"][s] for s in groupA_states)
sum_groupB = sum(m1.stats["total_time_spent_in_states"][s] for s in groupB_states)

print("\nMutually exclusive group totals:")
print(f"  Group A (SETUP + IDLE + ATLEAST_ONE_PROCESSING + ALL_ACTIVE_BLOCKED): {sum_groupA:.2f}")
print(f"  Group B (SETUP + IDLE + ALL_ACTIVE_PROCESSING + ATLEAST_ONE_BLOCKED): {sum_groupB:.2f}")



m1.update_final_state_time(500)

print("Simulation completed.")
# Print statistics
print(f"Source {src.id} generated {src.stats['num_item_generated']} items.")
print(f"Source {src.id} discarded {src.stats['num_item_discarded']} items.")
print(f"Source {src.id} state times: {src.stats['total_time_spent_in_states']}")
print(f"Machine {m1.id} state times: {m1.stats}")

print(f"Time-average number of items in  {buffer1.id} is {buffer1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {buffer2.id} is {buffer2.stats['time_averaged_num_of_items_in_buffer']}")


print(f"Sink {sink.id} received {sink.stats['num_item_received']} items.")

print(m1.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", m1.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",m1.per_thread_total_time_in_blocked_state)

print("Time spent in each machine state:")
for state, duration in m1.stats["total_time_spent_in_states"].items():
    print(f"  {state:<30}: {duration:.2f}")

# Compute mutually exclusive sums
groupA_states = ["SETUP_STATE", "IDLE_STATE", "ATLEAST_ONE_PROCESSING_STATE", "ALL_ACTIVE_BLOCKED_STATE"]
groupB_states = ["SETUP_STATE", "IDLE_STATE", "ALL_ACTIVE_PROCESSING_STATE", "ATLEAST_ONE_BLOCKED_STATE"]

sum_groupA = sum(m1.stats["total_time_spent_in_states"][s] for s in groupA_states)
sum_groupB = sum(m1.stats["total_time_spent_in_states"][s] for s in groupB_states)

print("\nMutually exclusive group totals:")
print(f"  Group A (SETUP + IDLE + ATLEAST_ONE_PROCESSING + ALL_ACTIVE_BLOCKED): {sum_groupA:.2f}")
print(f"  Group B (SETUP + IDLE + ALL_ACTIVE_PROCESSING + ATLEAST_ONE_BLOCKED): {sum_groupB:.2f}")
