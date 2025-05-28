
# Discrete event Simulation for Manufacturing
## Overview
<p style="text-align: justify;">
FactorySimPy is an open-source, light-weight Python library for modeling and discrete-event simulation (DES) of manufacturing systems. It provides a well-defined set of canonical components commonly found in a manufacturing setting—such as machines with configurable processing delays, joints that packs/joins items from multiple inputs, buffers that operate as FIFO queues, etc. These components come with pre-built behavior that is easily configurable, enabling users to rapidly construct simulation models. To use the library, users define the structure of the system and specify the parameters for each component. The modular design allows users to extend functionality by subclassing existing components, making the library extensible and reusable. Built on top of SimPy 4, FactorySimPy supports both "as fast as possible" and real-time simulation modes. It is currently designed for discrete-item flow systems where the model structure remains fixed during the simulation. Future development plans include extending support to material flows.

</p>





## Model Description
<p style="text-align: justify;">
The system is modeled as a graph consisting of two types of components: Nodes and Edges. Nodes represent active components that drive state changes—such as machines that introduce delays by performing operations like packing, unpacking, or modifying items. Edges, in contrast, represent passive components such as conveyor belts, human operators, warehouse robots, or transport vehicles that facilitate the movement of items between nodes.
</p>

<p style="text-align: justify;">
Each Node maintains two lists: in_edges and out_edges, representing incoming and outgoing connections, respectively. An Edge connects exactly two Nodes and holds direct references to its src_node (source node) and dest_node (destination node). It acts as an out_edge for the source node and an in_edge for the destination node. The graph supports both loops and self-loops, with each Edge uniquely associated with one source and one destination node—even if both refer to the same Node in the case of a self-loop.
</p>
<p style="text-align: justify;">
State transitions in the simulation are triggered solely by the actions of the Nodes, ensuring a clear separation between control (Nodes) and transport (Edges) within the model.
</p>


### Example Representation
An example model with 2 nodes and a directed edge

<!--- ![Alt text](images/gr_2nodes.jpg) --->
<img src="images/gr_2nodes.jpg" alt="System Architecture Diagram showing Nodes and Edges" width="400" height="10"/>


---

## Component Design:Important Classes

<p style="text-align: justify;">
Node, Edge and Item serves as the base classes. Item class represents the entities that flow in the system and get modified or processed. Nodes are the active, static elements in the system and are responsible for operations such as processing, splitting, or combining items. Each node maintains a list of in_edges and out_edges, which are references to edge objects that connect it to other nodes. Nodes also have parameters such as a unique name, work_capacity (the maximum number of items that can be processed simultaneously), delay (the processing time per item, which can be a constant or a random generator), and store_capacity (the number of items that can be held internally). Common node types include machine, Split, Joint, Source, and Sink.
</p>

<p style="text-align: justify;">
Edges are passive components that connect exactly two nodes: a source_node and a dest_node. Each edge has parameter capacity and methods like can_put, reserve_put, put, can_get, reserve_get, and get to control item movement. Specific types of edges include Buffer, Conveyor, and Fleet. Buffers act as FIFO queues with a defined delay. Conveyors move items between nodes while preserving order and support both discrete (slotted belts) and continuous motion. Discrete conveyors operate in fixed stages defined by delay_per_slot, while continuous conveyors move items at a fixed speed. Conveyors can be accumulating(non-blocking)—allowing multiple items to queue if the output is blocked—or non-accumulating(blocking), which donot accept any item unless the initial position is empty. Conveyors are characterized by parameters such as capacity, occupancy, and state(moving, stalled, or empty).
</p>

<p style="text-align: justify;">
Fleets represent systems like warehouse robots or human operators that transport items between nodes without preserving order. A fleet is characterized by its size (number of carriers), delay (fixed or variable), and state for each carrier, which can be either moving or idle. These components together define a flexible and modular system for modeling material flow in discrete-event simulation.
</p>
 

<!-- Here, is an example of a model with 3 nodes that are connected using 2 edges. Nodes are of type source, machine and sink and edges are of type conveyor.  -->

## System Description

### Rules for interconnection
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



<!-- <img src="images/split.jpg" alt="System Architecture Diagram showing Nodes and Edges" width="400" height="10"/>

<img src="images/joint.jpg" alt="System Architecture Diagram showing Nodes and Edges" width="400" height="10"/> -->

### Steps for Connecting Components
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
   e2.connect(n2,n3)
   ```

---

## **Class Hierarchy**
```
├── Node(Base Class for components that processes items)
    ├── Machine     # Processes items 
    ├── Joint      # Merges multiple flows into one
    ├── Split       # Splits a flow into multiple branches.
    ├── Sink        # Consumes items
    ├── Source       # generates items
  

├── Edge(Base Class for components that transfer items from one node to another)
    ├── Conveyor   # transfers items in a sequence from a node to another and order is preserved
    ├── Fleet      # Fleet of human operstor, warehouse robots or transport vehicles
    ├── Buffer     # Queue of items waiting to be accepted by the next node in a model

```





## Behavior of Components



---



### **Node** \( N \):
- **Purpose**: class to represent active elements in the system.  
- **Parameters**
     - `id`: unique identifier of a node
     - `in_edges`: list of input edges to the node
     - `out_edges`: list of output edges of the node
     - `node_setup_time`: Time for intial set up.

### Derived Classes from Node 
  1. **Source** \( N_src \):
     - **Purpose**: class to generate flow items in the simulation model
     - **Behavior**: after every inter_arrival_time(constant delay or random generator) the source generates items, if `blocking=True` , it yields `reserve_put` on the connected edge. If yielded, the item is added to the out edge using `put`. If `blocking=False`, it checks whether edge has space to receive an item and only if space is available item is pushed into the out edge, else it is discarded.
     - **Parameters**
         - `criterion_to_put`: method to choose the out egde to which the item will be pushed
         - `inter_arrival_item`: time between two successive item generation
         - `blocking`: whether source has to wait until the item is available in the out edge or not

      

  2. **Sink** \( N_snk \):
     
     - **Purpose**: Represents a terminal or leaf node in the simulation node, marking the end of one or more process paths. Items that enter a Sink are permanently removed from the system—they cannot be retrieved or processed further. 
     - **Behavior**: yields `reserve_get` on the incoming connected edge. If yielded, the item is retrieved using `get`. 

  3. **Machine** \( N_m \):
    - **Purpose**: class to represent entities that modify/process items
    - **Behavior**: yields `reserve_get` on the incoming connected edge. If yielded, the item is retrieved using `get`. The retrieved item is modified and put into its inbuiltstore until its store_capacity is reached. Then these processed items from the inbuiltstore is pushed to the outgoing edge by using `reserve_put` and `put` methods            
    - **Parameters**
         - `work_capacity`: no. of simultaneous operations that the node can perform
         - `store_capacity`: Capacity of the store.
         - `processing_delay`: time taken to process/modify a flow item.


4. **Split** \( N_sp \):
    - **Purpose**: class to represent items that multiplexes incoming items into outgoing flows
    - **Behavior**: yields `reserve_get` on the incoming connected edge. If yielded, the item is retrieved using `get`. The retrieved item is either put into out_edge 1 or out_edge 2 based on the rule specified by the user. Then these processed items  is pushed to the respective outgoing edge by using `reserve_put` and `put` methods            
    - **Parameters**:
        - `node_type`: Split
        -  `rule` : percentage of split
              
5. **Joint** \( N_jt \):
           
     - **Purpose**: class to represent items that combines items from multiple incoming edges
     - **Behavior**: yields `reserve_get` on the incoming connected edges. If yielded, the items are  retrieved using `get`. The retrieved items are combined and put into inbuiltstore. Then these processed items  is pushed to the respective outgoing edge by using `reserve_put` and `put` methods            
    - **Parameters**:
      - `node_type`: Joint

---            
                
### **Edge** \( E \):
- **Purpose**: Class to represent the passive entities in the system. It connects two nodes and helps the items to flow from one node to another  
- **Parameters**
     - `id`: unique name of a edge
     - `src_node`: reference to the source node
     - `dest_node`: reference to the destination node
     
### Derived Classes from Edge 

  1. **Conveyor** \( E_c \):
     - **Purpose**: class represents a slotted type conveyor belt in a manufacturing system.
     - **Behavior**: Waits for reserve_put and put to add items to the conveyor belt. Moves the items from one end to the other and waits for the item to be picked up from the belt using `reserve_get` and `get` method. It maintains the order of items. 
     - **Parameters**:
        - `belt_capacity`: Capacity of the conveyor.
        - `delay_per_slot`: Time for an item to move from one slot to the next.
        - `accumulating`: Boolean indicating if items can accumulate at the conveyor's end.
        
     - **Methods**:
        - `can_put()`, `reserve_put`, `put()`: Add items.
        - `can_get()`, `reserve_get`, `get()`: Retrieve items.

  2. **Buffer** \( E_b \):
     - **Purpose**: class to represent entities that acts like a FIFO queue with a pre-specified delay.
     - **Behavior**: waits for reserve_put and put of items. Once an item is put inside buffer, it becomes available for the destination node after `delay` amount of time. Destination node can retrieve the items from buffer's store using `reserve_get` and `get` methods.
     - **Parameters**:
        - `store_capacity`: Capacity of the buffer.
        - `delay`: Time after which the item becomes available at the output

       
     - **Methods**:
        - `can_put()`, `reserve_put`, `put()`: Add items.
        - `can_get()`, `reserve_get`, `get()`: Retrieve items.

  3. **Transporter** \( E_t \):
     - **Purpose**: Handles bursty traffic by operating in parallel.
     - **Behavior**: Spawns additional instances as required to manage flow surges.

 

---
 

### **Item** \( I \):
- **Purpose**: Items that flow in the system  
- **Parameters**
     - `item_id`: unique id of an item
     
     

---


