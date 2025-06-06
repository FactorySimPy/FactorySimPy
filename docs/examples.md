#Examples

In this section, we present examples that demonstrate how to use FactorySimPy

## A simple example

***Here's a simple example to connect a machine to an input buffer and output buffer and to simulate item flow through them.***
 
 In the example all the delays(inter_arrival_time, processing_delay) are constant values and out_edge_selection and out_edge_selection uses the generator functions that are available in the package ("FIRST"). The function name can be passed as a string. See [API](api_ref_main_page.md) for the details of all the available functions.

```python

#   System layout 
#   SRC ──> BUF1 ──> MACHINE1 ──> BUF2 ──> SINK

import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


env = simpy.Environment()

# Initializing nodes
SRC= Source(env, id="SRC",  inter_arrival_time= 0.8,blocking=False,out_edge_selection="FIRST" )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=4,store_capacity=5, processing_delay=1.1, in_edge_selection="FIRST",out_edge_selection="FIRST")
SINK= Sink(env, id="SINK" )

# Initializing edges
BUF1 = Buffer(env, id="BUF1", store_capacity=4, delay=0.5, mode = "FIFO")
BUF2 = Buffer(env, id="BUF2", store_capacity=4, delay=0.5, mode = "FIFO")

# Adding connections
BUF1.connect(SRC,MACHINE1)
BUF2.connect(MACHINE1,SINK)


env.run(until=10)


```

## Example with delay as random variates

***Here's an example showing how to pass functions as parameters.*** In this example inter_arrival is a python function that returns a value, processing_delay_generator and out_edge_selector are generator functions that yields a value based on some parameter of the node or simulation environment. 

```python


#   System layout 
#   SRC ──> BUF1 ──> MACHINE1 ──> BUF2 ──> SINK

import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

env = simpy.Environment()

def inter_arrival(loc=4.0, scale=5.0, size=1):
        delay = scipy.stats.expon.rvs(loc=0.0,scale=0.5,size=1)
        return delay[0]

def processing_delay_generator(node,env):
    while True:
        if Node.stats["total_time_spent_in_states"]["PROCESSING_STATE"]>7:
         yield 1
        else:
         yield 1.6







# Initializing nodes
SRC= Source(env, id="SRC",  inter_arrival_time=inter_arrival(),blocking=False, )


MACHINE1 = Machine(env, id="MACHINE1",work_capacity=4,store_capacity=5, processing_delay=None,in_edge_selection="FIRST",out_edge_selection="FIRST")
process_delay_gen1=processing_delay_generator(MACHINE1,env)
MACHINE1.processing_delay=process_delay_gen1

SINK= Sink(env, id="SINK" )


# Initializing edges
BUF1 = Buffer(env, id="BUF1", store_capacity=4, delay=0.5)
BUF2 = Buffer(env, id="BUF2", store_capacity=4, delay=0.5)


# Adding connections
BUF1.connect(SRC,MACHINE1)
BUF2.connect(MACHINE1,SINK)




env.run(until=10)
```

## Example with a custom edge selction policy is passed as a parameter

***Here's an example that shows how to interconnect a source to a machine using buffers and pass a python function or a generator instance as parameter.***
Sources generate items and puts it into its outgoing buffer. Machine picks this item and processes it and puts it another buffer. It choses the in_edge and out_edge based on the values yielded from function specified in in_edge_selection parameter and out_edge_selection parameter. Sink is used to remove the finished items from the respective buffers. 

```python


#  System layout 

#   src1 ──> buffer1 ──┐
#                      │
#   src2 ──> buffer2 ──┴─> Machine1 ──┬─> buffer3 ──> sink1
#      │                              │
#      └─> buffer4 ──> sink1          └─> buffer4 ──> sink1
#                                         

import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

env = simpy.Environment()

def machine_out_edge_selector(env):
   while True:
      if env.now%2==0:
         yield 1
      else:
         yield 0

def machine_in_edge_selector(node):
   num_edges= len(node.in_edges)
   while True:
         yield i
         yield i
         i = (i + 1) % num_edges

def source_out_edge_selector(node, env):

   while True:
      if env.now%2==0:
         yield 1
      else:
         yield 0
    





# Initializing nodes
SRC1= Source(env, id="SRC1",  inter_arrival_time=0.7,blocking=False )
SRC2= Source(env, id="SRC2",  inter_arrival_time=0.4,blocking=False, out_edge_selection=None )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=4,store_capacity=5, processing_delay=None,in_edge_selection=None,out_edge_selection=None)
SINK1= Sink(env, id="SINK1" )
SINK2= Sink(env, id="SINK2" )
SINK3= Sink(env, id="SINK3" )

#initialising out_edge_selection for source
source_out_edge_func = source_out_edge_selector(SRC,env)
SRC.out_edge_selection = source_out_edge_func

#initialising in_edge_selection parameter
machine_in_edge_func = machine_in_edge_selector(MACHINE1)
MACHINE1.in_edge_selection = in_edge_func

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
```



