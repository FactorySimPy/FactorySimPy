# Basic Components

<p style="text-align: justify;">
Node, Edge and Item are the 3 basic component types in the library. All the other components are derived from these basic types.  Nodes are the active, static elements in the system and are responsible for operations such as processing, splitting, or combining items. Each node maintains a list of in_edges and out_edges, which are references to edge objects that connect it to other nodes. Other parameters of Nodes are id (an unique name) and node_setup_time (initial delay in each node, which can be a constant or an arbitrary  distribution that is specifies by pass the reference to a generator funtion). Common node types include Machine, Split, Joint, Source, and Sink. Source can be used to generate items that flow in the system. Machines are the entities that modifies/processes an item. To multiplex the items that flow in the system, Splits can be used and to pack/join items from different incoming edges a Joint can be used. Sink is the terminal node in the system and the items that enter this node cannot be retrieved.
</p>

<p style="text-align: justify;">
Edges are passive components that connect exactly two nodes(src_node and dest_node) and helps in transfering items between them. Edges are directed. Each edge has parameter capacity and methods like can_put, reserve_put, put, can_get, reserve_get, and get to control item movement. Specific types of edges include Buffer, Conveyor, and Fleet. Buffers act as FIFO queues with a defined delay. Conveyors move items between nodes while preserving order and support both discrete (slotted belts) and continuous motion. Fleets represent systems like warehouse robots or human operators that transport items between nodes without preserving order.
</p>



<!-- Here, is an example of a model with 3 nodes that are connected using 2 edges. Nodes are of type source, machine and sink and edges are of type conveyor.  -->

## System Description

**Rules for interconnection**

1. Nodes are static entities like machine, source, sink, split, joints, etc.
2. Edges are directed and connects one node to another. Conveyor, buffer and fleet are the entities that are of type Edge.
3. Items are discrete parts that flow in the system through the directed edges from one node to another. 
3. Each Node has two lists `in_edges` and `out_edges` that points to the references of the edges that comes in and go out of the node
4. Each Edge stores pointers to a `src_node` and a `dest_node`. An Edge can be used only to connect a single node(`src_node`) to another (or same) node(`dest_node`).
5. An Edge can have the same node in both `src_node` and `dest_node`. (ie, a node can be connected to itself)
6. Nodes are the active elements whose activites initiates state changes in the system.
7. Edges are the passive elements and state change occurs due to actions initiated by nodes
8. To split the output from a `machine` node into two streams, a `Split` must be connected to the `machine` using an Edge.
9. To join two streams and to feed as input to a `machine` node, a `Joint` must be connected to the `machine` using an Edge





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

<p style="text-align: justify;">
Nodes represent active elements in the system. This is a basic type and is the basis for the active components like Machine, Split, Sink, Source, Joint, etc. Every node has a unique identifier named `id` and maintains two lists named `in_edges` and `out_edges`. Every node has a `node_setup_time` that can be specified as a constant delay or a reference to a generator function or a normal function that represents an arbitrary distribution.
</p>

### Source

<p style="text-align: justify;">
Source is responsible for generating items that enter and flow through the system. 
There are two variants of sources available:
</p>
**Blocking**: This variant generates an item and attempts to send it to the connected outgoing edge. If the edge is full or unable to accept the item, the source will wait until space becomes available.

**Non-blocking**: This variant generates items, but if the outgoing edge is full or unable to accept the item, the item is immediately discarded rather than waiting.

**Behavior**

During a simulation run, the Source component repeatedly generates items at intervals defined by `inter_arrival_time`. This delay can be specified as a fixed constant or as a reference to a generator function representing an arbitrary distribution.
After generating an item, the source behaves as follows:

1. If the source is `blocking`, it waits until the outgoing edge becomes available before pushing the item.

2. If the source is `non-blocking`, it checks the availability of the outgoing edge. If the edge is full or unavailable, the item is discarded.

The source then waits for the next inter_arrival_time before attempting to generate the next item. Source can be connected to multiple outgoing edges. To control how the next edge is selected for item transfer, desired strategy can be specified using the `out_edge_selection` parameter. Various options available are `RANDOM`, `FIRST`, `LAST`,`ROUND_ROBIN`, `FIRST_AVAILABLE`, etc. During its operation, the source transitions through the following states:

1. `SETUP_STATE`: Initialization or warm-up phase before item generation starts.

2. `GENERATING_STATE`: Active state where items are being created and pushed to the system.

3. `BLOCKED_STATE`: The source is blocked, waiting for the outgoing edge to accept an item (only in blocking mode).



**Monitoring and Reporting**
The source component reports the following key metrics:

1. Total number of items generated
2. Number of items discarded (non-blocking mode)
3. Time spent in each state 

These metrics help in analyzing the performance and efficiency of the item generation process within the simulation model.

### Machine
Machine is a component that has a processing delay and processes/modifies items that flow in the system. It can have multiple incoming edges and outgoing edges. It gets an item from one of its in edges and processes the item in a `processing_delay` amount of time and pushes the item to one of its out edges. 


**Behavior**
During a simulation run, Machine gets object from one of the in_edges. To choose an incoming edge, to pull the item from, the Machine utilises the strategy specified in the parameter `in_edge_selection`. Various options available are  `RANDOM`, `FIRST`, `LAST`,`ROUND_ROBIN`, `FIRST_AVAILABLE`, etc. Similarly, to select and outgoing edge, to push the item to, Machine uses the method specified in `out_edge_selection` parameter. Machine picks an item and takes `processing_delay` amount of time to process the item and puts it inside the inbuiltstore. The capacity of this store can be specified in the parameter `store_capacity`. Machine can parallely process `work_capacity` number of items. But, if `work_capacity` > `store_capacity`, then `work_capacity` is set to `store_capacity`. During its operation, Machine transitions through the following states: `SETUP_STATE`, `PROCESSING_STATE`, `BLOCKED_STATE`, and `IDLE_STATE`.

**Monitoring and Reporting**
The Machine component reports the following key metrics:

1. Total number of items processed
2. Time spent in each state 


### Split

### Joint

### Sink


## Edge

### Buffer

### Conveyor

