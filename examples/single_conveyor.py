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

sink= Sink(env, name="Sink-1", )

# Initializing edges
conveyor = ConveyorBelt(env, name="Conveyor-1", belt_capacity=10, delay_per_slot=1)


# Adding connections


conveyor.connect(src, sink)



env.run(until=30)
