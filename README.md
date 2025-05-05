
# FactorySimPy

> **Light-weight component library for discrete-event simulation of manufacturing systems, built on top of SimPy 4.1.1**

[![PyPI](https://img.shields.io/pypi/v/factorysimpy?color=informational)](https://pypi.org/project/factorysimpy/)
[![Python ≥ 3.8](https://img.shields.io/pypi/pyversions/factorysimpy)](https://pypi.org/project/factorysimpy/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

FactorySimPy is a opensource, lightweight python library for modeling and discrete-event simulation of systems seen in manufacturing systems. This library has a canonical set of components that are seen in a typical manufacuting setting like Machines with processing delay or Joints that pack incoming items from different other components, etc. These components' behaviour is pre-built and configurable. User has to provide the model structure and the component parameters to run the simulation model. User can include new features by deriving from the existing classes. This library is built on SimPy 4 and supports as fast as possible and real time simulation.
Currently, the library supports discrete flows only and is ideal for systems where the structure remains unchanged. We also plan to add support for material flow.

---

## Key Features
* **Open source, lightweight, reusable Component-based library** 
* **Modular and extensible** 
* **Documentation with Examples and usage details** 
* **MIT‑licensed**


---

## Installation
 1. **Install SimPy** (if not already installed, See the [SimPy documentation](https://simpy.readthedocs.io/en/4.1.1/) for details. )
```bash
pip install simpy
```
 

2. **Install FactorySimPy**

   **PyPI (recommended)**
   ```bash
   pip install factorysimpy
   ```

   **Latest Git main**
   ```bash
   pip install git+https://github.com/<org>/FactorySimPy.git
   ```

---

## Quick‑start — A minimum working example

[View a minimum working example](examples/quick_start.py)



---

## Component Reference

### Nodes 
| Class | Purpose | Key parameters |
|-------|---------|----------------|
| `Node`   | base class | `name` ,`work_capacity=1`, `store_capacity=1`, `delay=0`, `in_edges=None`,`out_edges=None`  |
| `Machine` | Processes one item at a time. 
| `Source`  | Generates new items. 
| `Sink`    | Collects / destroys items, gathers stats. 
| `Split`   | Routes items to multiple outputs (probability or rule). | `rule` |
| `Joint`    | Merges input streams into one. 


### Edges 
| Class | Purpose | Key parameters |
|-------|---------|----------------|
| `Edge`   | base class | `name` ,`delay=0`, `src_node=None`,`dest_edges=None`  |
| `Buffer`  | Finite‑capacity FIFO queue. | `store_capacity`|
| `Conveyor` | slotted conveyor belt; optional blocking slots. | `name`,`belt_capacity`, `time_per_slot`, `blocking=False` |
| `Fleet` | Pool of AGVs/robots moving items. | 


---

## Project Layout
```
FactorySimPy/
├─ src/factorysimpy/
│  ├─ nodes/          # Processor, Source, Sink, Split, Join
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

The full API reference, tutorials and example is available at:

```
https://factorysimpy.github.io/FactorySimPy/
```


---


## License

FactorySimPy is released under the **MIT License**.

---


