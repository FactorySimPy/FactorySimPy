import pytest
import simpy, sys, os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))



from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.edges.continuous_conveyor import ConveyorBelt
from factorysimpy.helper.item import Item
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


@pytest.fixture
def env_for_test():
    return simpy.Environment()


@pytest.fixture
def setup_machine_with_buffers(env_for_test):
    # Create input buffers
    conveyor1 = ConveyorBelt(env_for_test, "Conveyor1", conveyor_length=5, speed=5.76, item_length=0.5, accumulating=0)
    buffer1 = Buffer(env_for_test, "Buffer1", delay=0, capacity=4)

   

    # Create machine
    machine = Machine(
        env=env_for_test,
        id="M1",
        processing_delay=3,
        node_setup_time=0,
        work_capacity=2,
        blocking=True,
        in_edge_selection="ROUND_ROBIN",
        out_edge_selection="FIRST_AVAILABLE"
    )
    
    # create source and sink
    src1 = Source(env_for_test, id="Source-1",item_length=0.5,  inter_arrival_time=3,blocking=True,out_edge_selection="FIRST_AVAILABLE" )
   
    sink = Sink(env_for_test, id="Sink-1")
    return env_for_test, machine, src1, conveyor1, buffer1,  sink


def test_conveyor_2(setup_machine_with_buffers):
    env, machine,src1, conveyor1, buffer1, sink = setup_machine_with_buffers
    conveyor1.connect(src1, machine)
    buffer1.connect(machine, sink)
   

   
    env.run(until=1000)  # Run long enough for processing to complete

    # Check that output buffer got both items
    
   
    assert sink.stats['num_item_received'] == 332

    # Check that machine updated its stats
    assert np.round(conveyor1.stats['time_averaged_num_of_items_in_conveyor'],3) == 0.289
    assert sink.stats['num_item_received']/env.now == 0.332
    tot_cycletime = sink.stats["total_cycle_time"]
    tot_items = sink.stats["num_item_received"]
    assert np.round(tot_cycletime/tot_items,3) == 3.868


def test_conveyor_1(env_for_test):
    env= env_for_test
    conveyor1 = ConveyorBelt(env, "Conveyor1", conveyor_length=5, speed=1, item_length=0.5, accumulating=1)
    buffer1 = Buffer(env, "Buffer1", delay=0, capacity=4)

   

    # Create machine
    machine = Machine(
        env=env,
        id="M1",
        processing_delay=3,
        node_setup_time=0,
        work_capacity=1,
        blocking=True,
        in_edge_selection="ROUND_ROBIN",
        out_edge_selection="FIRST_AVAILABLE"
    )
    
    # create source and sink
    src1 = Source(env, id="Source-1", item_length=0.5, inter_arrival_time=0.3,blocking=True,out_edge_selection="FIRST_AVAILABLE" )
   
    sink = Sink(env, id="Sink-1")
    conveyor1.connect(src1, machine)
    buffer1.connect(machine, sink)
   

   
    env.run(until=1000)  # Run long enough for processing to complete

    # Check that output buffer got both items
    
   
    assert sink.stats['num_item_received'] == 331

    # Check that machine updated its stats
    assert np.round(conveyor1.stats['time_averaged_num_of_items_in_conveyor'],3) == 9.974 # 9.941
    assert sink.stats['num_item_received']/env.now == 0.331
    tot_cycletime = sink.stats["total_cycle_time"]
    tot_items = sink.stats["num_item_received"]
    assert np.round(tot_cycletime/tot_items,3) == 32.585 #32.48



def test_conveyor_3():

    env = simpy.Environment()



    # Initializing nodes
    SRC= Source(env, id="SRC",  inter_arrival_time=3,blocking=True, out_edge_selection="FIRST_AVAILABLE" )

    #src= Source(env, id="Source-1",  inter_arrival_time=0.2,blocking=True,out_edge_selection=0 )
    MACHINE1 = Machine(env, id="MACHINE1", node_setup_time=0, work_capacity=1, blocking=True, processing_delay=3, in_edge_selection="FIRST_AVAILABLE", out_edge_selection="ROUND_ROBIN")
    SINK= Sink(env, id="SINK")

    # Initializing edges
    BUFFER1 = Buffer(env, id="BUFFER1", capacity=4, delay=0, mode="FIFO")
    CONVEYORBELT1 = ConveyorBelt(env, id="CONVEYORBELT1", conveyor_length=5, speed=1, item_length=0.5, accumulating=1)



    # Adding connections
    CONVEYORBELT1.connect(SRC,MACHINE1)
    BUFFER1.connect(MACHINE1,SINK)

    env.run(until=1000)  # Run long enough for processing to complete

    # Check that output buffer got both items
    
   
    assert SINK.stats['num_item_received'] == 330

    # Check that machine updated its stats
    assert np.round(CONVEYORBELT1.stats['time_averaged_num_of_items_in_conveyor'],3) == 1.66 # 1.627
    assert SINK.stats['num_item_received']/env.now == 0.330
    tot_cycletime = SINK.stats["total_cycle_time"]
    tot_items = SINK.stats["num_item_received"]
    assert np.round(tot_cycletime/tot_items,3) == 8.0 #7.9





def test_conveyor_4():
    env = simpy.Environment()



    # Initializing nodes
    SRC= Source(env, id="SRC",  inter_arrival_time=1,blocking=True, out_edge_selection="FIRST_AVAILABLE" )

    #src= Source(env, id="Source-1",  inter_arrival_time=0.2,blocking=True,out_edge_selection=0 )
    MACHINE1 = Machine(env, id="MACHINE1", node_setup_time=0, work_capacity=2, blocking=True, processing_delay=1, in_edge_selection="FIRST_AVAILABLE", out_edge_selection="ROUND_ROBIN")
    SINK= Sink(env, id="SINK")

    # Initializing edges
    BUFFER1 = Buffer(env, id="BUFFER1", capacity=4, delay=0, mode="FIFO")
    CONVEYORBELT1 = ConveyorBelt(env, id="CONVEYORBELT1", conveyor_length=10, speed=2, item_length=1, accumulating=0)



    # Adding connections
    CONVEYORBELT1.connect(SRC,MACHINE1)
    BUFFER1.connect(MACHINE1,SINK)



    time=1000

    env.run(until=time)
    SRC.update_final_state_time(time)
    MACHINE1.update_final_state_time(time)
    CONVEYORBELT1.update_final_conveyor_avg_content(time)
    BUFFER1.update_final_buffer_avg_content(time)
    SINK.update_final_state_time(time)


    assert SINK.stats['num_item_received'] == 993 #994

    # Check that machine updated its stats
    assert np.round(CONVEYORBELT1.stats['time_averaged_num_of_items_in_conveyor'],3) == 4.985 # 4.980
    assert SINK.stats['num_item_received']/env.now == 0.993
    tot_cycletime = SINK.stats["total_cycle_time"]
    tot_items = SINK.stats["num_item_received"]
    assert np.round(tot_cycletime/tot_items,3) == 6.0 #5.99



def test_conveyor_5():

    env = simpy.Environment()



    # Initializing nodes
    SRC= Source(env, id="SRC", item_length= 0.5, inter_arrival_time=1,blocking=True, out_edge_selection="FIRST_AVAILABLE" )

    #src= Source(env, id="Source-1",  inter_arrival_time=0.2,blocking=True,out_edge_selection=0 )
    MACHINE1 = Machine(env, id="MACHINE1", node_setup_time=0, work_capacity=1, blocking=True, processing_delay=4, in_edge_selection="FIRST_AVAILABLE", out_edge_selection="ROUND_ROBIN")
    SINK= Sink(env, id="SINK")

    # Initializing edges
    BUFFER1 = Buffer(env, id="BUFFER1", capacity=4, delay=0, mode="FIFO")
    CONVEYORBELT1 = ConveyorBelt(env, id="CONVEYORBELT1", conveyor_length=4, speed=1, item_length=0.5, accumulating=1)



    # Adding connections
    CONVEYORBELT1.connect(SRC,MACHINE1)
    BUFFER1.connect(MACHINE1,SINK)



    time= 1000

    env.run(until=time)
    SRC.update_final_state_time(time)
    MACHINE1.update_final_state_time(time)
    CONVEYORBELT1.update_final_conveyor_avg_content(time)
    BUFFER1.update_final_buffer_avg_content(time)
    SINK.update_final_state_time(time)

    assert SINK.stats['num_item_received'] == 248 

    # Check that machine updated its stats
    assert np.round(CONVEYORBELT1.stats['time_averaged_num_of_items_in_conveyor'],3) == 7.956 # 7.956
    assert SINK.stats['num_item_received']/env.now == 0.248
    tot_cycletime = SINK.stats["total_cycle_time"]
    tot_items = SINK.stats["num_item_received"]
    assert np.round(tot_cycletime/tot_items,3) == 35.401 #35.41



   