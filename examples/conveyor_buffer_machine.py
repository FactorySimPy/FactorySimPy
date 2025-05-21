import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.processor import Processor
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
src1= Source(env, name="Source-1",  work_capacity=1, store_capacity=100, delay=0.25)
src2= Source(env, name="Source-2",  work_capacity=1, store_capacity=100, delay=distribution_generator())
m1 = Processor(env, name="M1",work_capacity=1,store_capacity=3, delay=distribution_generator())
sink= Sink(env, name="sink2",store_capacity=200 )

# Initializing edges
buffer1 = Buffer(env, name="Buffer-1", store_capacity=2, delay=0.5)

conveyor1 = ConveyorBelt(env, name="Conveyor-1", belt_capacity=2, delay_per_slot=1)

buffer2 = Buffer(env, name="Buffer-2", store_capacity=2, delay=0.5)

# Adding connections
conveyor1.connect(src1,m1)
buffer1.connect(src2,m1)
buffer2.connect(m1,sink)

env.run(until=20)
