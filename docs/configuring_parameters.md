#Configuring parameters

# Edge Selection

There are different methods available to choose an input edge and output edge. These parameters are common for all the nodes.

To choose an input edge to pull an item from, the nodes utilises the strategy specified in the parameter `in_edge_selection`.  Similarly, to select an output edge, to push the item to, nodes uses the method specified in `out_edge_selection` parameter. These parameters can be a constant integer value (one of the edge indices), or one of the methods available in the package (passed as a string; listed below) or a Python function or a generator function instance provided by the user. User-provided function should return or yield an edge index. If the function depends on any of the node attributes, users can pass `None` to these parameters at the time of node creation and later initialise the parameter with the reference to the function. This is illustrated in the examples shown below. Various options available in the package for `in_edge_selection` and `out_edge_selection` include:

- "RANDOM": Selects a random out edge.
- "ROUND_ROBIN": Selects out edges in a round-robin manner.
- "FIRST_AVAILABLE": Selects the first out edge that can accept an item. In case of "FIRST_AVAILABLE", always the edge with the least index value will be selected if multiple edges are available


***[Example showing how to pass constant values to these parameters](examples.md/#a-simple-example)***

***[Example showing how to pass one of the methods available in the package as a string or a custom function to these parameters](examples.md/#example-with-a-custom-edge-selction-policy-as-a-function)***


# Delay parameters

`node_setup_time`, `inter_arrival_time` and `processing_delay` are one of the two delay paramaters that can be configured. `node_setup_time` is an intial one time delay for setting up any node. `inter_arrival_time` is the time interval between two successive item generation in the source and `processing_delay` is the time incurres by an item to get processed in components like machine, split, joint, etc. `node_setup_time` can be an `int` or a `float` and is a constant value. The parameters `inter_arrival_time` and `processing_delay` can be specified as a constant value (`int` or `float`) or as a reference to a python function or a generator function instance that generates random variates from a chosen distribution. If the function depends on any of the node attributes, users can pass `None` to this parameter at the time of node creation and later initialise the parameter with the reference to the function.


***[Example showing how to pass constant values to these parameters](examples.md/#a-simple-example)***
***[Example showing how to pass a custom function or generator function instance to these parameters](examples.md/#example-with-delay-as-random-variates)***
