import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
from factorysimpy.constructs.chain import connect_chain_with_source_sink, connect_nodes_with_buffers    

env = simpy.Environment()

#   SRC ──> BUFFER1 ───> MACHINE1 ───> BUFFER2 ──> SINK




SRC = Source(env, id="SRC", inter_arrival_time=0.2, blocking=True, out_edge_selection="FIRST_AVAILABLE")
SRC2 = Source(env, id="SRC2", inter_arrival_time=0.2, blocking=True, out_edge_selection="FIRST_AVAILABLE")
MACHINE1 = Machine(env, id="MACHINE1", work_capacity=1, blocking=True, processing_delay=0.5, in_edge_selection="RANDOM", out_edge_selection=0)
MACHINE2 = Machine(env, id="MACHINE2", work_capacity=1, blocking=True, processing_delay=0.5, in_edge_selection="RANDOM", out_edge_selection=0)
SINK = Sink(env, id="SINK")

# Initializing edges
BUFFER1 = Buffer(env, id="BUFFER1", store_capacity=1, delay=0)
BUFFER2 = Buffer(env, id="BUFFER2", store_capacity=1, delay=0)
BUFFER3 = Buffer(env, id="BUFFER3", store_capacity=1, delay=0)
BUFFER4 = Buffer(env, id="BUFFER4", store_capacity=1, delay=0)
# Adding connections
BUFFER1.connect(SRC, MACHINE1)
BUFFER2.connect(MACHINE1, SINK)
BUFFER3.connect(SRC2, MACHINE2)
BUFFER4.connect(MACHINE2, SINK)

env.run(until=2)

print(f"SINK {SINK.id} received {SINK.stats['num_item_received']} items.")

print(f"Throuphput:{SINK.stats['num_item_received']/env.now}")
tot_cycletime = SINK.stats["total_cycle_time"]
tot_items = SINK.stats["num_item_received"]
print(f"Cycletime, {tot_cycletime/tot_items if tot_items > 0 else 0}")

# Print statistics
print(f"Source {SRC.id} generated {SRC.stats['num_item_generated']} items.")
print(f"Source {SRC.id} state times: {SRC.stats}")
print(f"Source2 {SRC2.id} state times: {SRC2.stats}")
print(f"Throughput of system: {SINK.stats['num_item_received'] / env.now:.2f} items per time unit.")

machines = [MACHINE1]
for machine in machines:
    print("\n" )
    print(f"Machine {machine.id} state times: {machine.stats}")
    print(machine.time_per_work_occupancy)
    print("per_thread_total_time_in_processing_state", machine.per_thread_total_time_in_processing_state)
    print("per_thread_total_time_in_blocked_state", machine.per_thread_total_time_in_blocked_state)
    print("total_time_in_processing_state", machine.stats["num_item_processed"])