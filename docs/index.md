
# Discrete event Simulation for Manufacturing
## FactorySimPy

FactorySimPy is an open-source, light-weight Python library for modeling and discrete-event simulation (DES) of manufacturing systems. It provides a well-defined set of canonical components commonly found in a manufacturing setting—such as machines with configurable processing delays, joints that packs/joins items from multiple inputs, buffers that operate as queues holding items that wait, etc. These components come with pre-built behavior that is easily configurable, enabling users to rapidly construct simulation models. To use the library, users define the structure of the system and specify the parameters for each component. The modular design allows users to extend functionality by subclassing existing components, making the library extensible and reusable. Built on top of SimPy 4, FactorySimPy supports both "as fast as possible" and real-time simulation modes. It is currently designed for discrete-item flow systems where the model structure remains fixed during the simulation. Future development plans include extending support to material flows.




## Model Description

The system is modeled as a graph consisting of two types of components: Nodes and Edges. Nodes represent active components that drive state changes—such as machines that introduce delays by performing operations like packing, unpacking, or modifying items. Edges, in contrast, represent passive components such as conveyor belts, human operators, warehouse robots, or transport vehicles that facilitate the movement of items between nodes.


Each node maintains two lists: `in_edges` and `out_edges`, with references to incoming and outgoing edges, respectively. An edge connects exactly two nodes and holds reference to its `src_node` (source node) and `dest_node` (destination node). The graph supports both loops and self-loops. Edge can be uniquely associated with one source and one destination node or a source node to itself in the case of a self-loop.
State transitions in the simulation are triggered solely by the actions of the nodes, ensuring a clear separation between control (Nodes) and transport (Edges) within the model.




## **Class Hierarchy**
```
├── Node(Base Class for components that processes items)
    ├── Machine     # Processes items 
    ├── Joint      # Merges multiple flows into one
    ├── Split       # Splits a flow into multiple branches.
    ├── Sink        # Consumes items
    ├── Source       # generates items
  

├── Edge(Base Class for components that transfer items from one node to another)
    ├── Conveyor  #transfers items in a sequence from node to another and order is preserved
    ├── Fleet      # Fleet of human operstor, warehouse robots or transport vehicles
    ├── Buffer     # Queue of items waiting to be accepted by the next node in a model


├── BaseFlowItem(Base Class for components that flow through the systen)
    ├── Item        #Smallest unit of discrete item. It cannot hold other items inside. 
    ├── Pallet      #Entities that can store multiple smaller units of items.
  

```




## **Simple Example**

A simple example simulating a machine that gets an item from a buffer and pushes it to one of its outgoing edges after processing it

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
SRC= Source(env, id="SRC", flow_item_type="item", inter_arrival_time= 0.8,blocking=False,out_edge_selection="FIRST" )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=4, processing_delay=1.1,blocking=False, in_edge_selection="FIRST",out_edge_selection="FIRST")
SINK= Sink(env, id="SINK" )

# Initializing edges
BUF1 = Buffer(env, id="BUF1", store_capacity=4, delay=0.5, mode = "FIFO")
BUF2 = Buffer(env, id="BUF2", store_capacity=4, delay=0.5, mode = "FIFO")

# Adding connections
BUF1.connect(SRC,MACHINE1)
BUF2.connect(MACHINE1,SINK)


env.run(until=10)


```


---


