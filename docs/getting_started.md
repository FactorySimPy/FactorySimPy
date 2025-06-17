# Getting Started with FactorySimPy

Welcome to FactorySimPy – a lightweight, open-source component library for discrete-event simulation (DES) of manufacturing systems, built on top of [SimPy v4.1.1](https://simpy.readthedocs.io/en/4.1.1/). 

This guide will help you to get started with the packages in a few minutes.

---

##  Installation

Install FactorySimPy. Make sure you have Python ≥ 3.8.

From Github

1. Install SimPy (if not already installed)
```bash
pip install simpy
```

2. Install FactorySimPy

```bash
pip install git+https://github.com/FactorySimPy/FactorySimPy.git
```

---

##  What You Can Model

FactorySimPy lets you simulate typical manufacturing scenarios using ready-made building blocks like:

- **Machine** is a node with configurable processing delay

- **Splitter ** and **Combiner** are nodes for splitting an item or joining multiple items.

- **Buffer**, **Conveyor** and **Fleet** are entities of type edge for aiding in item transfer from one node to another

- **Source** and **Sink** for generating and collecting items


All components can be customized, and extended easily.

---

##  A Minimal Working Example
An example that shows how to simulate a simple system with a machine and two buffers
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
SRC= Source(env, id="SRC", flow_item_type="item", inter_arrival_time= 0.8,blocking=False,out_edge_selection="RANDOM" )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=4, processing_delay=1.1,blocking=False, in_edge_selection="RANDOM",out_edge_selection="RANDOM")
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

##  Directory Structure

```
FactorySimPy/
├─ src/factorysimpy/
│  ├─ nodes/     # Processor, Source, Sink, Combiner, Splitter
│  ├─ edges/     # Buffer, Conveyor, Fleet
│  ├─ base/      # SimPy extensions
│  ├─ constructs/      # constructs to simplify model creation
│  ├─ helper/    # Other necessary classes like Item, baseflowitem, pallet
│  └─ utils/     # Other utility functions
├─ docs/
│  ├─ index.md
│  └─ examples/
├─ tests/
├─ examples/
└─ README.md
```

---


