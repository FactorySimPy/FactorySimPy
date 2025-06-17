
import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import factorysimpy
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
from factorysimpy.nodes.combiner import Combiner
from factorysimpy.nodes.splitter import Splitter


env = simpy.Environment()


def split_out_edge_selector(node):
   while True:
      proc=node.env.active_process
      worker_index = node.worker_process_map[proc]
      item_type = None
      if worker_index is None:
         raise RuntimeError("Unknown calling process")
      
      if node.item_in_process[worker_index].flow_item_type=="item" :
            yield 0
        
      elif node.pallet_in_process[worker_index].flow_item_type and len(node.pallet_in_process[worker_index].items) ==0:
        
            yield 1
      
      
      else:
         raise ValueError("Invalid item_type encountered")

# Initializing nodes
SRC1= Source(env, id="SRC1", flow_item_type = "pallet", inter_arrival_time= 0.8,blocking=False,out_edge_selection="RANDOM" )

SRC2= Source(env, id="SRC2", flow_item_type = "item",  inter_arrival_time= 0.8,blocking=False,out_edge_selection="RANDOM" )

COMBINER1 = Combiner(env, id="COMBINER1", target_quantity_of_each_item=[1,5], work_capacity=1, processing_delay=1.1, blocking= False, out_edge_selection="RANDOM" )

SPLITTER1 = Splitter(env, id="SPLITTER1",work_capacity=1, processing_delay=1.1, in_edge_selection="RANDOM",out_edge_selection=None )


SINK1= Sink(env, id="SINK1" )
SINK2= Sink(env, id="SINK2" )


#initialising in_edge_selection parameter for split
split_out_edge_func = split_out_edge_selector(SPLITTER1)
SPLITTER1.out_edge_selection = split_out_edge_func

# Initializing edges
BUF1 = Buffer(env, id="BUF1", store_capacity=2, delay=0.5, mode = "FIFO")
BUF2 = Buffer(env, id="BUF2", store_capacity=2, delay=0.5, mode = "FIFO")
BUF3 = Buffer(env, id="BUF3", store_capacity=2, delay=0.5, mode = "FIFO")
BUF4 = Buffer(env, id="BUF4", store_capacity=2, delay=0, mode = "FIFO")
BUF5 = Buffer(env, id="BUF5", store_capacity=2, delay=0, mode = "FIFO")


# Adding connections
BUF1.connect(SRC1,COMBINER1)
BUF2.connect(SRC2,COMBINER1)
BUF3.connect(COMBINER1,SPLITTER1)
BUF4.connect(SPLITTER1,SINK1)
BUF5.connect(SPLITTER1,SINK2)


env.run(until=10)
