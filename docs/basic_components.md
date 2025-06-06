# Basic Components


Node, Edge and Item are the 3 basic component types in the library. All the other components are derived from either Node or Edge. Item represents the entities that flow in the system. Nodes are the active, static elements in the system and are responsible for operations such as processing, splitting, or combining items. Every node maintains a list of `in_edges` and `out_edges`, which are references to edge objects that connect it to other nodes. Other parameters of Nodes are `id` (an unique name) and `node_setup_time` (initial delay in each node, which is be a constant value). Common node types include Machine, Split, Joint, Source, and Sink. Source can be used to generate items that flow in the system. Machines are the entities that modifies/processes an item. To multiplex the items that flow in the system, Splits can be used and to pack/join items from different incoming edges a Joint can be used. Sink is the terminal node in the system and the items that enter this node cannot be retrieved.


Edges are passive components that connect exactly two nodes (src_node and dest_node) and helps in transfering items between them. Edges are directed. Each edge has a unique identifier called `id`, and parameters `src_node` and `dest_node` to store the reference to the source node and destination node. Specific types of edges include Buffer, Conveyor, and Fleet. Buffers act as queues with a defined delay. Conveyors move items between nodes while preserving order and support both discrete (slotted belts) and continuous motion. Fleets represent systems like warehouse robots or human operators that transport items between nodes without preserving order.


**Rules for interconnection**

1. Node represent static entities that are active. Components like machine, source, sink, split, joints, etc are derived from node.
2. Edge is directed and connects one node to another. Conveyor, buffer and fleet are the entities that are of type Edge.
3. Items are discrete parts that flow in the system through the directed edges from one node to another. 
3. Each node has two lists `in_edges` and `out_edges` that points to a list with references of the edges that comes in and go out of the node.
4. Each edge stores pointers to a `src_node` and a `dest_node`. An edge can be used only to connect a node to another node or same node.
5. An edge can have the same node in both `src_node` and `dest_node`. Self loops are allowed.
6. Nodes are the active elements whose activites initiates state changes in the system.
7. Edges are the passive elements and state change occurs due to actions initiated by nodes.
8. To multiplex the output from a machine node into multiple streams, a split must be connected to the machine using an edge.
9. To join multiple streams and to feed as input to a machine , a joint must be connected to the machine using an edge.



**Steps for Connecting Components**

1. Instantiate nodes and edges:
   ```python
   n1 = Source()
   n2 = Machine()
   n3 = Sink()
   e1 = Buffer()
   e2 = Buffer()
   ```
2. Establish connections:
   ```python
   e1.connect(n1, n2)
   e2.connect(n2, n3)
   ```
---


<hr style="height:4px;border:none;color:blue; background-color:grey;" />
## Nodes 
<hr style="height:4px;border:none;color:blue; background-color:grey;" />

Nodes represent active elements in the system. This is a basic type and is the basis for the active components like Machine, Split, Sink, Source, Joint, etc. Every node has a unique identifier named `id` and maintains two lists named `in_edges` and `out_edges`. Every node has a `node_setup_time` that can be specified as a constant delay (integer of float). Activities that takesplace in a node create state changes in the system. The API documentation can be found in [Node](nodes.md)



<hr style="height:2px;border:none;color:grey; background-color:grey;" />

### Source
<hr style="height:2px;border:none;color:grey; background-color:grey;" />

The source component is responsible for generating items that enter and flow through the system. The API documentation can be found in [Source](source.md). There are two modes of operation for the source. If the `blocking` parameter is set to True, the source generates an item and tries to send it to the connected outgoing edge. If the edge is full or cannot accept the item, the source waits until space becomes available. If the `blocking` parameter is set to False, the source generates items and attempts to send them to the outgoing edge. If the edge is full or cannot accept the item, the source discards the item.



**Behavior**

At the start of the simulation, the source waits for `node_setup_time`. This is an initial, one-time wait time for setting up the node. This parameter is a constant delay specified as an integer or a float.
During a simulation run, the source generates items at discrete instants of time specified by `inter_arrival_time`. The parameter `inter_arrival_time` can be specified as a constant value (int or float) or as a reference to a python function or a generator function instance that generates random variates from a chosen distribution.
After generating an item, the source behaves as follows:

1. If `blocking` is True, it pushes the item without check if the outgoing edge if full and waits for the outgoing edge to accept the item.

2. If `blocking` is False, it checks if there is space in the outgoing edge to accomodate the item. If the edge is full or unavailable, the item is discarded.

The source then waits for an amount of time specified using the parameter `inter_arrival_time` before attempting to generate the next item. Source can be connected to multiple outgoing edges. To control how the next edge is selected for item transfer, desired strategy can be specified using the `out_edge_selection` parameter. It can either be one of the methods available in the package or a python function or a generator function instance that is provided by the user. Various options available in the package are "RANDOM", "FIRST", "LAST", "ROUND_ROBIN", "FIRST_AVAILABLE", etc. User can provide a reference to custom function in these parameters. If the function depends on any of the node attributes, users can pass `None` to these parameters at the time of node creation and later initilise the parameter with thea reference to the function. During its operation, the source transitions through the following states:

1. "SETUP_STATE": Initialization or warm-up phase before item generation starts.

2. "GENERATING_STATE": Active state where items are being created and pushed to the system.

3. "BLOCKED_STATE": The source is blocked, waiting for the outgoing edge to accept an item (only in blocking mode).



**Monitoring and Reporting**
The source component reports the following key metrics:

1. Total number of items generated
2. Number of items discarded (non-blocking mode)
3. Time spent in each state 

These metrics help in analyzing the performance and efficiency of the item generation process within the simulation model.

**Examples**

***Here's an example that shows how to interconnect a source to a machine using a buffer and pass a python function or a generator instance as parameter.***
Source generates items and puts it into the buffer. Machine picks this item and processes it and puts it another buffer. Sink is used to remove the finished items from the buffer. This example shows how to pass a python function and a generation function as parameter to the node.

```python

#   System layout 
#   src ──> buffer1 ──> m1 ──> buffer3 ──> sink1


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
         yield 0.8
        else:
         yield 1.6



# Initializing nodes
src= Source(env, id="Source-1",  inter_arrival_time=inter_arrival(),blocking=False,out_edge_selection="FIRST" )
m1 = Machine(env, id="M1",work_capacity=4,store_capacity=5, processing_delay=None,in_edge_selection="FIRST",out_edge_selection="FIRST")
sink= Sink(env, id="Sink-1" )

#initialising processing_delay parameter
process_delay_gen1=processing_delay_generator(m1,env)
m1.processing_delay=process_delay_gen1



# Initializing edges
buffer1 = Buffer(env, id="Buffer-1", store_capacity=4, delay=0.5)
buffer2 = Buffer(env, id="Buffer-2", store_capacity=4, delay=0.5)


# Adding connections
buffer1.connect(src,m1)
buffer2.connect(m1,sink)



env.run(until=10)
```

***Here's another example that shows how to interconnect a source to multiple machines and to pass a custom function in out_edge_selection parameter.*** Source generates items and puts it into the buffer by selecting the edge based on  the value specified in the parameter  `out_edge_selection`.  Based on which buffer has an item, the succeeding machine picks up the item and pushes it to its outgoing edge after processing it. Sink is used to remove the finished items from the buffer. This example shows how to pass a generation function to the parameter `out_edge_selection`

```python

#  System layout 

#   src ──> buffer1 ──> m1 ──> buffer3 ──> sink1  
#     └──> buffer2 ──> m2 ──> buffer4 ──> sink2

import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

env = simpy.Environment()



def out_edge_selector(env):

   while True:
      if env.now%2==0:
         yield 1
      else:
         yield 0



# Initializing nodes
src= Source(env, id="Source-1",  inter_arrival_time=0.56,blocking=False,out_edge_selection=None )
m1 = Machine(env, id="M1",work_capacity=4,store_capacity=5, processing_delay=0.98,in_edge_selection="FIRST",out_edge_selection="FIRST")
m2 = Machine(env, id="M2",work_capacity=4,store_capacity=5, processing_delay=0.5,in_edge_selection="FIRST",out_edge_selection="FIRST")
sink1= Sink(env, id="Sink-1" )
sink2= Sink(env, id="Sink-2" )

#initialising out_edge_selection parameter
out_edge_func=out_edge_selector(src,env)
src.out_edge_selection=out_edge_func

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


<hr style="height:2px;border:none;color:blue; background-color:grey;" />

### Machine
<hr style="height:2px;border:none;color:blue; background-color:grey;" />

Machine is a component that has a processing delay and processes/modifies items that flow in the system. It can have multiple incoming edges and outgoing edges. It gets an item from one of its in edges and processes the item in a `processing_delay` amount of time and pushes the item to one of its out edges. The API documentation can be found in [Machine](machine.md)


**Behavior**

At the start of the simulation, the machine waits for `node_setup_time`. This is an initial, one-time wait time for setting up the node. This parameter is a constant delay specified as an integer or a float.
During a simulation run, machine gets object from one of the in_edges. To choose an incoming edge, to pull the item from, the Machine utilises the strategy specified in the parameter `in_edge_selection`. Various options available are  "RANDOM", "FIRST", "LAST", "ROUND_ROBIN", "FIRST_AVAILABLE", etc. Similarly, to select and outgoing edge, to push the item to, Machine uses the method specified in `out_edge_selection` parameter. User can also provide a custom function to these parameters. If the function depends on any of the node attributes, users can pass `None` to these parameters at the time of node creation and later initilise the parameter with thea reference to the function or directly pass it at the time of creation. This is illustrated in the examples shown below. Machine picks an item and takes `processing_delay` amount of time to process the item and puts it inside the inbuiltstore. The capacity of this store can be specified in the parameter `store_capacity`. Machine can parallely process `work_capacity` number of items. But, if `work_capacity` is greater than `store_capacity`, then `work_capacity` is set to `store_capacity`. During its operation, Machine transitions through the following states:

1. "SETUP_STATE": Initialization or warm-up phase before item generation starts.

2. "IDLE_STATE": When the inbuilt store is empty, but the incoming edge does not have any items.

3. "PROCESSING_STATE": Active state where items are being processed and pushed to the system.

4. "BLOCKED_STATE": The machine is blocked, when its inbuilt store is full .


**Monitoring and Reporting**
The Machine component reports the following key metrics:

1. Total number of items processed
2. Time spent in each state 

**Examples**

***Here's an example that shows how to interconnect a source to a machine using buffers and pass a python function or a generator instance as parameter.***
Sources generate items and puts it into its outgoing buffer. Machine picks this item and processes it and puts it another buffer. It choses the in_edge and out_edge based on the values yielded from function specified in in_edge_selection parameter and out_edge_selection parameter. Sink is used to remove the finished items from the respective buffers. 

```python


#  System layout 

#   src1 ──> buffer1 ──┐
#                      │
#   src2 ──> buffer2 ──┴─> Machine1 ──┬─> buffer3 ──> sink1
#                                     │
#                                     └─> buffer4 ──> sink1
#   
import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

env = simpy.Environment()

def out_edge_selector(env):
   while True:
      if env.now%2==0:
         yield 1
      else:
         yield 0

def in_edge_selector(node):
   num_edges= len(node.in_edges)
   while True:
         yield i
         yield i
         i = (i + 1) % num_edges
    

def processing_delay_generator(node,env):
    while True:
        if node.stats["total_time_spent_in_states"]["PROCESSING_STATE"]>7:
         yield 0.8
        else:
         yield 1.6



# Initializing nodes
src1= Source(env, id="Source-1",  inter_arrival_time=0.7,blocking=False )
src2= Source(env, id="Source-2",  inter_arrival_time=0.4,blocking=False )
m1 = Machine(env, id="M1",work_capacity=4,store_capacity=5, processing_delay=None,in_edge_selection="FIRST",out_edge_selection="FIRST")
sink1= Sink(env, id="Sink-1" )
sink2= Sink(env, id="Sink-1" )

#initialising in_edge_selection parameter
in_edge_func=in_edge_selector(m1)
m1.in_edge_selection=in_edge_func

#initialising in_edge_selection parameter
out_edge_func=out_edge_selector(env)
m1.out_edge_selection=out_edge_func

#initialising processing_delay parameter
process_delay_gen1=processing_delay_generator(m1,env)
m1.processing_delay=process_delay_gen1



# Initializing edges
buffer1 = Buffer(env, id="Buffer-1", store_capacity=2, delay=0.5)
buffer2 = Buffer(env, id="Buffer-2", store_capacity=2, delay=0.5)
buffer3 = Buffer(env, id="Buffer-3", store_capacity=2, delay=0.5)
buffer4 = Buffer(env, id="Buffer-4", store_capacity=2, delay=0.5)


# Adding connections
buffer1.connect(src1,m1)
buffer2.connect(src2,m1)
buffer3.connect(m1,sink1)
buffer4.connect(m1,sink2)



env.run(until=10)
```

<hr style="height:2px;border:none;color:blue; background-color:grey;" />
### Split
<hr style="height:2px;border:none;color:blue; background-color:grey;" />

<hr style="height:2px;border:none;color:blue; background-color:grey;" />
### Joint
<hr style="height:2px;border:none;color:blue; background-color:grey;" />

<hr style="height:2px;border:none;color:blue; background-color:grey;" />
### Sink
<hr style="height:2px;border:none;color:blue; background-color:grey;" />


 A Sink is a terminal node that collects flow items at the end. Once an item enters the Sink, it is considered to have exited the system and cannot be retrieved or processed further. This sink can have multiple input edges and no output edges. It has a unique identifier. It only has a single state "COLLECTING_STATE". The API documentation can be found in [Sink](sink.md)


<hr style="height:3px;border:none;color: grey; background-color:grey; " />
## Edges
<hr style="height:3px;border:none;color: grey;background-color:grey; " />


Edges represent passive elements in the system. This is the basis for the components like Buffer, Conveyor, Fleet, etc. Every edge has a unique identifier named `id` and maintains references to a source node `src_node` and a destination node `dest_node`. Edge acts as a conntction between these two nodes and facilitates the movement of items between the nodes. 


<hr style="height:2px;border:none;color:blue; background-color:grey;" />
### Buffer
<hr style="height:2px;border:none;color:blue; background-color:grey;" />


Buffer is a type of edge that represents a queue to store items that wait to be accepted by a downstream component.
This helps to remove the bottlenecks that come when the processing delays of nodes are not matching and one processes faster than the other. It has two modes of operation that are FIFO and LIFO. The API documentation can be found in [Buffer](buffer.md)


**Behavior**


During a simulation run, `src_node` puts an item into the buffer and the item gets available after delay amount of time for the `dest_node`. It operates in two modes- First In First Out(FIFO) or Last In First Out(LIFO). The number of items that a buffer can hold at any time can be specified using the parameter `store_capacity`. Buffer transitions through the following states during simulation- 

1. "EMPTY_STATE"  : when there is no items in the buffer
2. "RELEASING_STATE". When there is items.


**Monitoring and Reporting**
The Machine component reports the following key metrics:

1. time averaged number of items available in buffer.
2. Time spent in each state 

<hr style="height:2px;border:none;color:blue; background-color:grey;" />
### Conveyor
<hr style="height:2px;border:none;color:blue; background-color:grey;" />

Conveyor connects two nodes and moves items from one end to the other. The API documentation can be found in [Conveyor](conveyor.md)
There are two variants of conveyor available:


**Slotted-type**: This variant moves items from one end to the other at fixed interval. There is a constant delay between two movements. The `capacity` of slotted-type conveyor is the number of slots available in it and cn hold up to `capacity` number of items at a time.

**Constant speed conveyors**: This variant moves items at a constant speed. It can only be used to move discrete items. It also has a `capacity` to specify the maximum number of items that it can hold at any given time.

Conveyors can be either `blocking` or `non-blocking`:

1. A `blocking` type conveyor is also known as `non-accumulating` conveyor, such conveyor will not allow `src_node` to push items into the conveyor, if it is in a blocked state

2. A `non-blocking`(`accumulating`) conveyor allows src_node to push items until its capacity is reached when when it is in blocked state.

**Behavior**


During a simulation run, the Conveyor gets an item and as soon as it gets an item it starts moving and after moving it waits delay amount of time before the next move. It moves until the first item reaches the other end of the belt. If item is not taken out by a dest_npde, then conveyor will be in "BLOCKED_STATE". During its operation, the source transitions through the following states:


1. "SETUP_STATE": Initialization or warm-up phase.

2. "MOVING_STATE": state when the belt is moving.

3. "BLOCKED_STATE": IT is blocked, waiting for the dest_node to taken an item ouy.



**Monitoring and Reporting**
The component reports the following key metrics:

1. Time averaged number of items 
3. Time spent in each state 

