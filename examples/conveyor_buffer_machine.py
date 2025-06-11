import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.conveyor import ConveyorBelt
from factorysimpy.edges.buffer import Buffer

from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


env = simpy.Environment()

def distribution_generator(loc=4.0, scale=5.0, size=1):
    while True:
        delay = scipy.stats.expon.rvs(loc=0.0,scale=0.5,size=1)
        yield delay[0]

# Initializing nodes
src1= Source(env, id="Source-1",  inter_arrival_time=1,blocking=True,out_edge_selection="FIRST_AVAILABLE" )
src2= Source(env, id="Source-2",  inter_arrival_time=1,blocking=True,out_edge_selection="FIRST_AVAILABLE" )
m1 = Machine(env, id="M1",node_setup_time=0,work_capacity=1, processing_delay=1,in_edge_selection="RANDOM",out_edge_selection="FIRST_AVAILABLE")

sink= Sink(env, id="Sink-1" )

# Initializing edges
buffer1 = Buffer(env, id="Buffer-1", store_capacity=4, delay=0, mode="LIFO")
buffer2 = Buffer(env, id="Buffer-2", store_capacity=4, delay=0, mode="FIFO")
conveyor1 = ConveyorBelt(env, id="Conveyor-1", belt_capacity=2, delay_per_slot=1)


# Adding connections
conveyor1.connect(src1,m1)
buffer1.connect(src2,m1)
buffer2.connect(m1,sink)

env.run(until=100)
