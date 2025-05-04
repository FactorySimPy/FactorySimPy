
# Discrete event Simulation for Manufacturing
## Overview
FactorySimPy is a opensource, python library for modeling and Discrete-event simulation of systems seen in manufacturing systems. This library has a canonical set of components that are seen in a typical manufacuting setting like Machines with processing delay or Joints that pack incoming items from different other components, etc. These components' behaviour is pre-built and configurable. User has to provide the model structure and the component parameters to run the simulation model. User can include new features by deriving from the existing classes. This library is built on SimPy 4 and supports as fast as possible and rela time simulation.    
Currently, the library supports discrete flows only and is ideal for systems where the structure remains unchanged. We also plan to add support for material flow.

System consists of two types of components namely Nodes and Edges and is defined as a graph with nodes which are the active components in the system like machine with a processing delay (or machines that pack or unpack items, etc). and edges that represent objects corresponding to conveyor or fleet of human operators or ware-house robots or transport vehicles that are used for item transfer in the system from one node to another.



## Model Description
User defines the system as a graph with nodes and edges. Nodes are the components that represents machines with processing delays and edges are the components that used to join two nodes together.

A node has a set of in_edges and out_edges. An edge connects exactly two nodes and serves as an in_edge for the dest_node and out_edge for the src_node. Graph can have loops(and self loops).



### Example Representation
An example model with 2 nodes and an edge

<!-- ![Graph Representation](jupyternb/images/gr_2nodes.jpg) -->

---

## Component Design:Important Classes

`Node` and `Edge` serves as the base classes. There is another class to represent the items that flow in the system and is named as `Item` class. `Nodes` are the active elements in the system and are static and `Edge` represents the passive elements in the systems and are used to interconnect two nodes.

Node has in_edges and out_edges which contains reference to edge objects. Other parameters of Node are id and name. `Machine` is a class derived from node class to represent all the nodes that have a processing capability. `Processor`, `Split`, and `Joint` are classes that are derived from `Machine` class. `Processor` has parameters capacity(int) which is the maximum number of items that can be processed simultaneously in the machine and delay which is the time taken for processing an item. Delay can be a number(integer or real-valued) or a generator function that can be used to generate random variates from a distribution. Other components that are derived from node are `Source` and `Sink`.
Edge has parameters dest_node, source_node and capacity and has methods can_put, put, can_get and get. `Conveyor`, `Fleet` and `Buffer` are classes that are derived from Edge base class.  In `Conveyors`, items are moved in sequence from one node to another and the order of the items are preseved. It has parameters capacity(int, maximum number of items it can hold), occupancy(int, number of items currently present on it) and state. State represents the state of the conveyor and takes values stalled, moving or empty.

`Conveyor` can support discrete(slotted belt) movement of items and continuous flow of discrete items. 

In a discrete motion conveyor, the items are moved in fixed steps or stages and will be halted for sometime defined as delayperslot. where as in conitnuous motion conveyor, items move continuously at a defined speed.

If an item is present at the other end of the conveyor, then an accumulating conveyor allows other incoming items to be placed in the conveyor and it will get lined up behind the the last item, until the capacity of the conveyor is reached. But, a non-accumulating conveyor will only allow one incoming item at the starting end of the conveyor if an item is already present at the other end of the conveyor.



 `Fleets` represents the objects that can transport items from a node to another by a fleet of carriers, warehouse robots, human operators, etc. The order of the items is not preserved here. It is characterised by the parameters size of fleet, delay, and state. The size of fleet(int) that the number of carriers, delay represents the time it take to transport the items. Delay can be a number(integer or real-valued) or a generator function that can be used to generate random variates from a distribution. State variable represents the state of every agent. The values it takes are `occupied` or `not-occupied`. If the state is occupied, then the fleet will be moving.


Here, is an example of a model with 3 nodes that are connected using 2 edges. Nodes are of type source, machine and sink and edges are of type conveyor. 

## System Description

### Rules for interconnection
1. Nodes are static entities like processor, source, sink, split, joints, etc.
2. Edges are directed and connects one node to another. Conveyor, buffer and fleet are the entities that are of type Edge.
3. Items are discrete parts that flow in the system through the directed edges from one node to another. 
3. Each Node has two lists `in_edges` and `out_edges` that points to the references of the edges that comes in and go out of the node
4. Each Edge stores pointers to a `src_node` and a `dest_node`. An Edge can be used only to connect a single node(`src_node`) to another (or same) node(`dest_node`).
5. An Edge can have the same node in both `src_node` and `dest_node`. (ie, a node can be connected to itself)
6. Nodes are the active elements whose activites initiates state changes in the system.
7. Edges are the passive elements and state change occurs due to actions initiated by nodes
8. To split the output from a `processor` node into two streams, a `Split` must be connected to the `processor` using an Edge.
9. To join two streams and to feed as input to a `processor` node, a `Joint` must be connected to the `processor` using an Edge

<!-- ![Example Image](jupyternb/images/split.jpg)

```<img src="jupyternb/images/split.jpg" alt="Example Image" style="width:400px;">```
```<img src="jupyternb/images/split.jpg" class="resized-img">```




![Graph Representation](jupyternb/images/joint.jpg) -->

### Steps for Connecting Components
1. Instantiate nodes and edges:
   ```python
   n1 = Node()
   n2 = Node()
   n3 = Sink()
   e1 = Edge()
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
    ├── Machine     # Base class for nodes that Processes items 
      ├── Processor     # Processes items 
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
- **Purpose**: Active elements in the system.  
- **Parameters**
     - `node_id`: unique id of a node
### Derived Classes from Node 
  1. **Source** \( N_src \):
     - **Purpose**: to mark the start of the model
      - **Behavior**: Calls `can_put` on the connected edge. If `True`, the item is added using `put`. Otherwise, the item is dropped (non-blocking behavior).
      - **Parameters**
          - `delay`: Time between item generations.
          - `can_put()`: Checks edge availability.
          - `put()`: Adds item to the edge.

  2. **Sink** \( N_snk \):
     - **Purpose**: To mark the end of the model
     - **Behavior**: Entity to consume items 
  3. **Machine** \( N_m \):
     
     - **Parameters**:
          - `work_capacity`: Capacity of the machine.
          - `store_capacity`: Capacity of the store.
          - `delay`: Time for processing.
          - `name`: string name of the machine.
       
     - **Methods**:
          - `can_put()`, `put()`: Add items.
          - `can_get()`, `get()`: Retrieve items.
    
     - **Derived Classes from Machines**:
          1. **Processor** \( N_p \):
            
            - **Parameters**:
                - `work_capacity`: Capacity of the machine.
                - `store_capacity`: Capacity of the store.
                - `delay`: Time for processing.
                - `name`: string name of the machine.
              
            - **Methods**:
                - `can_put()`, `put()`: Add items.
                - `can_get()`, `get()`: Retrieve items.

          2. **Split** \( N_sp \):
            
            - **Parameters**:
                - `work_capacity`: Capacity of the machine.
                - `store_capacity`: Capacity of the store.
                - `delay`: Time for processing.
                - `name`: string name of the machine.
              
            - **Methods**:
                - `can_put()`, `put()`: Add items.
                - `can_get()`, `get()`: Retrieve items
              
          3. **Joint** \( N_jt \):
            
            - **Parameters**:
                - `work_capacity`: Capacity of the machine.
                - `store_capacity`: Capacity of the store.
                - `delay`: Time for processing.
                - `name`: string name of the machine.
            - **Methods**:
                - `can_put()`, `put()`: Add items.
                - `can_get()`, `get()`: Retrieve items

                
### **Edge** \( E \):
- **Purpose**: Connects two nodes.  
- **Parameters**
     - `edge_id`: unique id of an edge

### Derived Classes from Edge 

  1. **Conveyor** \( E_c \):
     - **FIFO Behavior**: Maintains the order of items.
     - **Parameters**:
       - `num_slots`: Capacity of the conveyor.
       - `delay_per_slot`: Time for an item to move from one slot to the next.
       - `accumulating`: Boolean indicating if items can accumulate at the conveyor's end.
       - **Blocking Conveyor**: Blocks further additions if the last slot is occupied.
     - **Methods**:
       - `can_put()`, `put()`: Add items.
       - `can_get()`, `get()`: Retrieve items.

  2. **Transporter** \( E_t \):
     - **Purpose**: Handles bursty traffic by operating in parallel.
     - **Behavior**: Spawns additional instances as required to manage flow surges.

  3. **Buffer** \( E_b \):
     - **Purpose**: Handles bursty traffic by operating in parallel.
     - **Behavior**: Spawns additional instances as required to manage flow surges.

---
 

### **Item** \( I \):
- **Purpose**: Items that flow in the system  
- **Parameters**
     - `item_id`: unique id of an item
     - `delay`: inter-arrival time
     

---


## Summary
By adhering to this framework, FactorySimPy ensures a structured, intuitive simulation environment for modeling discrete item flows in manufacturing systems. The notations and rules defined here aim to provide clarity and minimize ambiguity during model creation.
