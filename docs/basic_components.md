# Basic Components


Node, Edge and Item are the 3 basic component types in the library. All the other components are derived from these basic types.  Nodes are the active, static elements in the system and are responsible for operations such as processing, splitting, or combining items. Each node maintains a list of in_edges and out_edges, which are references to edge objects that connect it to other nodes. Other parameters of Nodes are id (an unique name) and node_setup_time (initial delay in each node, which can be a constant or an arbitrary  distribution that is specifies by pass the reference to a generator funtion). Common node types include Machine, Split, Joint, Source, and Sink. Source can be used to generate items that flow in the system. Machines are the entities that modifies/processes an item. To multiplex the items that flow in the system, Splits can be used and to pack/join items from different incoming edges a Joint can be used. Sink is the terminal node in the system and the items that enter this node cannot be retrieved.



Edges are passive components that connect exactly two nodes(src_node and dest_node) and helps in transfering items between them. Edges are directed. Each edge has parameter capacity and methods like can_put, reserve_put, put, can_get, reserve_get, and get to control item movement. Specific types of edges include Buffer, Conveyor, and Fleet. Buffers act as FIFO queues with a defined delay. Conveyors move items between nodes while preserving order and support both discrete (slotted belts) and continuous motion. Fleets represent systems like warehouse robots or human operators that transport items between nodes without preserving order.








**Rules for interconnection**

1. Nodes are static entities like Machine, Source, Sink, Split, Joints, etc.
2. Edges are directed and connects one node to another. Conveyor, buffer and fleet are the entities that are of type Edge.
3. Items are discrete parts that flow in the system through the directed edges from one node to another. 
3. Each Node has two lists `in_edges` and `out_edges` that points to the references of the edges that comes in and go out of the node.
4. Each Edge stores pointers to a `src_node` and a `dest_node`. An Edge can be used only to connect a node to another or same node.
5. An Edge can have the same node in both `src_node` and `dest_node`.
6. Nodes are the active elements whose activites initiates state changes in the system.
7. Edges are the passive elements and state change occurs due to actions initiated by nodes.
8. To split the output from a `Machine` node into two streams, a `Split` must be connected to the `Machine` using an Edge.
9. To join two streams and to feed as input to a `Machine` node, a `Joint` must be connected to the `Machine` using an Edge.





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


Nodes represent active elements in the system. This is a basic type and is the basis for the active components like Machine, Split, Sink, Source, Joint, etc. Every node has a unique identifier named `id` and maintains two lists named `in_edges` and `out_edges`. Every node has a `node_setup_time` that can be specified as a constant delay or a reference to a generator function or a normal function that represents an arbitrary distribution.


### Source


Source is responsible for generating items that enter and flow through the system. 
There are two variants of sources available:


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

<p style="text-align: justify;">
 A Sink is a terminal node that collects flow items at the end. Once an item enters the Sink, it is considered to have exited the system and cannot be retrieved or processed further. This sink can have multiple input edges and no output edges. It has a unique identifier. It only has a single state `COLLECTING_STATE`.
</p>

## Edge

<p style="text-align: justify;">
Edges represent passive elements in the system. This is the basis for the components like Buffer, Conveyor, Fleet, etc. Every edge has a unique identifier named `id` and maintains references to a source node `src_node` and a destination node `dest_node`. Edge acts as a conntction between these two nodes and facilitates the movement of items between the nodes. Every edge has a `edge_setup_time` that can be specified as a constant delay or a reference to a generator function or a normal function that represents an arbitrary distribution.
</p>

### Buffer

<p style="text-align: justify;">
Buffer is a type of edge that represents a queue to store items that wait to be accepted by a downstream component.
This helps to remove the bottlenecks that come when the processing delays of nodes are not matching and one processes faster than the other. It has two modes of operation that are FIFO and LIFO. 

</p>
**Behavior**

<p style="text-align: justify;">
During a simulation run, `src_node` puts an item into the buffer and the item gets available after delay amount of time for the `dest_node`. It operates in two modes- First In First Out(FIFO) or Last In First Out(LIFO). The number of items that a buffer can hold at any time can be specified using the parameter `store_capacity`. Buffer transitions through the following states during simulation- `EMPTY_STATE` AND `RELEASING_STATE`.
</p>
**Monitoring and Reporting**
The Machine component reports the following key metrics:

1. time averaged number of items available in buffer.
2. Time spent in each state 

### Conveyor

<p style="text-align: justify;">
Conveyor connects two nodes and moves items from one end to the other 
There are two variants of conveyor available:
</p>

**Slotted-type**: This variant moves items from one end to the other at fixed interval. There is a constant delay between two movements. The `capacity` of slotted-type conveyor is the number of slots available in it and cn hold up to `capacity` number of items at a time.

**Constant speed conveyors**: This variant moves items at a constant speed. It can only be used to move discrete items. It also has a `capacity` to specify the maximum number of items that it can hold at any given time.

Conveyors can be either `blocking` or `non-blocking`:

1. A `blocking` type conveyor is also known as `non-accumulating` conveyor, such conveyor will not allow `src_node` to push items into the conveyor, if it is in a blocked state

2. A `non-blocking`(`accumulating`) conveyor allows src_node to push items until its capacity is reached when when it is in blocked state.

**Behavior**
<p style="text-align: justify;">
During a simulation run, the Conveyor gets an item and as soon as it gets an item it starts moving and after moving it waits delay amount of time before the next move. It moves until the first item reaches the other end of the belt. If item is not taken out by a dest_npde, then conveyor will be in `BLOCKED_STATE`. During its operation, the source transitions through the following states:
</p>
1. `SETUP_STATE`: Initialization or warm-up phase.

2. `MOVING_STATE`: state when the belt is moving.

3. `BLOCKED_STATE`: IT is blocked, waiting for the dest_node to taken an item ouy.



**Monitoring and Reporting**
The component reports the following key metrics:

1. Time averaged number of items 
3. Time spent in each state 

