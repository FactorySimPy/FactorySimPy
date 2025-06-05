import pytest
import simpy
import simpy,sys, os
import scipy.stats

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from factorysimpy.nodes.source import Source
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.sink import Sink



@pytest.fixture
def basic_env():
    return simpy.Environment()

@pytest.fixture
def buffer(basic_env):
    return Buffer(env=basic_env, id="B1", store_capacity=2)

@pytest.fixture
def sink(basic_env):
    return Sink(env=basic_env, id="S1")


def test_source_generates_items_and_puts_in_buffer(basic_env, buffer, sink):
    source = Source(
        env=basic_env,
        id="S1",
        in_edges=None,
        out_edges=[buffer],
        inter_arrival_time=1,
        blocking=False,
        out_edge_selection="FIRST"
    )

    buffer.connect(source, sink)
   
    basic_env.run(until=5)

    # Assertions
    assert source.stats["num_item_generated"] > 0
    assert source.stats["num_item_generated"] >= len(buffer.inbuiltstore.items)


    



def test_source_raises_on_zero_interarrival_in_nonblocking(basic_env, buffer):
    with pytest.raises(ValueError):
        Source(
            env=basic_env,
            id="S4",
            in_edges=None,
            out_edges=[buffer],
            inter_arrival_time=0,
            blocking=False,
            out_edge_selection="FIRST"
        )


def test_source_add_in_edge_raises_error(basic_env, buffer):
    source = Source(
        env=basic_env,
        id="S5",
        in_edges=None,
        out_edges=[buffer],
        inter_arrival_time=1,
        blocking=True,
        out_edge_selection="FIRST"
    )
    with pytest.raises(ValueError, match="Source does not have in_edges"):
        source.add_in_edges("fake_edge")

