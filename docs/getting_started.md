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

- **Split** and **Join** are nodes for splitting an item or joining multiple items.

- **Buffers**,**Conveyors** and **Fleets** are entities of type edge for transfering items from one node to another

- **Sources** and **Sinks** for generating and collecting items


All components can be customized, and extended easily.

---

##  A Minimal Working Example
An example that shows how to simulate a simple system with a machine and two buffers
```python
import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


env = simpy.Environment()

def distribution_generator(loc=4.0, scale=5.0, size=1):
    while True:
        delay = scipy.stats.expon.rvs(loc=0.0,scale=0.5,size=1)
        yield delay[0]

# Initializing nodes
src= Source(env, id="Source-1",  inter_arrival_time=distribution_generator(), blocking=False, out_edge_selection="FIRST" )
m1 = Machine(env, id="M1",work_capacity=4,store_capacity=5, processing_delay=1.6,in_edge_selection="FIRST",out_edge_selection="FIRST")

sink= Sink(env, id="Sink-1" )

# Initializing edges
buffer1 = Buffer(env, id="Buffer-1", store_capacity=4, delay=0.43, mode="LIFO")
buffer2 = Buffer(env, id="Buffer-2", store_capacity=2, delay=0.87, mode= "FIFO")

# Adding connections
buffer1.connect(src,m1)
buffer2.connect(m1,sink)


env.run(until=10)

```


---

##  Directory Structure

```
FactorySimPy/
├─ src/factorysimpy/
│  ├─ nodes/     # Processor, Source, Sink, Split, Join
│  ├─ edges/     # Buffer, Conveyor, Fleet
│  ├─ base/      # SimPy extensions
│  ├─ helper/    # Other necessary classes like Item
├─ docs/
│  ├─ index.md
│  └─ examples/
├─ tests/
├─ examples/
└─ README.md
```

---


