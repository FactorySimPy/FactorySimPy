#Examples

In this section, we present examples that demonstrate how to use factorysimpy

A simple example to connect a machine to an input buffer and output buffer and to simulate item flow through them

```python
import factorysimpy
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
src= Source(env, id="Source-1",  inter_arrival_time= 0.8,blocking=False,out_edge_selection="FIRST" )
m1 = Machine(env, id="M1",work_capacity=4,store_capacity=5, processing_delay=1.1, in_edge_selection="FIRST",out_edge_selection="FIRST")
sink= Sink(env, id="Sink-1" )

# Initializing edges
buffer1 = Buffer(env, id="Buffer-1", store_capacity=4, delay=0.5, mode = "FIFO")
buffer2 = Buffer(env, id="Buffer-2", store_capacity=4, delay=0.5, mode = "FIFO")

# Adding connections
buffer1.connect(src,m1)
buffer2.connect(m1,sink)


env.run(until=10)


```



