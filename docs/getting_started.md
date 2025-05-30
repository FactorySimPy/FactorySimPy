# Getting Started with FactorySimPy
<p style="text-align: justify;">
Welcome to FactorySimPy – a lightweight, open-source component library for discrete-event simulation (DES) of manufacturing systems, built on top of [SimPy 4.1.1](https://simpy.readthedocs.io/en/4.1.1/). 

This guide will help you to get started with the packages in a few minutes.
</p>
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

- **Split** and **Join** are nodes for splitting a flow into two or joining two flows

- **Buffers**,**Conveyors** and **Fleets** are entities of type edge for transfering items from one node to another

- **Sources** and **Sinks** for generating and collecting items


All components can be customized, and extended easily.

---

##  A Minimal Working Example

[An example that shows how to simulate a simple system with two machines and a conveyor](../examples/quick_start.py)




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

##  Documentation

Visit the [full documentation site](https://factorysimpy.github.io/FactorySimPy/)

##  License

FactorySimPy is licensed under the **MIT License**.

---
