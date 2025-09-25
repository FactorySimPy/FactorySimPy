import pytest
import simpy, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))



from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.helper.item import Item
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


@pytest.fixture
def env_for_test():
    return simpy.Environment()


@pytest.fixture
def setup_machine_with_buffers(env_for_test):
    # Create input buffers
    in_buffer1 = Buffer(env_for_test, "InBuffer1", delay=0, capacity=2)
    in_buffer2 = Buffer(env_for_test, "InBuffer2", delay=0, capacity=2)

    # Create output buffer
    out_buffer = Buffer(env_for_test, "OutBuffer", delay=6, capacity=2)

    # Create machine
    machine = Machine(
        env=env_for_test,
        id="M1",
        in_edges=[in_buffer1, in_buffer2],
        out_edges=[out_buffer],
        processing_delay=2,
        node_setup_time=0,
        work_capacity=2,
        in_edge_selection="ROUND_ROBIN",
        out_edge_selection="FIRST_AVAILABLE"
    )
    
    # create source and sink
    src1 = Source(env_for_test, id="Source-1",  inter_arrival_time=0.5,blocking=False,out_edge_selection="FIRST_AVAILABLE" )
    src2 = Source(env_for_test, id="Source-2",  inter_arrival_time=0.5,blocking=False,out_edge_selection="FIRST_AVAILABLE" )
    sink = Sink(env_for_test, id="Sink-1")
    return env_for_test, machine, src1, src2, in_buffer1, in_buffer2, out_buffer, sink


def test_machine_processes_multiple_inputs(setup_machine_with_buffers):
    env, machine,src1, src2, in_buffer1, in_buffer2, out_buffer, sink = setup_machine_with_buffers
    in_buffer1.connect(src1, machine)
    in_buffer2.connect(src2, machine)
    out_buffer.connect(machine, sink)
    # Put items into the input buffers
    item1 = Item("item1")
    item2 = Item("item2")

    def put_items():
        put_token1 = in_buffer1.reserve_put()
        yield put_token1
        item1.timestamp_creation = env.now
        in_buffer1.put(put_token1, item1)

        put_token2 = in_buffer2.reserve_put()
        yield put_token2
        item2.timestamp_creation = env.now
        in_buffer2.put(put_token2, item2)

    env.process(put_items())
    env.run(until=5)  # Run long enough for processing to complete

    # Check that output buffer got both items
    print(f"Out buffer items: {[item[0].id for item in out_buffer.get_items()]}")
    assert len(out_buffer.get_items()) == 2
    output_item_ids = [item[0].id for item in out_buffer.get_items()]
    assert "item1" in output_item_ids
    assert "item2" in output_item_ids

    # Check that machine updated its stats
    assert machine.stats["num_item_processed"] == 2



@pytest.mark.parametrize(
    "inter_arrival_time, processing_delay, work_capacity, buffer1_capacity, buffer2_capacity,, buffer1_delay, buffer2_delay",
    [   #single thread machine cases, no buffer delay
        (1, 1, 1, 4, 1, 0, 0),   # Case 1: Simple single-thread machine, no buffer delay
        (0.25, 1, 1, 4, 1,  0, 0), # Case 2: Faster arrivals, single-thread machine, no buffer delay
        (2, 3, 1, 4, 1, 0, 0),   # Case 3: Slower arrivals, single-thread machine, no buffer delay
        #multi thread machine cases, no buffer delay
        (1, 1, 5, 4, 1, 0, 0),   # Case 3: Simple multi-thread machine, no buffer delay
        (0.5, 1, 5,4, 1,  0, 0), # Case 4: Faster arrivals, multi-thread machine, no buffer delay
        (2, 3, 5,4, 1, 0, 0),   # Case 5: Slower arrivals, multi-thread machine, no buffer delay
        
        # single thread machine cases, with buffer delay
        (1, 1, 1,4, 1, 0, 3),   # Case 6: Balanced case with multi-thread machine
        (0.5, 2, 1,4, 1, 0, 3), # Case 7: High contention scenario
        (1, 2, 1, 1,4, 1, 3),   # Case 8: Buffers with delay


        #multi thread machine cases, with buffer delay
        (1, 1, 5,4, 1, 0, 3),   # Case 9: Balanced case with multi-thread machine
        (0.5, 2, 5,4, 1, 0, 3), # Case 10: High contention scenario
        (1, 2, 5, 1,4, 1, 3),   # Case 11: Buffers with delay
    ]
)
def test_pipeline_stats(inter_arrival_time, processing_delay, work_capacity,buffer1_capacity,buffer2_capacity, buffer1_delay, buffer2_delay):
    """
    Build a small pipeline: Source -> Buffer1 -> Machine -> Buffer2 -> Sink
    Run the simulation and check reported stats.
    """

    # Create environment
    env = simpy.Environment()

    # Create components
    source = Source(env, id="SRC", inter_arrival_time=inter_arrival_time)
    buffer1 = Buffer(env, id="BUF1", capacity=buffer1_capacity, delay=buffer1_delay)
    machine = Machine(env, id="M1", processing_delay=processing_delay, work_capacity=work_capacity)
    buffer2 = Buffer(env, id="BUF2", capacity=buffer2_capacity, delay=buffer2_delay)
    sink = Sink(env, id="SNK")

    # Connect components
    buffer1.connect(source, machine)
    buffer2.connect(machine, sink)

    # Run simulation
    SIM_TIME = 1500
    env.run(until=SIM_TIME)
    buffer2.update_final_buffer_avg_content(SIM_TIME)
    buffer1.update_final_buffer_avg_content(SIM_TIME)
    machine.update_final_state_time(SIM_TIME)
    sink.update_final_state_time(SIM_TIME)

    # === Assertions / Checks ===
    # Ensure that at least some items are processed
    assert machine.stats["num_item_processed"] > 0, "Machine should process some items"

    # Ensure Sink receives items
    assert sink.stats["num_item_received"] > 0, "Sink should receive items"

   

    # Report results (for manual inspection during dev)
    print("\n--- Simulation Results ---")
    print(f"Parameters: inter_arrival={inter_arrival_time}, processing_delay={processing_delay}, "
          f"buffer1_capacity={buffer1_capacity}, buffer2_capacity={buffer2_capacity}, work_capacity={work_capacity}")
    print(f"Items processed: {machine.stats['num_item_processed']}")
    print(f"Items discarded: {machine.stats['num_item_discarded']}")
    print(f"Sink received:   {sink.stats['num_item_received']}")
    print("Time spent in each state:")
    for state, t in machine.stats["total_time_spent_in_states"].items():
        print(f"  {state:<30}: {t:.2f}")
    print("Mutually exclusive group sums:")
    groupA = ["SETUP_STATE", "IDLE_STATE", "ATLEAST_ONE_PROCESSING_STATE", "ALL_ACTIVE_BLOCKED_STATE"]
    groupB = ["SETUP_STATE", "IDLE_STATE", "ALL_ACTIVE_PROCESSING_STATE", "ATLEAST_ONE_BLOCKED_STATE"]
    print(f"  Group A total: {sum(machine.stats['total_time_spent_in_states'][s] for s in groupA):.2f}")
    print(f"  Group B total: {sum(machine.stats['total_time_spent_in_states'][s] for s in groupB):.2f}")
    
    # Check that machine stats- states time should both add up to simulation time
    assert sum(machine.stats['total_time_spent_in_states'][s] for s in groupA) == SIM_TIME
    assert sum(machine.stats['total_time_spent_in_states'][s] for s in groupB) == SIM_TIME