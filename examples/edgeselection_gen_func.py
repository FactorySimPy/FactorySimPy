
import simpy,sys, os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))




from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

env = simpy.Environment()

#***Here's an example that shows how to interconnect a source to a machine using buffers and pass a python function or a generator instance as parameter.***




#  System layout 

#   SRC1 ──> BUFFER1 ──┐
#                      │
#   SRC2 ──> BUFFER2 ──┴─> MACHINE1 ──┬─> BUFFER3 ──> SINK1
#      │                              │
#      └─> BUFFER5 ──> SINK3          └─> BUFFER4 ──> SINK2
#                                         


env = simpy.Environment()

#let the out_edge_selection of the source be a generator function that yields 1 or 0 based on the current time
# This generator function will yield 1 if the current time is even, and 0 if it is odd.
# This will simulate a scenario where the source alternates between two output edges based on the time.
#out_edge_selection as a generator function for machine
def machine_out_edge_selector(env):
   while True:
      if env.now%2==0:
         yield 1
      else:
         yield 0

#let the in_edge_selection of the machine be a generator function that yields the index of the edge to be selected
# This generator function will yield the index of the edge to be selected based on the current time.
# The index will be incremented every time the generator is called, and will wrap around when it reaches the number of edges.
#in_edge_selection as a generator function for machine
def machine_in_edge_selector(node):
   num_edges= len(node.in_edges)
   i=0
   while True:
         yield i
         yield i
         i = (i + 1) % num_edges

#let the out_edge_selection of the source be a generator function that yields 1 or 0 based on the current time
# This generator function will yield 1 if the current time is even, and 0 if it is odd.
#out_edge_selection as a generator function for source
def source_out_edge_selector(node, env):

   while True:
      if env.now%2==0:
         yield 1
      else:
         yield 0
    





# Initializing nodes
SRC1= Source(env, id="SRC1",  inter_arrival_time=0.7,blocking=False, out_edge_selection="FIRST_AVAILABLE" )
SRC2= Source(env, id="SRC2",  inter_arrival_time=0.4,blocking=False, out_edge_selection=None )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=4, processing_delay=1,in_edge_selection=None,out_edge_selection=None)
SINK1= Sink(env, id="SINK1", in_edge_selection="RANDOM" )
SINK2= Sink(env, id="SINK2", in_edge_selection="RANDOM"  )
SINK3= Sink(env, id="SINK3", in_edge_selection="FIRST_AVAILABLE"  )

#initialising out_edge_selection for source
source_out_edge_func = source_out_edge_selector(SRC2,env)
SRC2.out_edge_selection = source_out_edge_func

#initialising in_edge_selection parameter
machine_in_edge_func = machine_in_edge_selector(MACHINE1)
MACHINE1.in_edge_selection = machine_in_edge_func

#initialising in_edge_selection parameter for machine
machine_out_edge_func = machine_out_edge_selector(env)
MACHINE1.out_edge_selection = machine_out_edge_func





# Initializing edges
# Initializing edges
BUF1 = Buffer(env, id="BUF1", store_capacity=4, delay=0.5)
BUF2 = Buffer(env, id="BUF2", store_capacity=4, delay=0.5)
BUF3 = Buffer(env, id="BUF3", store_capacity=4, delay=0.5)
BUF4 = Buffer(env, id="BUF4", store_capacity=4, delay=0.5)
BUF5 = Buffer(env, id="BUF5", store_capacity=4, delay=0.5)




# Adding connections
BUF1.connect(SRC1,MACHINE1)
BUF2.connect(SRC2,MACHINE1)
BUF3.connect(MACHINE1,SINK1)
BUF4.connect(MACHINE1,SINK2)
BUF5.connect(SRC2,SINK3)


env.run(until=10)

print("Simulation completed.")
# Print statistics
print(f"Source {SRC1.id} generated {SRC1.stats['num_item_generated']} items.")
print(f"Source {SRC1.id} discarded {SRC1.stats['num_item_discarded']} items.")
print(f"Source {SRC1.id} state times: {SRC1.stats['total_time_spent_in_states']}")
print(f"Machine {MACHINE1.id} state times: {MACHINE1.stats}")

print(f"Time-average number of items in  {BUF1.id} is {BUF1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF2.id} is {BUF2.stats['time_averaged_num_of_items_in_buffer']}")


print(f"Sink {SINK1.id} received {SINK1.stats['num_item_received']} items.")

print(MACHINE1.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", MACHINE1.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",MACHINE1.per_thread_total_time_in_blocked_state)
