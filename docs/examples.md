#Examples

In this section, we present examples that demonstrate how to use FactorySimPy

## A simple example

***Here's a simple example to connect a machine to an input buffer and output buffer and to simulate item flow through them.***

 

Shown below is a very simple example. Here, the delays to be configured are `inter_arrival_time`, and `processing_delay` of the source and the machine respectively. In this example, the delays `inter_arrival_time`, and `processing_delay`, are specified as constant values at the time of node initiation.

Similarly `in_edge_selection` and  `out_edge_selection` can also be provided as a constant or use one of the generator functions available in the package. These functions can be passed as a string. [See this page for details about edge selection policy.](configuring_parameters.md)

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

## Example with delay as a reference to a function


Shown below is a very simple example where the sources generate items and puts it to a machine through a buffer and the items processed in machine is moved to a sink using a another buffer. This example shows how to pass a function as a parameter.

### Delay as python function

 ***An example showing how to pass python functions as delay parameters.*** 

 In this example, the delays to be configured are `inter_arrival_time`, and `processing_delay` of source and machine. These are specified as a reference to a python function. Let the inter arrival time of the source be a value sampled from a gaussian distribution with mean = 1, std deviation is = 0.25 and the processing delay of the machine be a value function of the duration of the time spent by the machine in processing state.


```python


#   System layout 
#   SRC ──> BUF1 ──> MACHINE1 ──> BUF2 ──> SINK
import random
import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

env = simpy.Environment()

env = simpy.Environment()

#let the inter arrival time of the source be a value sampled from a gaussian distribution with mean = 1, std deviation is = 0.25
#Gaussian distribution as a python function 
def generate_gaussian_distribution(mean=0, std_dev=1):
   
    return random.gauss(mu=mean,sigma= std_dev)
       
#let the processing delay of the machine be a value function of the duration of the time spent by the machine in processing state
#if the time spent in processing state is greater than 7, the processing delay has to take one value in index 0 of the return_vals
#if the time spent in processing state is less than or equal to 7, the processing delay has to take the value in index 1
#This behaviour as a python function 
def generate_process_delay(node,env, return_vals):
      if node.stats["total_time_spent_in_states"]["PROCESSING_STATE"]>7:
        return return_vals[0]
      else:
        return return_vals[1]




# Initializing nodes
SRC= Source(env, id="SRC",  inter_arrival_time=generate_gaussian_distribution(1,0.25),blocking=False,out_edge_selection=0 )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=1,processing_delay=None,in_edge_selection="RANDOM",out_edge_selection="RANDOM")
processing_delay_func=generate_process_delay(MACHINE1,env,[0.9,1.2])
MACHINE1.processing_delay = processing_delay_func
SINK= Sink(env, id="SINK" )



# Initializing edges
BUF1 = Buffer(env, id="BUF1", store_capacity=4, delay=0.5)
BUF2 = Buffer(env, id="BUF2", store_capacity=4, delay=0.5)


# Adding connections
BUF1.connect(SRC,MACHINE1)
BUF2.connect(MACHINE1,SINK)




env.run(until=10)
```





### Delay as generator function
***An example showing how to pass python generator functions as delay parameters.*** 


  In this example (same as above), the delays to be configured are `inter_arrival_time`, and `processing_delay` of source and machine. These are specified as a reference to a python generator function instance. Let the inter arrival time of the source be a value sampled from a gaussian distribution with mean = 1, std deviation is = 0.25 and the processing delay of the machine be a value function of the duration of the time spent by the machine in processing state. Generator functions are created for the two cases and supplied as parameters.
```python


#   System layout 
#   SRC ──> BUF1 ──> MACHINE1 ──> BUF2 ──> SINK
import random
import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

env = simpy.Environment()

#let the inter arrival time of the source be a value sampled from a gaussian distribution with mean = 2, std deviation is = 0.5
#Gaussian distribution as a generator function 
def generate_gaussian_distribution(mean=0, std_dev=1):
   while True:
        yield random.gauss(mu=mean,sigma= std_dev)
       
#let the processing delay of the machine be a value function of the duration of the time spent by the machine in processing state
#if the time spent in processing state is greater than 7, the processing delay has to take one value in index 0 of the return_vals
#if the time spent in processing state is less than or equal to 7, the processing delay has to take the value in index 1
#This behaviour as a generator function 
def generate_process_delay(node,env, return_vals):
   while True:
      if node.stats["total_time_spent_in_states"]["PROCESSING_STATE"]>7:
        yield return_vals[0]
      else:
        yield  return_vals[1]




# Initializing nodes
SRC= Source(env, id="SRC",  inter_arrival_time=generate_gaussian_distribution(1,0.25),blocking=False,out_edge_selection=0 )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=1,processing_delay=None,in_edge_selection="RANDOM",out_edge_selection="RANDOM")
processing_delay_func=generate_process_delay(MACHINE1,env,[0.9,1.2])
MACHINE1.processing_delay = processing_delay_func
SINK= Sink(env, id="SINK" )



# Initializing edges
BUF1 = Buffer(env, id="BUF1", store_capacity=4, delay=0.5)
BUF2 = Buffer(env, id="BUF2", store_capacity=4, delay=0.5)


# Adding connections
BUF1.connect(SRC,MACHINE1)
BUF2.connect(MACHINE1,SINK)




env.run(until=10)
```




## Example with a custom edge selection policy as a function




In the example below, the sources generate items and puts it into its output buffer. Machine picks this item and processes it and puts it to another buffer. It choses the input edge and output edge based on the values yielded from function specified in `in_edge_selection` parameter and `out_edge_selection` parameter. 



### Edge selection as python function

***An example that shows how to interconnect a source to a machine using buffers and pass a python function as parameter.***

Consider the case when the edge selection parameters are to be modelled as a python function. Here is an example that shows how to pass a python function instance as a parameter. Let us consider a case where the `in_edge_selection` is dependant on the values sampled from a uniform distribution [0,1], if the sampled value is less than 0.5, then always index 1 is returned and if the sampled value is greater than 0.5 then index 0 is returned. `out_edge_selection` is dependant on the values sampled from a gaussian distribution with mean 4 and standard deviation 1 , if the value is greater than 3, then edge 0 is selected otherwise edge 1 is selected. Edge selection parameters of SRC1, and all the  SINKs are provided with options that are implemented within the package. [See this page for details about edge selection policy.s](configuring_parameters.md)

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

#let the in_edge_selection of the machine be a function that yields 1 or 0 based on the value sampled from uniform distribution [0,1]
# This  function will yield 1 if value 0.5, and 0 if it is otherwise.
#in_edge_selection as a  function for machine
def machine_in_edge_selector():
   if random.random()<0.5:
      return 1
   else:
      return 0

#let the out_edge_selection of the machine be a function that yields the index of the edge to be selected
# This  function will yield the index of the edge to be selected based on the value sampled from a gaussian dostribution with mean=4 and sigma=1
# it will return 1 is the sampled value is >3, else it will return 0
#out_edge_selection as a function for machine

def machine_out_edge_selector(mean=4, std_dev=1):
   if random.gauss(mu=mean,sigma= std_dev) >3:
      return 1
   else:
      return 0

#let the out_edge_selection of the source 2 be a generator function that yields 1 or 0 based on the current time
# This generator function will yield 1 if the current time is even, and 0 if it is odd.
#out_edge_selection as a function for source
def source_out_edge_selector(env):
      if env.now%2==0:
         return 1
      else:
         return 0
    





# Initializing nodes
SRC1= Source(env, id="SRC1",  inter_arrival_time=0.7,blocking=False, out_edge_selection="FIRST_AVAILABLE" )
SRC2= Source(env, id="SRC2",  inter_arrival_time=0.4,blocking=False, out_edge_selection=source_out_edge_selection(env) )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=4, processing_delay=1,in_edge_selection=machine_in_edge_selection(),out_edge_selection=machine_in_edge_selection(4,1))
SINK1= Sink(env, id="SINK1", in_edge_selection="RANDOM" )
SINK2= Sink(env, id="SINK2", in_edge_selection="RANDOM"  )
SINK3= Sink(env, id="SINK3", in_edge_selection="FIRST_AVAILABLE"  )







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


### Edge selection as generator function

***An example that shows how to interconnect a source to a machine using buffers and pass a python function or a generator instance as parameter.***

Consider the case when the edge selection parameters are to be modelled as a generator function that depends on the node object or the current time of the simulation environment. Here is an example that shows how to pass a generator function instance as a parameter.
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

#let the out_edge_selection of the source be a generator function that yields 1 or 0 based on the current time
# This generator function will yield 1 if the current time is even, and 0 if it is odd.
# This will simulate a scenario where the source alternates between two output edges based on the time.
#out_edge_selection as a generator function for machine
def machine_out_edge_selector(env):
   while True:
      if env.now%2==0:
         yield 1
      else:
         yield 0

#let the in_edge_selection of the machine be a generator function that yields the index of the edge to be selected
# This generator function will yield the index of the edge to be selected based on the current time.
# The index will be incremented every time the generator is called, and will wrap around when it reaches the number of edges.
#in_edge_selection as a generator function for machine
def machine_in_edge_selector(node):
   num_edges= len(node.in_edges)
   i=0
   while True:
         yield i
         yield i
         i = (i + 1) % num_edges

#let the out_edge_selection of the source be a generator function that yields 1 or 0 based on the current time
# This generator function will yield 1 if the current time is even, and 0 if it is odd.
#out_edge_selection as a generator function for source
def source_out_edge_selector(node, env):

   while True:
      if env.now%2==0:
         yield 1
      else:
         yield 0
    





# Initializing nodes
SRC1= Source(env, id="SRC1",  inter_arrival_time=0.7,blocking=False, out_edge_selection="FIRST_AVAILABLE" )
SRC2= Source(env, id="SRC2",  inter_arrival_time=0.4,blocking=False, out_edge_selection=None )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=4, processing_delay=1,in_edge_selection=None,out_edge_selection=None)
SINK1= Sink(env, id="SINK1", in_edge_selection="RANDOM" )
SINK2= Sink(env, id="SINK2", in_edge_selection="RANDOM"  )
SINK3= Sink(env, id="SINK3", in_edge_selection="FIRST_AVAILABLE"  )

#initialising out_edge_selection for source
source_out_edge_func = source_out_edge_selector(SRC2,env)
SRC2.out_edge_selection = source_out_edge_func

#initialising in_edge_selection parameter
machine_in_edge_func = machine_in_edge_selector(MACHINE1)
MACHINE1.in_edge_selection = machine_in_edge_func

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


