
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

[View a minimum working example](examples/quick_start.py)



---

## Component Reference

### Nodes 
| Class | Purpose | Key parameters |
|-------|---------|----------------|
| `Node`   | base class | `id` , `node_set_up_time=0`, `in_edges=None`,`out_edges=None`  |
| `Source`  | Generates new items | `inter_arrival_time=0` , `blocking=False` , `criterion_to_put=first_available`,   |
| `Machine` | Processes one item at a time.| `work_capacity=1`, `store_capacity=1`, `processing_delay=0`|
| `Sink`    | Collects / destroys items.
| `Split`   | Routes items to multiple outputs (probability or rule). | `rule` |
| `Joint`    | Merges input streams into one. 


### Edges 
| Class | Purpose | Key parameters |
|-------|---------|----------------|
| `Edge`   | base class | `name` ,`delay=0`, `src_node=None`,`dest_edges=None`  |
| `Buffer`  | Finite‑capacity FIFO queue. | `store_capacity`|
| `Conveyor` | slotted conveyor belt; optional blocking slots. | `name`,`belt_capacity`, `time_per_slot`, `accumulating=False` |
| `Fleet` | Pool of AGVs/robots moving items. | 


---

## Project Layout
```
FactorySimPy/
├─ src/factorysimpy/
│  ├─ nodes/          # Machine, Source, Sink, Split, Join
│  ├─ edges/          # Buffer, Conveyor, Fleet
│  ├─ base/          # extended resources from simPy
│  └─ helper/          # Item
├─ docs/
│  ├─ index.md
│  └─ examples/
├─ tests/
├─ examples/
└─ README.md
```
---

## Documentation



```
https://factorysimpy.github.io/FactorySimPy/
```


---


## License

FactorySimPy is released under the **MIT License**.

---


