
# FactorySimPy

**A light-weight component library for discrete-event simulation of manufacturing systems**

<!-- [![PyPI](https://img.shields.io/pypi/v/factorysimpy?color=informational)](https://pypi.org/project/factorysimpy/)
[![Python >= 3.8](https://img.shields.io/pypi/pyversions/factorysimpy)](https://pypi.org/project/factorysimpy/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE) -->

FactorySimPy is a light-weight Python library for modeling and discrete-event simulation of manufacturing systems, built using SimPy (version ≥ 4.1.1). It provides a compact set of pre-built, validated, and configurable component classes for manufacturing systems components such as machines and conveyors. Users can easily model a manufacturing system as a graph, with nodes representing processing elements (such as machines), and edges representing transportation methods (such as conveyors, human operators, or robotic fleets). FactorySimPy includes built-in support for reporting a variety of performance metrics and offers both accelerated ("as-fast-as-possible") and real-time simulation modes, making it suitable for digital twins and control applications. Currently, the library supports discrete item flows and is particularly suited for systems with fixed structures. Future updates will include support for continuous material flow.

---

## Key Features
* **Open source, light-weight, reusable component-based library** 
* **Modular and extensible** 
* **Documentation with examples and usage details** 



---

## Installation
 
 1. **Install SimPy** (if not already installed, See the [SimPy documentation](https://simpy.readthedocs.io/en/4.1.1/) for details.)

   ```bash
   pip install simpy
   ```
 

2. **Install FactorySimPy**

   <!--- **PyPI (recommended)**
   ```bash
   pip install factorysimpy
   ``` --->

   **Latest Git main**
   ```bash
   pip install git+https://github.com/FactorySimPy/FactorySimPy.git
   ```

---

## Quick‑start — A minimum working example

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

## Component Reference

### Nodes 
| Class | Purpose | Key parameters |
|-------|---------|----------------|
| `Node`   | base class for active entities | `id` , `node_set_up_time=0`, `in_edges=None`,`out_edges=None`  |
| `Source`  | Generates new items | `inter_arrival_time=0` , `flow_item_type="item"`, `blocking=False` , `out_edge_selection="RANDOM"`   |
| `Machine` | Processes/modifies items.| `work_capacity=1`, `blocking=False` , `processing_delay=0`, `in_edge_selection="RANDOM"`,`out_edge_selection="ROUND_ROBIN"`|
| `Sink`    | Collects / destroys items.
| `Split`   | Routes items to multiple outputs  | `blocking=False` , `processing_delay=0`, `in_edge_selection="RANDOM"`, `out_edge_selection="RANDOM"` |
| `Joint`    | Merges input streams into one | `blocking=False` , `processing_delay=0`,`target_quantity_of_each_item=[1]`, `in_edge_selection="RANDOM"`,`out_edge_selection="ROUND_ROBIN"`|

 
### Edges 
| Class | Purpose | Key parameters |
|-------|---------|----------------|
| `Edge`   | base class for passive entities | `id` ,`delay=0`, `src_node=None`,`dest_node=None`  |
| `Buffer`  | Finite‑capacity queue. | `store_capacity`,`delay=0`, `mode="FIFO"`|
| `Conveyor` | slotted conveyor belt; optional blocking slots. | `belt_capacity`, `time_per_slot`, `accumulating=False` |
| `Fleet` | Pool of AGVs/robots moving items. | 


---

## Project Layout
```
FactorySimPy/
├─ src/factorysimpy/
│  ├─ nodes/          # Machine, Source, Sink, Split, Join
│  ├─ edges/          # Buffer, Conveyor, Fleet
│  ├─ base/          # extended resources from simPy
│  ├─ helper/        # Other necessary classes like Item, 
│  └─ utils/         # Other utility functions
├─ docs/
│  ├─ index.md
│  └─ examples/
├─ tests/
├─ examples/
└─ README.md
```
---

## Documentation

Detailed documentation is available in [FactorySimPy documentation](https://factorysimpy.github.io/FactorySimPy/)



---


## License

FactorySimPy is released under the **MIT License**.

---


