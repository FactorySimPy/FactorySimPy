import simpy,sys, os,random
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.edges.conveyor import ConveyorBelt

from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink



env = simpy.Environment()


# Configuring the delay distributions for each Machine
# These distributions are used to simulate the processing times for each step in the manufacturing process.


def loader_distribution_generator(loc=4.0, scale=5.0, size=1):
    while True:
        delay = scipy.stats.expon.rvs(loc=0.0,scale=0.5,size=1)
        yield delay[0]


def solder_distribution_generator(loc=4.0, scale=5.0, size=1):
    while True:
        args=[0.5]
        delay = scipy.stats.triang.rvs(*args,loc=1.0,scale=2.0,size=1)
        yield delay[0]


def placer_distribution_generator(loc=4.0, scale=5.0, size=1):
    while True:
        delay = scipy.stats.uniform.rvs(loc=3.0,scale=6,size=1)
        yield delay[0]

def reflow_distribution_generator(loc=4.0, scale=5.0, size=1):
    while True:
        delay = scipy.stats.norm.rvs(loc=2,scale=0.25,size=1)
        yield delay[0]
def inspect_distribution_generator(loc=4.0, scale=5.0, size=1):
    while True:
        delay = scipy.stats.expon.rvs(loc=0.0,scale=3,size=1)
        yield delay[0]

def package_distribution_generator(loc=4.0, scale=5.0, size=1):
    while True:
        delay = scipy.stats.uniform.rvs(loc=2,scale=4, size=1)
        yield delay[0]

def source_delay_generator():
        while True:
            #yield random.randint(delay_range[0], delay_range[1])
            #yield random.random()
            yield random.randint(1,3)

loader_delay = loader_distribution_generator()
solder_delay = solder_distribution_generator()
placer_delay = placer_distribution_generator()
reflow_delay = reflow_distribution_generator()
inspect_delay = inspect_distribution_generator()
package_delay = package_distribution_generator()


# Define the parameters for the processors and edges




board_loader=Machine(env, "board_loader",  work_capacity=1, store_capacity=1, processing_delay=loader_delay)
solder_printer=Machine(env, "solder_printer",  work_capacity=1, store_capacity=1, processing_delay=solder_delay)
component_placer=Machine(env, "component_placer",  work_capacity=1, store_capacity=1, processing_delay=placer_delay)
reflow_oven=Machine(env, "reflow_oven", work_capacity=1, store_capacity=1, processing_delay=reflow_delay)
inspection=Machine(env, "inspection",  work_capacity=1, store_capacity=1, processing_delay=inspect_delay)
packing=Machine(env, "packing",  work_capacity=1, store_capacity=1, processing_delay=package_delay)
source=Source(env, "source", inter_arrival_time=source_delay_generator(),criterion_to_put="first", blocking=False)
sink=Sink(env, "sink",)

#edges
buffer_loader=Buffer(env, "buffer_loader")
buffer_solder=Buffer(env, "buffer_solder" )
buffer_component=Buffer(env, "buffer_component")
buffer_reflow=Buffer(env, "buffer_reflow" )
buffer_inspection=Buffer(env, "buffer_inspection")
buffer_packing=Buffer(env, "buffer_packing")
buffer_sink=Buffer(env, "buffer_sink")
#connections
buffer_loader.connect(source,board_loader)
buffer_solder.connect(board_loader,solder_printer)
buffer_component.connect(solder_printer,component_placer)
buffer_reflow.connect(component_placer,reflow_oven)
buffer_inspection.connect(reflow_oven,inspection)
buffer_packing.connect(inspection,packing)
buffer_sink.connect(packing,sink)
# Run the simulation
env.run(until=6000)

print("Simulation completed.")
print(f"Total items received: {sink.class_statistics['item_received']}")