import pytest
import simpy, sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))



from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.helper.item import Item


@pytest.fixture
def simple_env():
    return simpy.Environment()


@pytest.fixture
def setup_machine_with_buffers(simple_env):
    # Create input buffers
    in_buffer1 = Buffer(simple_env, "InBuffer1", store_capacity=1)
    in_buffer2 = Buffer(simple_env, "InBuffer2", store_capacity=1)

    # Create output buffer
    out_buffer = Buffer(simple_env, "OutBuffer", store_capacity=2)

    # Create machine
    machine = Machine(
        env=simple_env,
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

    return simple_env, machine, in_buffer1, in_buffer2, out_buffer


def test_machine_processes_multiple_inputs(setup_machine_with_buffers):
    env, machine, in_buffer1, in_buffer2, out_buffer = setup_machine_with_buffers

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
