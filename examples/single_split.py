
import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.split import Split
from factorysimpy.edges.buffer import Buffer

from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


env = simpy.Environment()

def distribution_generator(loc=4.0, scale=5.0, size=1):
    while True:
        delay = scipy.stats.expon.rvs(loc=0.0,scale=0.5,size=1)
        yield delay[0]

# Initializing nodes
src= Source(env, name="Source-1",  work_capacity=1, store_capacity=100, delay=distribution_generator())
split = Split(env, name="Drill-1",work_capacity=1,store_capacity=3, delay=distribution_generator())
sink1= Sink(env, name="Sink-1",store_capacity=20 )
sink2= Sink(env, name="Sink-1",store_capacity=20 )

# Initializing edges
buffer1 = Buffer(env, name="Buffer-1", store_capacity=5, delay=0.5)
buffer2 = Buffer(env, name="Buffer-2", store_capacity=5, delay=0.5)
buffer3 = Buffer(env, name="Buffer-3", store_capacity=5, delay=0.5)

# Adding connections
buffer1.connect(src,split)
buffer2.connect(split,sink1)
buffer2.connect(split,sink2)


env.run(until=12)

