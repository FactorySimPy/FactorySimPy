
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
src= Source(env, id="Source-1",  inter_arrival_time=distribution_generator(),blocking=False,out_edge_selection="FIRST_AVAILABLE" )
m1 = Machine(env, id="M1",work_capacity=2,store_capacity=2, processing_delay=distribution_generator())
sink= Sink(env, id="Sink-1" )

# Initializing edges
buffer1 = Buffer(env, id="Buffer-1", store_capacity=4, delay=0.5)
buffer2 = Buffer(env, id="Buffer-2", store_capacity=4, delay=0.5)

# Adding connections
buffer1.connect(src,m1)
buffer2.connect(m1,sink)


env.run(until=10)
print("Simulation completed.")
# Print statistics
print(f"Source {src.id} generated {src.stats['num_item_generated']} items.")
print(f"Source {src.id} discarded {src.stats['num_item_discarded']} items.")
print(f"Source {src.id} state times: {src.stats['total_time_spent_in_states']}")

print(f"Sink {sink.id} received {sink.stats['num_item_received']} items.")

