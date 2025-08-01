
import simpy,sys, os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))



import random

from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

env = simpy.Environment()

#let the inter arrival time of the source be a value sampled from a gaussian distribution with mean = 2, std deviation is = 0.5
#Gaussian distribution as a python function 
def generate_gaussian_distribution(mean=0, std_dev=1):
   
    return random.gauss(mu=mean,sigma= std_dev)
       
#let the processing delay of the machine be a value function of the duration of the time spent by the machine in processing state
#if the time spent in processing state is greater than 7, the processing delay has to take one value in index 0 of the return_vals
#if the time spent in processing state is less than or equal to 7, the processing delay has to take the value in index 1
#This behaviour as a python function 
def generate_process_delay(node,env, return_vals):
      if node.stats["total_time_spent_in_states"]["PROCESSING_STATE"]>7:
        return return_vals[0]
      else:
        return return_vals[1]




# Initializing nodes
SRC= Source(env, id="SRC",  inter_arrival_time=generate_gaussian_distribution(1,0.25),blocking=False,out_edge_selection=0 )
MACHINE1 = Machine(env, id="MACHINE1",work_capacity=1,processing_delay=None,in_edge_selection="RANDOM",out_edge_selection="RANDOM")
processing_delay_func=generate_process_delay(MACHINE1,env,[0.9,1.2])
MACHINE1.processing_delay = processing_delay_func
SINK= Sink(env, id="SINK" )



# Initializing edges
BUF1 = Buffer(env, id="BUF1", capacity=4, delay=0.5)
BUF2 = Buffer(env, id="BUF2", capacity=4, delay=0.5)


# Adding connections
BUF1.connect(SRC,MACHINE1)
BUF2.connect(MACHINE1,SINK)




env.run(until=10)
print("Simulation completed.")
# Print statistics
print(f"Source {SRC.id} generated {SRC.stats['num_item_generated']} items.")
print(f"Source {SRC.id} discarded {SRC.stats['num_item_discarded']} items.")
print(f"Source {SRC.id} state times: {SRC.stats['total_time_spent_in_states']}")
print(f"Machine {MACHINE1.id} state times: {MACHINE1.stats}")

print(f"Time-average number of items in  {BUF1.id} is {BUF1.stats['time_averaged_num_of_items_in_buffer']}")
print(f"Time-average number of items in  {BUF2.id} is {BUF2.stats['time_averaged_num_of_items_in_buffer']}")


print(f"Sink {SINK.id} received {SINK.stats['num_item_received']} items.")

print(MACHINE1.time_per_work_occupancy)
print("per_thread_total_time_in_processing_state", MACHINE1.per_thread_total_time_in_processing_state)
print("per_thread_total_time_in_blocked_state",MACHINE1.per_thread_total_time_in_blocked_state)
