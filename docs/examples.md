#Examples

In this section, we present examples that demonstrate how to use factorysimpy

A simple example to connect a machine to an input buffer and output buffer and to simulate item flow through them. Here, all the delays(inter_arrival_time, processing_delay) are constant values and out_edge_selection and out_edge_selection are generator functions that are available in the package. 

```python
import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


env = simpy.Environment()


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


An example showing how to pass functions as parameters. In this example inter_arrival is a python function that returns a value, processing_delay_generator and out_edge_selector are generator functions that yields a value based on some parameter of the node or simulation environment. 

```python

import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

env = simpy.Environment()

def inter_arrival(loc=4.0, scale=5.0, size=1):
        delay = scipy.stats.expon.rvs(loc=0.0,scale=0.5,size=1)
        return delay[0]

def processing_delay_generator(Node,env):
    while True:
        if Node.stats["total_time_spent_in_states"]["PROCESSING_STATE"]>7:
         yield 1
        else:
         yield 1.6

def out_edge_selector(Node, env):

   while True:
      if env.now%2==0:
         yield 1
      else:
         yield 0



# Initializing nodes
src= Source(env, id="Source-1",  inter_arrival_time=inter_arrival(),blocking=False,out_edge_selection=None )
OES=out_edge_selector(src,env)
src.out_edge_selection=OES

m1 = Machine(env, id="M1",work_capacity=4,store_capacity=5, processing_delay=None,in_edge_selection="FIRST",out_edge_selection="FIRST")
process_delay_gen1=processing_delay_generator(m1,env)
m1.processing_delay=process_delay_gen1

m2 = Machine(env, id="M2",work_capacity=4,store_capacity=5, processing_delay=0.5,in_edge_selection="FIRST",out_edge_selection="FIRST")
sink1= Sink(env, id="Sink-1" )
sink2= Sink(env, id="Sink-2" )

# Initializing edges
buffer1 = Buffer(env, id="Buffer-1", store_capacity=4, delay=0.5)
buffer2 = Buffer(env, id="Buffer-2", store_capacity=4, delay=0.5)
buffer3 = Buffer(env, id="Buffer-3", store_capacity=4, delay=0.5)
buffer4 = Buffer(env, id="Buffer-4", store_capacity=4, delay=0.5)

# Adding connections
buffer1.connect(src,m1)
buffer2.connect(src,m2)
buffer3.connect(m1,sink1)
buffer4.connect(m2,sink2)


env.run(until=10)
```



