
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
src= Source(env, id="Source-1",  inter_arrival_time=distribution_generator(),criterion_to_put="round_robin", blocking=False)
m1 = Machine(env, id="M1",work_capacity=1,store_capacity=2, processing_delay=distribution_generator())
m2 = Machine(env, id="M2",work_capacity=1,store_capacity=2, processing_delay=distribution_generator())
sink1= Sink(env, id="Sink-1" )
sink2= Sink(env, id="Sink-2" )

# Initializing edges
buffer1 = Buffer(env, id="Buffer-1", store_capacity=4, delay=0.5)
buffer2 = Buffer(env, id="Buffer-2", store_capacity=4, delay=0.5)

buffer3 = Buffer(env, id="Buffer-1", store_capacity=4, delay=0.5)
buffer4 = Buffer(env, id="Buffer-2", store_capacity=4, delay=0.5)

# Adding connections
buffer1.connect(src,m1)
buffer2.connect(src,m2)
buffer3.connect(m1,sink1)
buffer4.connect(m2,sink2)


env.run(until=10)
print("Simulation completed.")
# Print statistics
print(f"Source {src.id} generated {src.class_statistics['item_generated']} items.")
print(f"Source {src.id} discarded {src.class_statistics['item_discarded']} items.")
print(f"Source {src.id} state times: {src.class_statistics['state_times']}")

print(f"Sink {sink1.id} received {sink1.class_statistics['item_received']} items.")
print(f"Sink {sink2.id} received {sink2.class_statistics['item_received']} items.")

