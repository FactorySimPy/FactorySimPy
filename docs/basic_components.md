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




## Nodes 
<hr style="height:4px;border:none;color:blue; background-color:grey;" />

Nodes represent active elements in the system. This is a basic type and is the basis for the active components like Machine, Split, Sink, Source, Joint, etc. Every node has a unique identifier named `id` and maintains two lists named `in_edges` and `out_edges`. Every node has a `node_setup_time` that can be specified as a constant delay (integer of float). Activities that takesplace in a node create state changes in the system. The API documentation can be found in [Node](nodes.md)



<hr style="height:2px;border:none;color:grey; background-color:grey;" />

### Source
<hr style="height:2px;border:none;color:grey; background-color:grey;" />

**About**
The source component is responsible for generating items that enter and flow through the system. The API documentation can be found in [Source](source.md). There are two modes of operation for the source. If the `blocking` parameter is set to True, the source generates an item and tries to send it to the connected outgoing edge. If the edge is full or cannot accept the item, the source waits until space becomes available. If the `blocking` parameter is set to False, the source generates items and attempts to send them to the outgoing edge. If the edge is full or cannot accept the item, the source discards the item.

**Basic attributes**

- `state` - current state of the component
- `inter_arrival_time`- time interval between two successive item generation
- `blocking` -  If True, waits for outgoing edge to accept item; if False, discards if full
- `out_edge_selection`- Edge selection policy as a function to select outgoing edge

**Behavior**

At the start of the simulation, the source waits for `node_setup_time`. This is an initial, one-time wait time for setting up the node and should be provided as a constant (an `int` or `float`).

During a simulation run, the source generates items at discrete instants of time determined by the parameter `inter_arrival_time`. This parameter can be specified as a constant value (`int` or `float`) or as a reference to a python function or a generator function instance that generates random variates from a chosen distribution. If the function depends on any of the node attributes, users can pass `None` to this parameter at the time of node creation and later initialise the parameter with the reference to the function.


After generating an item, the source behaves as follows:

1. If `blocking` is `True`, it pushes the item without checking whether the outgoing edge is full and waits for the outgoing edge to accept the item.

2. If `blocking` is `False`, it checks if there is space in the outgoing edge to accomodate the item. If the edge is full or unavailable, the item is discarded.



The source can be connected to multiple outgoing edges. To control how the next edge is selected for item transfer, the desired strategy can be specified using the `out_edge_selection` parameter. It can either be one of the methods available in the package (passed as a string) or a Python function or a generator function instance provided by the user. 

Various options available in the package for `out_edge_selection` include:

- "RANDOM": Selects a random out edge.
- "FIRST": Selects the first out edge.
- "LAST": Selects the last out edge.
- "ROUND_ROBIN": Selects out edges in a round-robin manner.
- "FIRST_AVAILABLE": Selects the first out edge that can accept an item.

User-provided function should return or yield an edge index. If the function depends on any of the node attributes, user can pass `None` to this parameter at the time of node creation and later initialize the parameter with the reference to the function. The source then waits for an amount of time determined using the parameter `inter_arrival_time` before attempting to generate the next item.

**States**

During its operation, the source transitions through the following states:

1. "SETUP_STATE": Initialization or warm-up phase before item generation starts.

2. "GENERATING_STATE": Active state where items are being created and pushed to the out_edge.

3. "BLOCKED_STATE": The source is blocked, waiting for the outgoing edge to accept an item (only when `blocking` is `True`).

**Usage**

Source can be initialised as shown below.

```python

import factorysimpy
from factorysimpy.nodes.source import Source

SRC = Source(
    env,                        # Simulation environment
    id="SRC2",                  # Unique identifier for the source node
    inter_arrival_time=0.4,     # Time between item generations (can be constant or function/generator)
    blocking=False,             # If True, waits for outgoing edge to accept item; if False, discards if full
    out_edge_selection=None     # Strategy or function to select outgoing edge (can be string or callable)
)


```


**Statistics collected**

 Several key metrics are being monitored in the class can be accessed in the attribute `stats` as 
 component.stats[`num_item_generated`]. The source component reports the following key metrics.

1. Total number of items generated
2. Number of items discarded (non-blocking mode)
3. Time spent in each state 

Consider a source with `blocking`= `False` and instance name as SRC. Metrics of a component SRC can be accessed after completion of the simulation run as

```python


print(f"Total number of items generated by {SRC.id}={SRC.stats["num_items_processed"]}")
print(f"Total number of items discarded by {SRC.id}={SRC.stats["num_items_discarded"]}")

print(f"Source {SRC.id}, state times: {SRC.stats["time_spent_in_states"]}")


```


**Examples**

- ***[A simple example with all parameters passed as constants](examples.md/#a-simple-example)***

- ***[An example with `inter_arrival_delay` passed as a reference to a generator function instance that generates random variates from a chosen distribution](examples.md/#example-with-delay-as-random-variates)***

- ***[An example with `out_edge_selection` parameter is passed as custom function that yields edge indices](examples.md/#example-with-a-custom-edge-selction-policy-as-a-function)***



<hr style="height:2px;border:none;color:blue; background-color:grey;" />

### Machine
<hr style="height:2px;border:none;color:blue; background-color:grey;" />

**About**

Machine is a component that processes/modifies items that flow in the system. It uses a `processing_delay` amount of time to process an item. It can have multiple incoming edges and outgoing edges. A machine can process more than one item simultaneously. It gets an item from one of its in edges and processes the item in a `processing_delay` amount of time and pushes the item to one of its out edges. It does not have any inbuilt storage. Machine has two modes of operation based on the parameter value specified in `blocking`. If it is set to `True`, the machine pushes the processed item to a chosen outgoing edge and waits for it to accept the item. The other mode is when `blocking` is set to `False`. Machine checks if there is space available in the chosen outgoing edge and only if then the item is pushed. If the outgoing edge is unavailable or full, the item will be discarded. The API documentation can be found in [Machine](machine.md)

**Basic attributes**

- `state` - current state of the component
- `processing_delay`- time taken to process an item
- `work_capacity` - maximum number of jobs or items that can be processed by the machine simulataneously
- `blocking`-  If True, waits for outgoing edge to accept item; if False, discards if full
- `in_edge_selection`- Edge selection policy as a function to select outgoing edge
- `out_edge_selection`- Edge selection policy as a function to select outgoing edge

**Behavior**

At the start of the simulation, the machine waits for `node_setup_time`. This is an initial, one-time wait time for setting up the node and should be provided as a constant (an `int` or `float`).  Machine can parallely process `work_capacity` number of items. Machine spawns `work_capcity` number of workers that repeats all the activities from picking an item from a chosen incoming edge, processing it and pushing it out to the next chosen outgoing edge. 

During a simulation run, each worker thread gets object from one of its `in_edges`. To choose an incoming edge to pull an item from, the worker thread utilises the strategy specified in the parameter `in_edge_selection`.  Similarly, to select an outgoing edge, to push the item to, worker thread uses the method specified in `out_edge_selection` parameter. User can also provide a custom python function or a generator function instance to these parameters. User-provided function should return or yield an edge index. If the function depends on any of the node attributes, users can pass `None` to these parameters at the time of node creation and later initialise the parameter with the reference to the function. This is illustrated in the examples shown below. 
Various options available in the package for `in_edge_selection` and `out_edge_selection` include:

- "RANDOM": Selects a random out edge.
- "FIRST": Selects the first out edge.
- "LAST": Selects the last out edge.
- "ROUND_ROBIN": Selects out edges in a round-robin manner.
- "FIRST_AVAILABLE": Selects the first out edge that can accept an item.

 The worker thread picks an item and takes `processing_delay` amount of time to process the item. The parameter `processing_delay` can be specified as a constant value (`int` or `float`) or as a reference to a python function or a generator function instance that generates random variates from a chosen distribution. If the function depends on any of the node attributes, users can pass `None` to this parameter at the time of node creation and later initialise the parameter with the reference to the function. The worker thread does not have an any storage in it. 
 
 After processing the item, the worker thread behaves as follows:

1. If `blocking` is `True`, it pushes the item without checking whether the outgoing edge is full and waits for the outgoing edge to accept the item.

2. If `blocking` is `False`, it checks if there is space in the outgoing edge to accomodate the item. If the edge is full or unavailable, the item is discarded.

 The machine can parallely process `work_capacity` number of items. The machine spawns `work_capcity` number of workers that repeats all the activities from picking an item from a chosen incoming edge, processing it and pushing it out to the next chosen outgoing edge. 
 
 **States**
 
 During its operation, machine transitions through the following states:

1. "SETUP_STATE": Initialization or warm-up phase before item processing starts.

2. "IDLE_STATE": When the machine doesnot have any item to process as the incoming edge is empty

3. "PROCESSING_STATE": Active state where items are being processed.

4. "BLOCKED_STATE": The machine is blocked, when the incoming edge is full or unavilable .

**Usage**

A machine can be initialised as below.

```python
import factorysimpy
from factorysimpy.nodes.machine import Machine

MACHINE1 = Machine(
    env,                        # Simulation environment
    id="MACHINE1",                    # Unique identifier for the machine node
    work_capacity=4,            # Max number of items that can be processed simultaneously
    store_capacity=5,           # Max number of items that can be stored in the machine's internal store
    processing_delay=1.2,       # Processing delay (constant or generator/function)
    in_edge_selection="FIRST",  # Policy or function to select incoming edge
    out_edge_selection="FIRST"  # Policy or function to select outgoing edge
)
```

**Statistics collected**

The machine component reports the following key metrics. 

1. Total number of items processed
2. Time spent in each state 

Consider a machine with `work_capacity`=`2`, `blocking`= `False` and and instance name as MACHINE1. Metrics of a component MACHINE1 can be accessed after completion of the simulation run as

```python


print(f"Total number of items processed by worker thread 1 of {MACHINE1.id}={MACHINE1.stats[1]["num_items_processed"]}")
print(f"Total number of items discarded by worker thread 1 of {MACHINE1.id}={MACHINE1.stats[1]["num_items_discarded"]}")
print(f"Total number of items processed by worker thread 2 of {MACHINE1.id}={MACHINE1.stats[1]["num_items_processed"]}")
print(f"Total number of items discarded by worker thread 2 of {MACHINE1.id}={MACHINE1.stats[1]["num_items_discarded"]}")
print(f"Machine {MACHINE1.id}, worker1 state times: {MACHINE1.stats[1]["time_spent_in_states"]}")
print(f"Machine {MACHINE1.id}, worker2 state times: {MACHINE1.stats[1]["time_spent_in_states"]}")

```





**Examples**



- ***[A simple example with all parameters passed as constants](examples.md/#a-simple-example)***

- ***[An example with `processing_delay` passed as a reference to a generator function instance that generates random variates from a chosen distribution](examples.md/#example-with-delay-as-random-variates)***

- ***[An example with `out_edge_selection` and `in_edge_selection` parameter is passed as custom function that yields edge indices](examples.md/#example-with-a-custom-edge-selction-policy-as-a-function)***



<hr style="height:2px;border:none;color:blue; background-color:grey;" />

### Split
<hr style="height:2px;border:none;color:blue; background-color:grey;" />

Split represents entities that performs actions like unpacking, splitting etc. It can have multiple incoming edges and multiple outgoing edges.

The API documentation can be found in [Split](split.md)

<hr style="height:2px;border:none;color:blue; background-color:grey;" />

### Joint
<hr style="height:2px;border:none;color:blue; background-color:grey;" />
The API documentation can be found in [Joint](joint.md)

<hr style="height:2px;border:none;color:blue; background-color:grey;" />

### Sink
<hr style="height:2px;border:none;color:blue; background-color:grey;" />


 A Sink is a terminal node that collects flow items at the end. Once an item enters the sink, it is considered to have exited the system and cannot be retrieved or processed further. This sink can have multiple input edges and no output edges. It only has a single state "COLLECTING_STATE". The API documentation can be found in [Sink](sink.md)


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


During a simulation run, `src_node` puts an item into the buffer and the item gets available after delay amount of time for the `dest_node`. It operates in two modes- First In First Out(FIFO) or Last In First Out(LIFO). The number of items that a buffer can hold at any time can be specified using the parameter `store_capacity`. Buffer uses `ReservablePriorityReqFilterStore` as the inbuiltstore. In "FIFO" `mode`, it uses an additional filter to return the item which is added recently. Buffer transitions through the following states during simulation 

1. "EMPTY_STATE"  : when there is no items in the buffer
2. "RELEASING_STATE". When there is items.


**Monitoring and Reporting**
The buffer component reports the following key metrics:

1. Time averaged number of items available in buffer.
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


<hr style="height:4px;border:none;color:blue; background-color:grey;" />

## Item
<hr style="height:4px;border:none;color:blue; background-color:grey;" />

**About**

The `Item` class represents the discrete entities that flow through the system. Each item is created by a source node and is then processed, transferred, or collected by various nodes and edges as it moves through the simulation. The `Item` object tracks its movement, including timestamps for creation, entry and exit at each node, and destruction, as well as the time spent at each node.

**Basic attributes**

- `id` - Unique identifier for the item.
- `timestamp_creation` - Time when the item was created.
- `timestamp_destruction` - Time when the item was destroyed (e.g., collected by a sink).
- `timestamp_node_entry` - Time when the item entered the current node.
- `timestamp_node_exit` - Time when the item exited the current node.
- `current_node_id` - The ID of the node the item is currently in.
- `source_id` - The ID of the source node that created the item.
- `payload` - Optional data carried by the item.
- `destructed_in_node` - The node where the item was destroyed.


**Behavior**

When an item is created, its creation time and source node are recorded. As the item enters and exits nodes, the `update_node_event` method updates entry/exit times and accumulates the time spent at each node in the `stats` dictionary. When the item is destroyed (e.g., collected by a sink), the destruction time and node are recorded.

**Usage**

An item is typically created inside a source node and then passed through the system. The source node should call `set_creation` to record the creation time and source. Each node should call `update_node_event` when the item enters or exits, and the sink or terminal node should call `set_destruction` to record when and where the item is destroyed.

```python
from factorysimpy.helper.item import Item

# Create an item in the source node
item = Item("item1")
item.set_creation(source_id="SRC1", env=env)

# When item enters a node
item.update_node_event(node_id="MACHINE1", env=env, event_type="entry")

# When item exits a node
item.update_node_event(node_id="MACHINE1", env=env, event_type="exit")

# When item is destroyed (e.g., in a sink)
item.set_destruction(node_id="SINK1", env=env)
```

**Statistics collected**

The `Item` class tracks:

1. Creation and destruction times.
2. The node where the item was created and destroyed.
3. Time spent at each node (accessible via the `stats` dictionary).

This information can be used for detailed analysis of item flow and performance in the simulation.

<hr style="height:4px;border:none;color:blue; background-color:grey;" />