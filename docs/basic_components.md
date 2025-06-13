# Basic Components


Node, Edge and BaseFlowItem are the 3 basic component types in the library. All the other components are derived from them. Nodes are the active, static elements in the system and are responsible for operations such as processing, splitting, or combining items. Every node maintains a list of `in_edges` and `out_edges`, which are references to edge objects that connect it to other nodes. Other parameters of Nodes are `id` (a unique name) and `node_setup_time` (initial delay in each node, which is be a constant value). Common node types include Machine, Split, Joint, Source, and Sink. Source can be used to generate items that flow in the system. Machines are the entities that modifies/processes an item. To multiplex the items that flow in the system, Splits can be used and to pack/join items from different incoming edges a Joint can be used. Sink is the terminal node in the system and the items that enter this node cannot be retrieved.


Edges are passive components that connect exactly two nodes (src_node and dest_node) and helps in transfering items between them. Edges are directed. Each edge has a unique identifier called `id`, and parameters `src_node` and `dest_node` to store the reference to the source node and destination node. Specific types of edges include Buffer, Conveyor, and Fleet. Buffers act as queues with a defined delay. Conveyors move items between nodes while preserving order and support both discrete (slotted belts) and continuous motion. Fleets represent systems like warehouse robots or human operators that transport items between nodes without preserving order.

BaseFlowItem represents the entities that flow in the system. Every baseflowitem has a unique `id`. There are mainly two two of flow items available specified as `flow_item_type`. It can be either item or a pallet. Item is the smallest unit of discrete items that flow in the system.
Pallets represents enitities that can hold multiple base items that belong to `flow_item_type`- "items".  


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

**Basic attributes**

- `id` - unique identifier of the node
- `in_edges`- list of all the incoming edges to the node
- `out_edges` -  list of all the outgoing edges from the node
- `node_setup_time`- an initial delay to set up the node. 


<hr style="height:2px;border:none;color:grey; background-color:grey;" />

### Source
<hr style="height:2px;border:none;color:grey; background-color:grey;" />

**About**

The source is an active component that generates items that flow through the system. There are two modes of operation for the source. If the parameter `blocking` is set to True, the source generates an item and tries to send it to the connected output edge. If the edge is full or cannot accept the item, the source waits until space becomes available. If the `blocking` parameter is set to False, the source generates items and attempts to send them to the output edge. If the edge is full or cannot accept the item, the source discards the item. The API documentation can be found in [Source](source.md). 

**Basic attributes**

- `state` - Current state of the component.
- `inter_arrival_time`- Time interval between two successive item generation.
- `flow_item_type` - This is the type of item the source should generate. Either "item" or "pallet".
- `blocking` -  If True, waits for outgoing edge to accept item; if False, discards the item if the outgoing edge if full.
- `out_edge_selection`- Edge selection policy as a function to select outgoing edge.

**Behavior**

At the start of the simulation, the source waits for `node_setup_time`. This is an initial, one-time wait time for setting up the node and should be provided as a constant (an `int` or `float`).

During a simulation run, the source generates items at discrete instants of time determined by the parameter `inter_arrival_time`. [More details on how to configure parameter `inter_arrival_time` can be found here](configuring_parameters.md/#delay-parameters). After the wait it produces a flow item based on the type mentioned in `flow_item_type`. It can be of two type namely "item" and "pallet". Item represents the smallest unit of discrete items that flow in the system. Pallets represents the type of flow item that can hold multiple items inside and it can be used to pack items. The source can have multiple output edges. It chooses an output edge from `out_edges` list based on the `out_edge_selection` parameter. [More details on the parameter `out_edge_selection` can be found here](configuring_parameters.md/#edge-selection).


After generating an item and choosing an output edge, the source behaves as follows:

1. If `blocking` is `True`, it waits with the processed item in a "BLOCKED_STATE" for the out edge to be available and pushes the item when output edge becomes available or has space.
2. If `blocking` is `False`, it checks if there is space in the outgoing edge to accomodate the item. If the edge is full or unavailable, the item is discarded and the count of discarded item is recorded.






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
    flow_item_type="item",      # Type of baseflowitem that the source should generate
    blocking=False,             # If True, waits for outgoing edge to accept item; if False, discards item if the outgoing edge is full
    out_edge_selection=0        # Strategy or function to select outgoing edge (can be string or callable or genrator or a constant int)
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

- ***[An example with `inter_arrival_delay` passed as a normal python function that returns random variates from a chosen distribution](examples.md/#example-with-delay-as-random-variates)***

- ***[An example with `out_edge_selection` parameter is passed as custom function that yields edge indices](examples.md/#example-with-a-custom-edge-selction-policy-as-a-function)***



<hr style="height:2px;border:none;color:blue; background-color:grey;" />

### Machine
<hr style="height:2px;border:none;color:blue; background-color:grey;" />

**About**
A machine is an active component that processes items flowing through the system. Each item incurs a `processing_delay` amount of time to get processed in the machine. A machine can have multiple `in_edges` and `out_edges`. A machine can process multiple items simultaneously. The parameter `work_capacity` indicates the maximum number of items that can be processed simulatanously inside the machine. If work_capacity is set to a number greater than 1 (eg 3), this represents a machine with a maximum of 3 worker processes that are capable of processing 3 worker threads simultaneously. The `processing_delay` can be defined as a constant or defined as a random variate implemented as a python function or a generator function. Machine has two modes of operation based on the parameter value specified in `blocking`. If it is set to `True`, the processed item is held in a blocked state and machine waits for the out edge to be available to accept the item and pushes the processed item to the chosen out edge once it is available. The other mode can be configured by setting `blocking` to `False`. In this mode , the machine checks if there is space available in the chosen outgoing edge and only if there is space the item is pushed. If the outgoing edge is unavailable or full, the item will be discarded and its count will be recorded. The API documentation can be found in [Machine](machine.md)

**Basic attributes**

- `work_capacity` - Maximum number of items that can be processed by the machine simulataneously.
- `processing_delay`- Time taken to process an item.
- `state` - This is the state per working thread. This is a dictionary where each key is a worker thread's ID (assigned in order of initialization), and the value is the current state of that worker.
- `blocking`-  If True, waits for outgoing edge to accept item; if False, discards the item if the outgoing edge is full.
- `in_edge_selection`- Edge selection policy as a function to select input edge.
- `out_edge_selection`- Edge selection policy as a function to select output edge.

**Behavior**

At the start of the simulation, the machine waits for `node_setup_time`. This is an initial, one-time wait time for setting up the node and should be provided as a constant (an `int` or `float`).  Machine can process atmost `work_capacity` number of items in parallel. As soon as an item is input, a worker thread is reserved which remains busy for processing the item in `processing_delay` amount of time and at the end of this time the worker thread attempts to output the item to one of the `out_edges` selected using the `out_edge_selection` parameter. [More details on how to configure the parameters `processing_delay`, `out_edge_selection` and `in_edge_selection` can be found here](configuring_parameters.md). Multiple items can be in "PROCESSING_STATE" at a time. After processing the item, the worker thread behaves as follows:

1. If `blocking` is `True`, it waits with the processed item in a "BLOCKED_STATE" for the out edge to be available and pushes the item when output edge becomes available or has space.
2. If `blocking` is `False`, it checks if there is space in the outgoing edge to accomodate the item. If the edge is full or unavailable, the item is discarded and the count of discarded item is recorded.


 
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
    processing_delay=1.2,       # Processing delay (constant or generator/function)
    blocking=False,             # If True, waits for outgoing edge to accept item; if False, discards item if the outgoing edge is full
    in_edge_selection="RANDOM",  # Policy or function to select incoming edge
    out_edge_selection="RANDOM"  # Policy or function to select outgoing edge
)
```

**Statistics collected**

The machine component reports the following key metrics. 

1. Total number of items processed
2. total time in PROCESSING_STATE (per thread)
3. Total time spent in BLOCKED_STATE (per thread)
4. Occupancy of the worker threads
5. Total number if items discarded (when `blocking`= False)

Consider a machine with `work_capacity`=`2`, `blocking`= `False` and and instance name as MACHINE1. Metrics of a component MACHINE1 can be accessed after completion of the simulation run as

```python


print(f"Total number of items processed by worker thread 1 of {MACHINE1.id}={MACHINE1.stats["num_items_processed"]}")
print(f"Total number of items discarded by worker thread 1 of {MACHINE1.id}={MACHINE1.stats["num_items_discarded"]}")
print(f"Total number of items processed by worker thread 2 of {MACHINE1.id}={MACHINE1.stats["num_items_processed"]}")
print(f"Total number of items discarded by worker thread 2 of {MACHINE1.id}={MACHINE1.stats["num_items_discarded"]}")
print(f"Machine {MACHINE1.id},total time in BLOCKED_STATE (per thread) : {MACHINE1.per_thread_total_time_in_blocked_state}")
print(f"Machine {MACHINE1.id},total time in PROCESSING_STATE (per thread) : {MACHINE1.per_thread_total_time_in_processing_state}")
print(f"Worker occupancy, {MACHINE1.time_per_work_occupancy)})

```





**Examples**



- ***[A simple example with all parameters passed as constants](examples.md/#a-simple-example)***

- ***[An example with `processing_delay` passed as a reference to a generator function instance that generates random variates from a chosen distribution](examples.md/#example-with-delay-as-random-variates)***

- ***[An example with `out_edge_selection` and `in_edge_selection` parameter is passed as custom function that yields edge indices](examples.md/#example-with-a-custom-edge-selction-policy-as-a-function)***



<hr style="height:2px;border:none;color:blue; background-color:grey;" />

### Joint
<hr style="height:2px;border:none;color:blue; background-color:grey;" />

**About**

The `Joint` component represents a node that combines or packs items from multiple incoming edges into a single pallet or box, and then pushes the packed pallet to an outgoing edge. It is useful for modeling operations such as packing, assembly, or combining flows from different sources. The number of items to be taken from each incoming edge can be specified, and the first incoming edge is expected to provide the pallet or container. A joint can process more than one item simultaneously and this number can be set using parameter `work_capacity`. Joint creates that many worker threads to mimic its actions. The API documentation can be found in [Joint](joint.md)

**Basic attributes**

- `state` - current state of the component. This is a dictionary where each key is a worker thread's ID (assigned in order of initialization), and the value is the current state of that worker.
- `processing_delay` - time taken to process and pack the items
- `work_capacity` - maximum number of jobs or pallets that can be processed simultaneously
- `blocking` - if True, waits for outgoing edge to accept the packed pallet; if False, discards the pallet if the outgoing edge is full
- `target_quantity_of_each_item` - list specifying how many items to take from each incoming edge (first entry is always 1 for the pallet)
- `out_edge_selection` - edge selection policy as a function to select outgoing edge

**Behavior**
 At the start of the simulation, the joint waits for `node_setup_time`. This is an initial, one-time wait time for setting up the node and should be provided as a constant (an `int` or `float`). Then it spawns `work_capacity` number of threads.
 Each worker thread then repeatedly:

1. Pulls a pallet from the first incoming edge.
2. Pulls the specified number of items from each of the other incoming edges and adds them to the pallet.
3. Waits for `processing_delay` to simulate packing/combining.
4. Pushes the packed pallet to the outgoing edge, either waiting if `blocking` is True or discarding if the edge is full and `blocking` is False.

To select an outgoing edge, to push the item to, worker thread uses the method specified in `out_edge_selection` parameter. User can also provide a custom python function or a generator function instance to these parameters. User-provided function should return or yield an edge index. If the function depends on any of the node attributes, users can pass `None` to these parameters at the time of node creation and later initialise the parameter with the reference to the function. This is illustrated in the examples shown below. 
Various options available in the package for `out_edge_selection` include:

- "RANDOM": Selects a random out edge.
- "ROUND_ROBIN": Selects out edges in a round-robin manner.
- "FIRST_AVAILABLE": Selects the first out edge that can accept an item.

**States**

During its operation, the joint transitions through the following states:

1. "SETUP_STATE": Initialization or warm-up phase before packing starts.
2. "IDLE_STATE": Waiting to receive a pallet and items.
3. "PROCESSING_STATE": Actively packing items into the pallet.
4. "BLOCKED_STATE": Blocked, waiting for the outgoing edge to accept the packed pallet.

**Usage**

A joint can be initialized as below:

```python
import factorysimpy
from factorysimpy.nodes.joint import Joint

JOINT1 = Joint(
    env,                              # Simulation environment
    id="JOINT1",                      # Unique identifier for the joint node
    target_quantity_of_each_item=[1, 2],  # 1 pallet from in_edges[0], 2 items from in_edges[1]
    work_capacity=1,                  # Number of pallets that can be packed simultaneously
    processing_delay=1.5,             # Packing delay (constant or generator/function)
    blocking=True,                    # Wait for outgoing edge to accept pallet
    out_edge_selection="RANDOM"        # Policy or function to select outgoing edge
)
```


**Statistics collected**

The joint component reports the following key metrics:

1. Total number of pallets packed and pushed
2. Number of pallets/items discarded (non-blocking mode)
3. Time spent in each state

After the simulation run, metrics can be accessed as:

```python
print(f"Total number of pallets processed by worker 1 of {JOINT1.id} = {JOINT1.stats[1]['num_item_processed']}")
print(f"Total number of pallets discarded by worker 1 of {JOINT1.id} = {JOINT1.stats[1]['num_item_discarded']}")
print(f"Joint {JOINT1.id}, worker1 state times: {JOINT1.stats[1]['total_time_spent_in_states']}")
```

**Examples**

- ***[An example of a joint node combining items from two sources](examples.md/#example-to-illustrate-the-use-of-the-components-split-and-joint)***

<hr style="height:2px;border:none;color:blue; background-color:grey;" />

### Split
<hr style="height:2px;border:none;color:blue; background-color:grey;" />


**About**

The `Split` component represents a node that unpacks or splits an incoming item (such as a pallet or batch) and sends its contents to multiple outgoing edges. It is useful for modeling operations such as unpacking, sorting, or distributing items from a container to different destinations.  A split can process more than one pallet or jobs simultaneously and this number can be set using parameter `work_capacity`. Split creates that many worker threads to mimic its actions. The incoming edge is selected according to the `in_edge_selection` policy, and the outgoing edge for each unpacked item is selected according to the `out_edge_selection` policy. The API documentation can be found in [Split](split.md)

**Basic attributes**

- `state` - current state of the component. This is a dictionary where each key is a worker thread's ID (assigned in order of initialization), and the value is the current state of that worker.
- `processing_delay` - time taken to process and unpack the items
- `work_capacity` - number of worker threads that can process items or jobs concurrently
- `blocking` - if True, waits for outgoing edge to accept the item; if False, discards the items if the outgoing edge is full
- `in_edge_selection` - edge selection policy as a function to select incoming edge
- `out_edge_selection` - edge selection policy as a function to select outgoing edge

**Behavior**

At the start of the simulation, the split waits for `node_setup_time`. Each worker thread then repeatedly:

1. Pulls a packed item (e.g., pallet) from the selected incoming edge.
2. Waits for `processing_delay` to simulate unpacking or splitting.
3. Unpacks the items from the pallet and pushes each item to an outgoing edge, one by one, using the `out_edge_selection` policy.
4. After all items are pushed, the empty container itself is pushed to an outgoing edge.
5. If `blocking` is True, the split waits for the outgoing edge to accept each item; if `blocking` is False, items are discarded if the outgoing edge is full.

To select an outgoing edge and incoming edge, worker thread uses the method specified in `out_edge_selection` and `in_edge_selection` parameters. User can also provide a custom python function or a generator function instance to these parameters. User-provided function should return or yield an edge index. If the function depends on any of the node attributes, users can pass `None` to these parameters at the time of node creation and later initialise the parameter with the reference to the function. This is illustrated in the examples shown below. 
Various options available in the package for `in_edge_selection` and `out_edge_selection` include:

- "RANDOM": Selects a random out edge.
- "ROUND_ROBIN": Selects out edges in a round-robin manner.
- "FIRST_AVAILABLE": Selects the first out edge that can accept an item.


**States**

During its operation, the split transitions through the following states:

1. "SETUP_STATE": Initialization or warm-up phase before unpacking starts.
2. "IDLE_STATE": Waiting to receive a container/item.
3. "PROCESSING_STATE": Actively unpacking or splitting items.
4. "BLOCKED_STATE": Blocked, waiting for the outgoing edge to accept the item.

**Usage**

A split can be initialized as below:

```python
import factorysimpy
from factorysimpy.nodes.split import Split

SPLIT1 = Split(
    env,                        # Simulation environment
    id="SPLIT1",                # Unique identifier for the split node
    work_capacity=1,            # Number of worker threads
    processing_delay=1.0,       # Unpacking delay (constant or generator/function)
    blocking=True,              # Wait for outgoing edge to accept item
    in_edge_selection="RANDOM",  # Policy or function to select incoming edge
    out_edge_selection="ROUND_ROBIN"  # Policy or function to select outgoing edge
)
```

**Statistics collected**

The split component reports the following key metrics:

1. Total number of items unpacked and pushed
2. Number of items discarded (non-blocking mode)
3. Time spent in each state

After the simulation run, metrics can be accessed as:

```python
print(f"Total number of items processed by worker 1 of {SPLIT1.id} = {SPLIT1.stats[1]['num_item_processed']}")
print(f"Total number of items discarded by worker 1 of {SPLIT1.id} = {SPLIT1.stats[1]['num_item_discarded']}")
print(f"Split {SPLIT1.id}, worker1 state times: {SPLIT1.stats[1]['total_time_spent_in_states']}")
```

**Examples**

- ***[An example of a split node unpacking a pallet and distributing items to multiple destinations](examples.md/#example-to-illustrate-the-use-of-the-components-split-and-joint)***

<hr style="height:2px;border:none;color:blue; background-color:grey;" />

### Sink
<hr style="height:2px;border:none;color:blue; background-color:grey;" />


 A Sink is a terminal node that collects flow items at the end. Once an item enters the sink, it is considered to have exited the system and cannot be retrieved or processed further. The sink can have multiple input edges but no output edges. [More details on how to configure the parameter `out_edge_selection` can be found here](configuring_parameters.md) It only has a single state "COLLECTING_STATE". The API documentation can be found in [Sink](sink.md)
 

**Usage**

A split can be initialized as below:

```python
import factorysimpy
from factorysimpy.nodes.sink import Sink

SINK = SINK(
    env,                        # Simulation environment
    id="SINK",                # Unique identifier for the  node
    in_edge_selection="RANDOM",  # Policy or function to select incoming edge
    
)
```

 **Statistics collected**

The sink component reports the following key metrics. 

1. Total number of items received
2. sum of cycle times of all items received by the sink

Consider a sink with instance name as SINK. Its metrics can be accessed after completion of the simulation run as

```python


total= SINK.stats["num_item_received"]
cycle_time = SINK.stats["total_cycle_time"]/60
print(f"Average cycle time per item: {cycle_time/total if total > 0 else 0:.2f} minutes")
print(f"Total number of items received: {sink.stats}")

```

<hr style="height:3px;border:none;color: grey; background-color:grey; " />


## Edges
<hr style="height:3px;border:none;color: grey;background-color:grey; " />


Edges represent passive elements in the system. This is the basis for the components like Buffer, Conveyor, Fleet, etc. Every edge has a unique identifier named `id` and maintains references to a source node `src_node` and a destination node `dest_node`. Edge acts as a conntction between these two nodes and facilitates the movement of items between the nodes. 





<hr style="height:2px;border:none;color:blue; background-color:grey;" />

### Buffer
<hr style="height:2px;border:none;color:blue; background-color:grey;" />


**About**

The `Buffer` component represents a queue (FIFO or LIFO) that temporarily holds items between nodes in the system. It acts as an edge with internal storage, allowing items to be stored until the destination node is ready to accept them. Items placed in the buffer become available for retrieval after a specified `delay`. The buffer can operate in two modes:  
- **FIFO (First In First Out):** Oldest items are released first.  
- **LIFO (Last In First Out):** Newest items are released first.

The API documentation can be found in [Buffer](buffer.md)

**Basic attributes**

- `state` - current state of the buffer 
- `store_capacity` - maximum number of items the buffer can hold
- `mode` - mode of operation of the buffer. Either "FIFO" or "LIFO".
- `delay` - time after which an item becomes available for retrieval (can be a constant, generator, or callable)

**Behavior**

- When an item is put into the buffer, it is stored internally and becomes available for retrieval after the specified `delay`.
- The buffer has methods to check if it can accept new items using can_put method and if it can provide items to the next node using 
  can_get method.
- In FIFO mode, items are released in the order they were added; in LIFO mode, the most recently added items are released first.
- Incoming edges can use reserve_get and reserve_put calls on the store in the buffer to reserve an item or space and after yielding 
 the requests, an item can be put and obtained by using put and get methods. 

**States**


- The buffer transitions between states such as "IDLE_STATE" (waiting for items), "RELEASING_STATE" (releasing items), and "BLOCKED_STATE" (cannot accept or release items due to capacity or downstream constraints).

1. "EMPTY_STATE"  - when there is no items in the buffer
2. "RELEASING_STATE"- When there is items in the buffer



**Usage**

A buffer can be initialized as below:

```python
import factorysimpy
from factorysimpy.edges.buffer import Buffer

BUF1 = Buffer(
    env,                 # Simulation environment
    id="BUF1",           # Unique identifier for the buffer
    store_capacity=10,   # Maximum number of items in the buffer
    delay=2.0,           # Delay before items become available (can be int, float, generator, or callable)
    mode="FIFO"          # "FIFO" or "LIFO"
)
```

**Statistics collected**

The buffer component reports the following key metrics:

1. Time when the state was last changed (`last_state_change_time`)
2. Time-averaged number of items in the buffer (`time_averaged_num_of_items_in_buffer`)
3. Total time spent in each state (`total_time_spent_in_states`)

After the simulation run, metrics can be accessed as:

```python
print(f"Buffer {BUF1.id} last state change: {BUF1.stats['last_state_change_time']}")
print(f"Buffer {BUF1.id} time-averaged number of items: {BUF1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Buffer {BUF1.id} state times: {BUF1.stats['total_time_spent_in_states']}")
```

**Examples**

- ***[A simple example with a FIFO buffer between a source and a machine](examples.md/#a-simple-example)***





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

## BaseFlowItem
<hr style="height:4px;border:none;color:blue; background-color:grey;" />

This is base class for the items that flow in the system. 


**Basic attributes**

- `id` - Unique identifier for the pallet.
- `timestamp_creation` - Time when the pallet was created.
- `timestamp_destruction` - Time when the pallet was destroyed (e.g., collected by a sink).
- `timestamp_node_entry` - Time when the pallet entered the current node.
- `timestamp_node_exit` - Time when the pallet exited the current node.
- `current_node_id` - The ID of the node the pallet is currently in.
- `source_id` - The ID of the source node that created the pallet.
- `payload` - Optional data carried by the pallet.
- `destructed_in_node` - The node where the pallet was destroyed.


<hr style="height:4px;border:none;color:blue; background-color:grey;" />

### Item
<hr style="height:4px;border:none;color:blue; background-color:grey;" />

**About**

The `Item` class represents the discrete entities that flow through the system. Each item is created by a source node and is then processed, transferred, or collected by various nodes and edges as it moves through the simulation. The `Item` object tracks its movement, including timestamps for creation, entry and exit at each node, and destruction, as well as the time spent at each node.

**Basic attributes**


- `flow_item_type` - `"item"` type of the base flow item



**Behavior**

When an item is created, its creation time and source node are recorded. As the item enters and exits nodes, the `update_node_event` method updates entry/exit times and accumulates the time spent at each node in the `stats` dictionary. When the item is destroyed (e.g., collected by a sink), the destruction time and node are recorded.



**Statistics collected**

The `Item` class tracks:

1. Creation and destruction times.
2. The node where the item was created and destroyed.
3. Time spent at each node (accessible via the `stats` dictionary).

Consider that an item is created inside a source and it has finished its flow in the system. The statistics can be collected as f0llows

```python

item1 = Item(id= "item1")

for key, value in item1.stats:
    print("Time spent in node{key.id} is {value}")


```

<hr style="height:4px;border:none;color:blue; background-color:grey;" />

### Pallet
<hr style="height:2px;border:none;color:blue; background-color:grey;" />

**About**

The `Pallet` class represents a special type of item that can hold multiple other items. It is used to model containers, pallets, or boxes that group several items together for combined processing, transport, or packing/unpacking operations in the system. The `Pallet` object tracks its own journey through the system, just like a regular `Item`, and also maintains a list of the items it contains.

**Basic attributes**


- `flow_item_type` -  `"Pallet"` type of the base flow item
- `items` - List of items currently held in the pallet.


**Behavior**

- When a pallet is created, its creation time and source node are recorded.
- Items can be added to the pallet using the `add_item(item)` method.
- Items can be removed from the pallet using the `remove_item()` method, which returns an item or `None` if the pallet is empty.
- As the pallet enters and exits nodes, the `update_node_event` method updates entry/exit times and accumulates the time spent at each node in the `stats` dictionary.
- When the pallet is destroyed (e.g., collected by a sink), the destruction time and node are recorded.



**Statistics collected**

The `Pallet` class tracks:

1. Creation and destruction times.
2. The node where the pallet was created and destroyed.
3. Time spent at each node (accessible via the `stats` dictionary).
4. The number of items currently held in the pallet.


Consider that an pallet is created inside a source and it has finished its flow in the system. The statistics can be collected as f0llows

```python

pallet1 = Pallet(id= "pallet1")

for key, value in pallet1.stats:
    print("Time spent in node {key.id} is {value}")

```


<hr style="height:4px;border:none;color:blue; background-color:grey;" />