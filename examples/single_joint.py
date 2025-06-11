
import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.joint import Joint
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


env = simpy.Environment()

SRC1= Source(env, id="SRC1", flow_item_type = "pallet", inter_arrival_time= 0.8,blocking=False,out_edge_selection="RANDOM" )

SRC2= Source(env, id="SRC2", flow_item_type = "item",  inter_arrival_time= 0.8,blocking=False,out_edge_selection="RANDOM" )

JOINT1 = Joint(env, id="JOINT1", target_quantity_of_each_item=[1,5], work_capacity=1, processing_delay=1.1, blocking= False, out_edge_selection="RANDOM" )

#SPLIT1 = Split(env, id="SPLIT1",work_capacity=4, processing_delay=1.1, in_edge_selection="RANDOM",out_edge_selection=None )


SINK1= Sink(env, id="SINK1" )
#SINK2= Sink(env, id="SINK2" )


#initialising in_edge_selection parameter for split
# split_out_edge_func = split_out_edge_selector(SPLIT1, env)
# SPLIT1.out_edge_selection = split_out_edge_func

# Initializing edges
BUF1 = Buffer(env, id="BUF1", store_capacity=2, delay=0.5, mode = "FIFO")
BUF2 = Buffer(env, id="BUF2", store_capacity=2, delay=0.5, mode = "FIFO")
BUF3 = Buffer(env, id="BUF3", store_capacity=2, delay=0.5, mode = "FIFO")
# BUF4 = Buffer(env, id="BUF4", store_capacity=2, delay=0.5, mode = "FIFO")
# BUF5 = Buffer(env, id="BUF5", store_capacity=2, delay=0.5, mode = "FIFO")


# Adding connections
BUF1.connect(SRC1,JOINT1)
BUF2.connect(SRC2,JOINT1)
BUF3.connect(JOINT1,SINK1)
# BUF4.connect(SPLIT1,SINK1)
# BUF5.connect(SPLIT1,SINK2)


env.run(until=50)

