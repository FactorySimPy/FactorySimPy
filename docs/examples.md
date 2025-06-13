#Examples

In this section, we present examples that demonstrate how to use FactorySimPy

## A simple example

***Here's a simple example to connect a machine to an input buffer and output buffer and to simulate item flow through them.***

 

Shown below is a very simple example. Here, the delays to be configured are `inter_arrival_time`, and `processing_delay` of the source and the machine respectively. In this example, the delays `inter_arrival_time`, and `processing_delay`, are specified as constant values at the time of node initiation.

Similarly `in_edge_selection` and  `out_edge_selection` can also be provided as a constant or use one of the generator functions available in the package. Such function name can be passed as a string. See [API](api_ref_main_page.md) for the details of all the available functions.
 
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
SRC= Source(env, id="SRC",  inter_arrival_time= 0.8,blocking=False,out_edge_selection=0 )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=4, processing_delay=1.1, in_edge_selection=0,out_edge_selection="RANDOM")
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

***Here's an example showing how to pass functions as delay parameters.*** 

Shown below is a very simple example where the sources generate items and puts it to a machine through a buffer and the items processed in machine is moved to a sink using a another buffer. This example shows how to pass a function as a parameter. Here, the delays to be configured are `inter_arrival_time`, and `processing_delay` of source and machine. These are specified as a reference to a python function and generator function instance respectively. Here, inter_arrival is a python function that returns a value, processing_delay_generator is a generator functions that yields a value based on an attribute of the node.

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
SRC= Source(env, id="SRC",  inter_arrival_time=inter_arrival(),blocking=False,out_edge_selction=0 )


MACHINE1 = Machine(env, id="MACHINE1",work_capacity=4,processing_delay=None,in_edge_selection="RANDOM",out_edge_selection="RANDOM")
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

## Example with a custom edge selction policy as a function

***Here's an example that shows how to interconnect a source to a machine using buffers and pass a python function or a generator instance as parameter.***


In the example below, the sources generate items and puts it into its output buffer. Machine picks this item and processes it and puts it to another buffer. It choses the input edge and output edge based on the values yielded from function specified in `in_edge_selection` parameter and `out_edge_selection` parameter. Generator function instances are passed as input to parameters in this example. Sink is used to remove the finished items from the respective buffers. 


```python


#  System layout 

#   SRC1 ──> BUFFER1 ──┐
#                      │
#   SRC2 ──> BUFFER2 ──┴─> MACHINE1 ──┬─> BUFFER3 ──> SINK1
#      │                              │
#      └─> BUFFER5 ──> SINK3          └─> BUFFER4 ──> SINK2
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
SRC1= Source(env, id="SRC1",  inter_arrival_time=0.7,blocking=False, out_edge_selection="FIRST_AVAILABLE" )
SRC2= Source(env, id="SRC2",  inter_arrival_time=0.4,blocking=False, out_edge_selection=None )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=4, processing_delay=None,in_edge_selection=None,out_edge_selection=None)
SINK1= Sink(env, id="SINK1", in_edge_selection="RANDOM" )
SINK2= Sink(env, id="SINK2", in_edge_selection="RANDOM"  )
SINK3= Sink(env, id="SINK3",, in_edge_selection="FIRST_AVAILABLE"  )

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

## Example to illustrate the use of the components split and joint

***An example to understand how to simulate packing and unpacking of items using split and joint***

Consider a system which has to pack 5 base items of `flow_item_type`="item" in to an entity of `flow_item_type`="pallet". And in the same example
the method to unpack these packed items using a split is also shown.


```python



#  System layout 

#   SRC1 ──> BUFFER1 ──┐
#                      │
#   SRC2 ──> BUFFER2 ──┴─> JOINT1 ──> BUFFER3 ──>SPLIT1 ──┬─> BUFFER4 ──> SINK1
#                                                         │
#                                                         └─> BUFFER5 ──> SINK2
# 


import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
from factorysimpy.nodes.joint import Joint
from factorysimpy.nodes.split import Split


env = simpy.Environment()


def split_out_edge_selector(node):
   while True:
      proc=node.env.active_process
      item_in_process= node.worker_process_map[proc]
     
      if item_in_process is None:
         raise RuntimeError("Unknown calling process")
      
      if item_in_process.flow_item_type=="item" :
            yield 0
        
      elif item_in_process.flow_item_type=="pallet" and len(item_in_process.items) ==0:
        
            yield 1
      
      
      else:
         raise ValueError("Invalid item_type encountered")

# Initializing nodes
SRC1= Source(env, id="SRC1", flow_item_type = "pallet", inter_arrival_time= 0.8,blocking=False,out_edge_selection="RANDOM" )

SRC2= Source(env, id="SRC2", flow_item_type = "item",  inter_arrival_time= 0.8,blocking=False,out_edge_selection="RANDOM" )

JOINT1 = Joint(env, id="JOINT1", target_quantity_of_each_item=[1,5], work_capacity=1, processing_delay=1.1, blocking= False, out_edge_selection="RANDOM" )

SPLIT1 = Split(env, id="SPLIT1",work_capacity=1, processing_delay=1.1, in_edge_selection="RANDOM",out_edge_selection=None )


SINK1= Sink(env, id="SINK1" )
SINK2= Sink(env, id="SINK2" )


#initialising in_edge_selection parameter for split
split_out_edge_func = split_out_edge_selector(SPLIT1)
SPLIT1.out_edge_selection = split_out_edge_func

# Initializing edges
BUF1 = Buffer(env, id="BUF1", store_capacity=2, delay=0.5, mode = "FIFO")
BUF2 = Buffer(env, id="BUF2", store_capacity=2, delay=0.5, mode = "FIFO")
BUF3 = Buffer(env, id="BUF3", store_capacity=2, delay=0.5, mode = "FIFO")
BUF4 = Buffer(env, id="BUF4", store_capacity=2, delay=0, mode = "FIFO")
BUF5 = Buffer(env, id="BUF5", store_capacity=2, delay=0, mode = "FIFO")


# Adding connections
BUF1.connect(SRC1,JOINT1)
BUF2.connect(SRC2,JOINT1)
BUF3.connect(JOINT1,SPLIT1)
BUF4.connect(SPLIT1,SINK1)
BUF5.connect(SPLIT1,SINK2)


env.run(until=10)



```

## Example with constructs

***Here's an example that shows the utility of the constructs***


Suppose you want to model an assembly line with 20 machines connected in series, each separated by a buffer. Manually creating and connecting each machine and buffer would be repetitive, error-prone, and require a lot of code. To simplify this process for large, homogeneous systems, FactorySimPy provides constructs that automate the creation and connection of such chains.



```python


#  System layout 

#   SRC ──> BUF1 ──> MACHINE1 ──> BUF2 ──> MACHINE2 ──>   
#       ──> BUF3 ──> MACHINE3 ──> BUF4 ──> MACHINE4 ──>  ...
#            .          .           .         .
#            .          .           .         .
#       ...   BUF19 ──> MACHINE19 ──> BUF20 ──> MACHINE20 ──> SINK

# (20 machines in series, each separated by a buffer)

import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
from factorysimpy.constructs.chain import connect_chain_with_source_sink, connect_nodes_with_buffers    

env = simpy.Environment()

node_kwargs = {
   
    "node_setup_time": 0,
    "work_capacity": 1,
    "processing_delay": 0.8,
    "in_edge_selection": "RANDOM",
    "out_edge_selection": "FIRST_AVAILABLE"
}

edge_kwargs = {
    
    "store_capacity": 4,
    "delay": 0,
    "mode": "LIFO"
}

source_kwargs = {
    
    "inter_arrival_time": 1,
    "blocking": True,
    "out_edge_selection": "FIRST_AVAILABLE"
}
sink_kwargs = {
    "id": "Sink-1"
}


# Example for a chain of 1 machine (count=1)
nodes, edges, src, sink = connect_chain_with_source_sink(
    env,
    count=20,
    node_cls=Machine,
    edge_cls=Buffer,
    source_cls=Source,
    sink_cls=Sink,
    node_kwargs=node_kwargs,
    edge_kwargs=edge_kwargs,
    source_kwargs = source_kwargs,
    sink_kwargs= sink_kwargs,
    prefix="Machine",
    edge_prefix="Buffer"
)


machines, buffers = connect_nodes_with_buffers(nodes, edges, src, sink)




env.run(until=100)

```


