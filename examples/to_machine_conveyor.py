
import simpy,sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.processor import Processor
from factorysimpy.edges.buffer import Buffer
from factorysimpy.edges.conveyor import ConveyorBelt

from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


env = simpy.Environment()


# Initializing nodes
src= Source(env, name="Source-1", delay=(1,2))
m1 = Processor(env, name="M1",work_capacity=1,store_capacity=3, delay=3)
m2 = Processor(env, name="M2",work_capacity=1,store_capacity=3, delay=0.3)
sink= Sink(env, name="Sink-1",store_capacity=100 )

# Initializing edges
conveyor = ConveyorBelt(env, name="Conveyor-1", belt_capacity=10, delay_per_slot=1)
buffer1 = Buffer(env, name="Buffer-1", store_capacity=5, delay=0.5)
buffer2 = Buffer(env, name="Buffer-2", store_capacity=5, delay=0.5)

# Adding connections

buffer1.connect(src,m1)
conveyor.connect(m1, m2)
buffer2.connect(m2,sink)


env.run(until=30)

