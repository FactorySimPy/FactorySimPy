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
    in_buffer1 = Buffer(env_for_test, "InBuffer1", store_capacity=2)
    in_buffer2 = Buffer(env_for_test, "InBuffer2", store_capacity=2)

    # Create output buffer
    out_buffer = Buffer(env_for_test, "OutBuffer", store_capacity=2)

    # Create machine
    machine = Machine(
        env=env_for_test,
        id="M1",
        in_edges=[in_buffer1, in_buffer2],
        out_edges=[out_buffer],
        processing_delay=2,
        node_setup_time=0,
        store_capacity=2,
        work_capacity=2,
        in_edge_selection="ROUND_ROBIN",
        out_edge_selection="FIRST"
    )
    
    # create source and sink
    src1 = Source(env_for_test, id="Source-1",  inter_arrival_time=0.5,blocking=False,out_edge_selection="FIRST" )
    src2 = Source(env_for_test, id="Source-2",  inter_arrival_time=0.5,blocking=False,out_edge_selection="FIRST" )
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
        put_token1 = in_buffer1.inbuiltstore.reserve_put()
        yield put_token1
        in_buffer1.inbuiltstore.put(put_token1, item1)

        put_token2 = in_buffer2.inbuiltstore.reserve_put()
        yield put_token2
        in_buffer2.inbuiltstore.put(put_token2, item2)

    env.process(put_items())
    env.run(until=20)  # Run long enough for processing to complete

    # Check that output buffer got both items
    assert len(out_buffer.inbuiltstore.items) == 2
    output_item_ids = [item.id for item in out_buffer.inbuiltstore.items]
    assert "item1" in output_item_ids
    assert "item2" in output_item_ids

    # Check that machine updated its stats
    assert machine.stats["num_item_processed"] == 2
