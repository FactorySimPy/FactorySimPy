#%%writefile unittest_reservable_priority_filter_store.py
# @title Testbench
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from factorysimpy.base.reservable_priority_req_filter_store import ReservablePriorityReqFilterStore  # Import your class

import pytest
import simpy
import random
#from ReservablePriorityReqFilterStore import ReservablePriorityReqFilterStore  # Import your class ###from ReservablePriorityReqFilterStore import ReservablePriorityReqFilterStore

@pytest.fixture
def env():
    """Fixture to create a SimPy environment for testing."""
    return simpy.Environment()



@pytest.fixture
def store(env):
    """Fixture to create an instance of ReservablePriorityReqStore."""
    return ReservablePriorityReqFilterStore(env,  capacity=5, trigger_delay=0)

class Item:
    """Simple Item class for testing."""
    def __init__(self, name, value=0):
        self.name = name
        self.value = value



def test_reserve_put_and_put(env, store):
    """Test reserving a put and successfully putting an item."""
    def process():
        put_event = store.reserve_put(priority=1)
        yield put_event
        assert put_event.triggered, "Reserve put event should be triggered"
        success = store.put(put_event, Item("item1"))
        assert success, "Put should be successful"

    env.process(process())
    env.run()

    assert len(store.items) == 1, "Store should contain 1 item after put"






def test_reserve_get_and_get(env, store):
    """Test reserving a get and successfully getting an item."""
    def process():
        put_event = store.reserve_put(priority=1)
        yield put_event
        store.put(put_event, Item("item1"))

        get_event = store.reserve_get(priority=1)
        yield get_event
        assert get_event.triggered, "Reserve get event should be triggered"

        item = store.get(get_event)
        assert item is not None, "Get should return an item"
        assert item.name == "item1", "The correct item should be retrieved"

    env.process(process())
    env.run()

    assert len(store.items) == 0, "Store should be empty after getting the item"

def test__put_after_cancelling_reserve_put_event(env, store):
    """Test reserving a put, cancel it and try to place an item."""
    def process():
        put_event = store.reserve_put(priority=1)
        yield put_event

        canceled = store.reserve_put_cancel(put_event)
        assert canceled == True, "Canceling a reserve put should return True"

        with pytest.raises(RuntimeError, match="No matching reservation found for process"):
            store.put(put_event, "item")  # Attempt to put without reserving


    env.process(process())
    env.run()

    assert len(store.items) == 0, "Store should be empty after getting the item"

def test__get_after_cancelling_reserve_get_event(env, store):
    """Test reserving a get, cancel it and try to get an item."""
    def process():
        put_event = store.reserve_put(priority=1)
        yield put_event

        get_event = store.reserve_get(priority=1)
        yield get_event

        canceled = store.reserve_get_cancel(get_event)

        assert get_event.triggered == True, "Reserve get event should be triggered after cancellation"
        assert canceled == True, "Canceling a reserve put should return True"

        with pytest.raises(RuntimeError, match="No matching reservation found for process"):
            store.put(put_event, "item")  # Attempt to put without reserving


    env.process(process())
    env.run()

    assert len(store.items) == 0, "Store should be empty after getting the item"

def test_reserve_put_cancel(env, store):
    """Test canceling a reserve get event."""
    def process():
        yield env.timeout(1)
        put_event = store.reserve_put(priority=1)
        canceled = store.reserve_put_cancel(put_event)
        #print(canceled)
        assert canceled == True, "Canceling a reserve put should return True"

    env.process(process())
    env.run()

def test_reserve_get_cancel(env, store):
    """Test canceling a reserve get event."""
    def process():
        yield env.timeout(1)
        put_event = store.reserve_put(priority=1)
        yield put_event
        store.put(put_event, Item("item1"))
        get_event = store.reserve_get(priority=1)
        canceled = store.reserve_get_cancel(get_event)
        #print(canceled)
        assert canceled == True, "Canceling a reserve get should return True"

    env.process(process())
    env.run()

def test_priority(env, store):
    """Ensure that priorities are handled."""
    def process():
        put_event = store.reserve_put(priority=1)
        yield put_event
        store.put(put_event, Item("item1"))

        get_event1 = store.reserve_get(priority=2)
        yield get_event1
        get_event2 = store.reserve_get(priority=1)
        yield get_event2

        item1 = store.get(get_event2)
        assert item1 is not None, "First get should return an item"

        item2 = store.get(get_event1)
        assert item2 is None, "Second get should fail since the item is already taken"

    env.process(process())
    env.run()

def test_itemorder_after_cancel(env, store):
    """Ensure the same item is not assigned to two different get events."""
    def process():
        for i in range(5):
          put_event = store.reserve_put(priority=1)
          yield put_event
          store.put(put_event, Item(f"item{i}"))

        #print(store.items)

        get_event1 = store.reserve_get(priority=4)
        yield get_event1
        get_event2 = store.reserve_get(priority=3)
        yield get_event2
        get_event3 = store.reserve_get(priority=2)
        yield get_event3
        get_event4 = store.reserve_get(priority=1)
        yield get_event4

        itemA = store.get(get_event2)

        assert itemA.name == "item1", "item1 should be returned"

        canceled = store.reserve_get_cancel(get_event1)
        assert canceled == True, "Canceling a reserve get should return True"

        itemB = store.get(get_event3)
        assert itemB.name =="item2", "item2 should be returned"

    env.process(process())
    env.run()

def test_reserve_get_fails_when_empty(env, store):
    """Test that reserve get fails when there are no available items."""
    def process():
        get_event = store.reserve_get(priority=1)
        yield get_event
        assert not get_event.triggered, "Reserve get event should not trigger when store is empty"

    env.process(process())
    env.run()

def test_capacity_put(env, store):
    """Test to check if we can put items beyond capacity."""
    def process():
        for i in range(6):
            put_event = store.reserve_put(priority=1)
            yield put_event
            success = store.put(put_event, Item(f"item{i}"))
            assert  success, f"Put should be successful for item {i}"


    env.process(process())
    env.run()
    assert len(store.items) ==5 , "Number of items in store should be 5"
    assert len(store.reserve_put_queue)==1, "reserve_put_queue should be empty"


def test_capacity_get(env, store):
    """Test to check if we can get items beyond capacity."""
    def process():
        for i in range(5):
            put_event = store.reserve_put(priority=1)
            yield put_event
            success = store.put(put_event, Item(f"item{i}"))
            assert  success, f"Put should be successful for item {i}"

        assert len(store.items)==5, "Number of items in store should be 5"
        for i in range(6):
          get_event = store.reserve_get(priority=1)
          yield get_event
          item = store.get(get_event)
          assert item is not None, f"Get should return an item for item {i}"
          assert item.name == f"item{i}", f"The correct item should be retrieved for item {i}"


    env.process(process())
    env.run()
    assert len(store.items) ==0, "Number of items in store should be 0"
    assert len(store.reserve_get_queue)==1, "reserve_get_queue should be empty"


def test_put_get(env, store):
    """Test to put all items and then get all items ."""
    def process():
        for i in range(5):
            put_event = store.reserve_put(priority=1)
            yield put_event
            success = store.put(put_event, Item(f"item{i}"))
            assert  success, f"Put should be successful for item {i}"

        for i in range(5):
          get_event = store.reserve_get(priority=1)
          yield get_event
          item = store.get(get_event)
          assert item is not None, f"Get should return an item for item {i}"
          assert item.name == f"item{i}", f"The correct item should be retrieved for item {i}"


    env.process(process())
    env.run()
    assert len(store.items) ==0 , "Number of items in store should be 5"
    assert len(store.reserve_put_queue)==0, "reserve_put_queue should be empty"
    assert len(store.reserve_get_queue)==0, "reserve_get_queue should be empty"
    assert len(store.reservations_get)==0, "reservations_get should be empty"
    assert len(store.reservations_put)==0, "reservations_put should be empty"


def process_put(env, store, item, results):
    """Process that reserves space, puts an item, and records the result."""
    put_event = store.reserve_put(priority=1)
    yield put_event  # Wait until space is reserved
    assert put_event.triggered, "Reserve put event should be triggered"
    success = store.put(put_event, item)
    results.append(("put", env.now, item.name, success))

def process_get(env, store, results):
    """Process that reserves an item, gets it, and records the result."""
    get_event = store.reserve_get(priority=1)
    yield get_event  # Wait until an item is reserved
    assert get_event.triggered, "Reserve get event should be triggered"
    item = store.get(get_event)
    results.append(("get", env.now, item.name))

@pytest.mark.parametrize("capacity, num_processes", [(5, 3), (10, 5)])
def test_concurrent_reserve_put_and_get(capacity, num_processes):
    """Simulate multiple processes reserving and retrieving items simultaneously."""
    env = simpy.Environment()
    store = ReservablePriorityReqFilterStore(env, capacity=capacity)

    results = []  # Track process actions

    # Start multiple put and get processes
    for i in range(num_processes):
        env.process(process_put(env, store, Item(f"Item-{i}"),results))
        env.process(process_get(env, store, results))

    # Run the simulation
    env.run()

    # Check all puts and gets completed successfully
    #print(results)
    put_count = sum(1 for r in results if r[0] == "put" and r[3] is True)
    get_count = sum(1 for r in results if r[0] == "get" and r[2] is not None)
    #print(f"put and get--{results}")

    assert put_count == num_processes, f"Expected {num_processes} puts, got {put_count}"
    assert get_count == num_processes, f"Expected {num_processes} gets, got {get_count}"


def test_cancel_non_existent_reserve_put(env, store):
    """Test attempting to cancel a non-existent reserve_put event."""


    # Create a dummy event (not in store.reserve_put_queue)
    non_existent_event = env.event()

    # Expecting RuntimeError when cancelling a non-existent reservation
    with pytest.raises(RuntimeError, match="No matching event in reserve_put_queue or reservations_put for this process"):
        store.reserve_put_cancel(non_existent_event)

def test_cancel_non_existent_reserve_get(env, store):
    """Test attempting to cancel a non-existent reserve_get event."""


    # Create a dummy event (not in store.reserve_get_queue)
    non_existent_event = env.event()

    # Expecting RuntimeError when cancelling a non-existent reservation
    with pytest.raises(RuntimeError, match="No matching event in reserve_get_queue or reservations_get for this process"):
        store.reserve_get_cancel(non_existent_event)


def test_non_existent_get(env, store):
    """Test attempting to place non-existent get event(no prior reserve_get)."""


    # Create a dummy event (not in store.reserve_put_queue)
    non_existent_event = env.event()

    # Expecting RuntimeError when cancelling a non-existent reservation
    with pytest.raises(RuntimeError, match="No matching reservation found for process: reservations_get is empty"):
        store.get(non_existent_event)

def test_non_existent_put(env, store):
    """Test attempting to place non-existent put event(no prior reserve_put)."""


    # Create a dummy event (not in store.reserve_put_queue)
    non_existent_event = env.event()

    # Expecting RuntimeError when cancelling a non-existent reservation
    with pytest.raises(RuntimeError, match="No matching reservation found for process: reservations_put is empty"):
        store.put(non_existent_event, 'Item')

def run_put_put1(env, store):
    """Test attempting to place non-existent put event(no prior reserve_put) from one process while another
    process makes a valid put request (all valid first- invalid); reservations_put is empty ."""

    for i in range(3):
      put_event = store.reserve_put(priority=1)
      yield put_event
      success = store.put(put_event, Item(f"item{i}"))
      assert  success, f"Put should be successful for item {i}"

    assert len(store.items)==3, "Number of items in store should be 3"
    assert len(store.reserve_put_queue)==0, "reserve_put_queue should be empty"
    assert len(store.reservations_put)==0, "reservations_put should be empty"

    # Create a dummy event (not in store.reserve_put_queue)
    non_existent_event = env.event()

    # Expecting RuntimeError when cancelling a non-existent reservation
    with pytest.raises(RuntimeError, match="No matching reservation found for process: reservations_put is empty"):
        store.put(non_existent_event, 'Item')

def test_putvalid_putinvalid(env, store):
    """Run the put test inside the SimPy environment."""
    env.process(run_put_put1(env, store))
    env.run()

def run_put_put2(env, store):
    """Test attempting to place non-existent put event(no prior reserve_put) from one process
    while another process makes a valid put request (1valid-invalid);reservations_put is not empty ."""

    for i in range(3):
      put_event = store.reserve_put(priority=1)
      yield put_event

    success = store.put(put_event, Item(f"item{i}"))
    assert  success, f"Put should be successful for item {i}"

    assert len(store.items)==1, "Number of items in store should be 3"
    assert len(store.reserve_put_queue)==0, "reserve_put_queue should be empty"
    assert len(store.reservations_put)==2, "reservations_put should be empty"

    # Create a dummy event (not in store.reserve_put_queue)
    non_existent_event = env.event()

    # Expecting RuntimeError when cancelling a non-existent reservation
    with pytest.raises(RuntimeError, match="No matching reservation found for process"):
        store.put(non_existent_event, 'Item')
def test_putvalid_putinvalid_putvalid(env, store):
    """Run the put test inside the SimPy environment."""
    env.process(run_put_put2(env, store))
    env.run()


def run_get_get1(env, store):
    """Test attempting to get an item (no prior reserve_get) from one process while another
    process makes a valid get request (all valid first, then invalid); reservations_get is empty."""

    items = [Item(f"item{i}") for i in range(3)]
    for item in items:
        item.put_time=0
        store.items.append(item)  # Manually populate store with items

    for i in range(3):
        get_event = store.reserve_get(priority=1)
        yield get_event
        retrieved_item = store.get(get_event)
        assert retrieved_item == items[i], f"Expected item {items[i]}, but got {retrieved_item}"

    assert len(store.items) == 0, "All items should have been retrieved"
    assert len(store.reserve_get_queue) == 0, "reserve_get_queue should be empty"
    assert len(store.reservations_get) == 0, "reservations_get should be empty"

    # Create a dummy event (not in store.reserve_get_queue)
    non_existent_event = env.event()

    # Expecting RuntimeError when attempting to get an item with no reservation
    with pytest.raises(RuntimeError, match="No matching reservation found for process: reservations_get is empty"):
        store.get(non_existent_event)

def test_getvalid_getinvalid(env, store):
    """Run the get test inside the SimPy environment."""
    env.process(run_get_get1(env, store))
    env.run()

def run_get_get2(env, store):
    """Test attempting to get an item (no prior reserve_get) from one process while another
    process makes a valid get request (1 valid, then invalid); reservations_get is not empty."""

    items = [Item(f"item{i}") for i in range(3)]
    for item in items:
        item.put_time=0
        store.items.append(item)  # Manually populate store with items

    for i in range(2):  # Only two valid reservations
        get_event = store.reserve_get(priority=1)
        yield get_event

    retrieved_item = store.get(get_event)
    assert retrieved_item == items[1], f"Expected item {items[1]}, but got {retrieved_item}"

    assert len(store.items) == 2, "Only one item should have been retrieved"
    assert len(store.reserve_get_queue) == 0, "reserve_get_queue should be empty"
    assert len(store.reservations_get) == 1, "One reservation should still exist"

    # Create a dummy event (not in store.reserve_get_queue)
    non_existent_event = env.event()

    # Expecting RuntimeError when attempting to get with no valid reservation
    with pytest.raises(RuntimeError, match="No matching reservation found for process"):
        store.get(non_existent_event)

def test_getvalid_getinvalid_getvalid(env, store):
    """Run the get test inside the SimPy environment."""
    env.process(run_get_get2(env, store))
    env.run()


def test_nonuniqueitem_put(env, store):
    """Test to check if we can put nonunque or identical items."""
    def process():
        for i in range(6):
            put_event = store.reserve_put(priority=1)
            yield put_event
            success = store.put(put_event, Item(f"item"))
            assert  success, f"Put should be successful for item {i}"


    env.process(process())
    env.run()
    assert len(store.items) ==5 , "Number of items in store should be 5"
    assert len(store.reserve_put_queue)==1, "reserve_put_queue should be empty"


def test_nonuniqueitem_get(env, store):
    """Test to check if we can get nonunque or identical items ."""
    def process():
        for i in range(5):
            put_event = store.reserve_put(priority=1)
            yield put_event
            success = store.put(put_event, Item(f"item"))
            assert  success, f"Put should be successful for item {i}"

        assert len(store.items)==5, "Number of items in store should be 5"
        for i in range(6):
          get_event = store.reserve_get(priority=1)
          yield get_event
          item = store.get(get_event)
          assert item is not None, f"Get should return an item for item {i}"
          assert item.name == f"item", f"The correct item should be retrieved for item {i}"


    env.process(process())
    env.run()
    assert len(store.items) ==0, "Number of items in store should be 0"
    assert len(store.reserve_get_queue)==1, "reserve_get_queue should be empty"

def test_reserve_get_put(env, store):
  def process():
    put_event = store.reserve_get(priority=1)
    assert not put_event.triggered, "Reserve get event should be triggered"
    yield put_event # it will not pass this step
    assert put_event.triggered, "Reserve get event should be triggered"
    success = store.put(put_event, Item("item"))
    assert  success, f"Put should not be successful for item "
  env.process(process())
  env.run()


def test_2reserve_get_1get_filter(env):
  def process():
    store = ReservablePriorityReqFilterStore(env, capacity=5, trigger_delay=3)
    for i in range(5):
        put_event = store.reserve_put(priority=1)
        yield put_event
        success = store.put(put_event, Item(f"item{i}"))
        #print(f"T={env.now}, put an item{i} ")
        yield env.timeout(random.random())
        assert  success, f"Put should be successful for item {i}"

    assert len(store.items)==5, "Number of items in store should be 5"
    #filter = lambda x : env.now>= x.put_time + 3

    get_event1 = store.reserve_get(priority=1)
    #assert not get_event1.triggered, "Reserve get1 event should not be triggered"
    yield get_event1 # it will not pass this step
    #print(f"T={env.now} yielded get_event1")
    assert get_event1.triggered, "Reserve get1 event should be triggered"

    get_event2 = store.reserve_get(priority=1)
    #assert not get_event2.triggered, "Reserve get2 event should not be triggered"
    yield get_event2 # it will not pass this step
    #print(f"T={env.now} yielded get_event2")
    assert get_event2.triggered, "Reserve get2 event should be triggered"

    item_got = store.get(get_event2)
    assert env.now >= item_got.put_time + 3, "Get2 should be triggered after 3 seconds"

    assert item_got.name == "item1", "The correct item should be retrieved"

    item_got1 = store.get(get_event1)
    assert env.now >= item_got.put_time + 3, "Get1 should be triggered after 3 seconds"
    assert item_got1.name == "item0", "The correct item should be retrieved"
    #print(f"T={env.now} is >= {item_got.put_time}+3 and f=got {item_got.name}")


  env.process(process())
  env.run()


def test_2reserve_get_delayed1get_filter(env):
  def process():
    store = ReservablePriorityReqFilterStore(env,  capacity=5, trigger_delay=5)
    for i in range(5):
        put_event = store.reserve_put(priority=1)
        yield put_event
        success = store.put(put_event, Item(f"item{i}"))
        #print(f"T={env.now}, put an item{i} ")
        yield env.timeout(random.random())
        assert  success, f"Put should be successful for item {i}"

    assert len(store.items)==5, "Number of items in store should be 5"
    #filter = lambda x : env.now>= x.put_time + 5

    get_event1 = store.reserve_get(priority=1)
    #assert not get_event1.triggered, "Reserve get1 event should not be triggered"
    yield get_event1 # it will not pass this step
    #print(f"T={env.now} yielded get_event1")
    assert get_event1.triggered, "Reserve get1 event should be triggered"

    get_event2 = store.reserve_get(priority=1)
    #assert not get_event2.triggered, "Reserve get2 event should not be triggered"
    yield get_event2 # it will not pass this step
    #print(f"T={env.now} yielded get_event2")
    assert get_event2.triggered, "Reserve get2 event should be triggered"

    item_got = store.get(get_event2)
    assert env.now >= item_got.put_time + 5, "Get should be triggered after 5 seconds"
    assert item_got.name == "item1", "The correct item should be retrieved"
    #print(f"T={env.now} is >= {item_got.put_time}+5 and got {item_got.name}")

    item_got1 = store.get(get_event1)
    assert item_got1.name == "item0", "The correct item should be retrieved"
    assert env.now >= item_got1.put_time + 5, "Get should be triggered after 5 seconds"
    print(f"T={env.now} is >= {item_got1.put_time}+5 and got {item_got1.name}")


  env.process(process())
  env.run()

