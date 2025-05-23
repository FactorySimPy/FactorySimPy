


# Extended resources for FactorySimPy

Welcome to the extended resources documentation for FactorySimPy!

---

### ReservablePriorityReqStore   


<p style="text-align: justify;">
The ReservablePriorityReqStore is a class derived from SimPy's Store class that addresses a missing capability in the library by allowing both priority-based retrieval and reservation of items(or space) before they are actually retrieved (or put), respecting the capacity of the store. This is particularly useful in manufacturing systems where materials or products must be allocated in advance, ensuring that specific parts are reserved for machines before processing begins. It also allows priority-based retrieval, ensuring that urgent requests are handled first. Additionally, decoupling reservation from yielding a "get" request ensures that items remain in storage until they are actually needed, and can be retrieved using a simple get method, improving coordination in assembly lines and buffer management. Only the reservation request has to be yielded, and upon yielding it, the user can just call the get or put method to get or put an item. Unlike SimPy’s existing resource reservation methods, which manage process-related elements like machines or operators, ReservablePriorityReqStore focuses on item-level management, making it a valuable addition for handling inventory, buffer stocks, and material flows in discrete-event simulations. 
However, when implementing SimPy interrupts, the events should be manually canceled in case of an interruption.
</p>

 

The `ReservablePriorityReqStore` extends SimPy's `Store` by allowing users to:  

- **Reserve Capacity**: Processes can reserve space (or item) in the store before actually putting (or getting) in it.  

- **Enforce Reservation Rules**: Prohibits any process from adding (or getting) items to the store without a prior reservation.  

- **Priority for requests**: Users can pass a priority along with the reservation requests. The requests with the highest priority(lowest first) will be yielded first. Two requests with same priority will be yielded in a FIFO manner.

- **Cancel a reservation**: Allows users to cancel a placed/yielded reserve_put (or reserve_get) request.




##### Parameters
- **`env`**: The SimPy environment managing the simulation.  
- **`capacity`**: Maximum number of items the store can hold (default: infinite).  

##### Example Usage 
```python
import simpy
import random
from ReservablePriorityReqStore import ReservablePriorityReqStore

class Item:
    """Represents an item to be stored."""
    def __init__(self, name):
        self.name = name

# Simulation Setup
env = simpy.Environment()
itemstore = ReservablePriorityReqStore(env, capacity=3)

def producer(env, itemstore, name, priority):
    """Producer process produces items and puts it in the store."""
    yield env.timeout(random.uniform(1, 3))  # Simulate time before producing

    put_reservation = itemstore.reserve_put(priority=priority)
    yield put_reservation  # Wait for reservation to succeed

    item = Item(f"{name}")
    itemstore.put(put_reservation, item)
    print(f"T={env.now:.2f} : {name} added to store with priority {priority}")

def consumer(env, itemstore, name, priority, cancel=False):
    """Consumer process picks up items from the store."""
   
    get_reservation = itemstore.reserve_get(priority=priority)
    print(f"T={env.now:.2f} : {name} placed a reserve_get request 
             to store with priority {priority}")

    if cancel and random.choice([True, False]):
        itemstore.reserve_get_cancel(get_reservation)
        print(f"T={env.now:.2f} : {name} CANCELED reservation")
        return

    yield get_reservation  # Wait for reservation to succeed
    print(f"T={env.now:.2f} : {name} yielded from store with priority {priority}")
    yield env.timeout(random.uniform(2, 5))
    item = itemstore.get(get_reservation)
    print(f"T={env.now:.2f} : {name} retrieved {item.name} from store with 
                priority {priority}")

# Creating producers and consumers
env.process(consumer(env, itemstore, "Consumer1", priority=3, cancel=True))
env.process(consumer(env, itemstore, "Consumer2", priority=1))
env.process(consumer(env, itemstore, "Consumer3", priority=2))


env.process(producer(env, itemstore, "ItemA", priority=2))
env.process(producer(env, itemstore, "ItemB", priority=1))
env.process(producer(env, itemstore, "ItemC", priority=3))


env.run(until=10)
```

**Simulation output**  
```
T=0.00 : Consumer1 placed a reserve_get request to store with priority 3
T=0.00 : Consumer1 CANCELED reservation
T=0.00 : Consumer2 placed a reserve_get request to store with priority 1
T=0.00 : Consumer3 placed a reserve_get request to store with priority 2
T=2.14 : ItemB added to store with priority 1
T=2.14 : Consumer2 yielded from store with priority 1
T=2.23 : ItemA added to store with priority 2
T=2.23 : Consumer3 yielded from store with priority 2
T=2.54 : ItemC added to store with priority 3
T=5.40 : Consumer2 retrieved ItemB from store with priority 1
T=6.02 : Consumer3 retrieved ItemA from store with priority 2 

```


##### Usecase
```python
# @title Usecase
import simpy
from ReservablePriorityReqStore import ReservablePriorityReqStore

'''
In this simulation, two machines (MachineGreen and MachineOrange) produce
new items by consuming specific part. MachineGreen,which produces green balls, 
requests parts (like yellow and blue balls) with a higher priority, while 
MachineOrange, which produces orange balls, requests parts
(like yellow and red balls) with lower priority. Producers generate red, yellow, 
and blue balls at defined intervals, and consumers retrieve the assembled green 
and orange balls from their respective stores.'''



# ----- Producer -----
def producer(env, interarrival, store, item_prefix):
    """Produces items with a given prefix into a store."""
    i = 0
    while True:
        yield env.timeout(interarrival)
        put_req = store.reserve_put()
        yield put_req
        item_name = f"{item_prefix}{i+1}"
        store.put(put_req, item_name)
        print(f"T={env.now:.2f}: Producer {item_prefix}: added {item_name})")
        
        i += 1

# ----- Consumer -----
def consumer(env, interarrival, store, consumer_name):
    """Consumes items from a store."""
    while True:
        yield env.timeout(interarrival)
        get_req = store.reserve_get()
        yield get_req
        item = store.get(get_req)
        print(f"T={env.now:.2f}: Consumer {consumer_name}: got item {item}")
       

# ----- Machine -----
def machine(env, delay, input_stores, input_priorities, 
               output_store, output_prefix):
    """
    A machine that requests multiple items from input stores 
    (with optional priorities),waits processing time, and outputs a new item.
    
    Args:
        input_stores (list): list of stores to get inputs from
        input_priorities (list): list of priorities (None if no priority)
        output_store: where to put output
        output_prefix: name prefix for output items
    """
    i = 0
    while True:
        put_req = output_store.reserve_put()
        yield put_req

        # Request input items
        input_requests = []
        for store, priority in zip(input_stores, input_priorities):
            if priority is not None:
                req = store.reserve_get(priority=priority)
            else:
                req = store.reserve_get()
            input_requests.append(req)

        print(f"T={env.now:.2f}: Machine {output_prefix}: waiting to yield 
                           reserve_get requests")
        yield env.all_of(input_requests)

        # Get input items
        for store, req in zip(input_stores, input_requests):
            store.get(req)

        print(f"T={env.now:.2f}: Machine {output_prefix}: got both inputs")
        yield env.timeout(delay)

        output_store.put(put_req, f"{output_prefix}{i}")
        print(f"T={env.now:.2f}: Machine {output_prefix}: finished product is 
                        available in its store")
        i += 1

# ----- Simulation Setup -----
def run_simulation():
    env = simpy.Environment()

    # Create Stores
    redstore = ReservablePriorityReqStore(env, capacity=5)
    yellowstore = ReservablePriorityReqStore(env, capacity=1)
    bluestore = ReservablePriorityReqStore(env, capacity=5)
    orangestore = ReservablePriorityReqStore(env, capacity=1)
    greenstore = ReservablePriorityReqStore(env, capacity=1)

    # Producer setups
    producer_params = [
        (1, redstore, "red"),
        (2, yellowstore, "yellow"),
        (1, bluestore, "blue")
    ]

    # Consumer setups
    consumer_params = [
        (1, orangestore, "orange"),
        (1, greenstore, "green")
    ]

    # Machine setups
    machine_params = [
       (1, [yellowstore, redstore], [None, None], orangestore, "orange"),#Machine1
       (1, [yellowstore, bluestore], [-2, None], greenstore, "green") # Machine2
    ]

    # Start Producers
    for interarrival, store, prefix in producer_params:
        env.process(producer(env, interarrival, store, prefix))

    # Start Consumers
    for interarrival, store, name in consumer_params:
        env.process(consumer(env, interarrival, store, name))

    # Start Machines
    for delay, inputs, priorities, output, prefix in machine_params:
        env.process(machine(env, delay, inputs, priorities, output, prefix))

    # Run Simulation
    env.run(until=5)



# Run it
run_simulation()


```

**Simulation output** 

```
T=0.00: Machine orange: waiting to yield reserve_get requests
T=0.00: Machine green: waiting to yield reserve_get requests
T=1.00: Producer red: added red1 
T=1.00: Producer blue: added blue1 
T=2.00: Producer yellow: added yellow1
T=2.00: Producer red: added red2 
T=2.00: Producer blue: added blue2
T=2.00: Machine green: got both inputs
T=3.00: Machine green: finished product is available in its store
T=3.00: Producer red: added red3 
T=3.00: Producer blue: added blue3
T=3.00: Consumer green: got item green0
T=3.00: Machine green: waiting to yield reserve_get requests
T=4.00: Producer yellow: added yellow2 
T=4.00: Producer red: added red4 
T=4.00: Producer blue: added blue4 
T=4.00: Machine green: got both inputs
```


[Go to API Reference](reservablepriorityreqstore.md)

---

## PriorityReqStore
<p style="text-align: justify;">
PriorityReqStore is a resource store with priority handling capabilities. Users can add a priority for each of the get(or put) requests. Request with lower values of priority yields first among all get(or put) requests. If two requests with same priority are placed from two processes then FIFO order is followed to yield the requests.
</p>
**Main Features:**

- **Priority for requests**: Manages concurrent requests with different priority values.


##### Parameters  
- **`env`**: The SimPy environment managing the simulation.  
- **`capacity`**: Maximum number of items the store can hold (default: infinite).  



### Example Usage
```python
import simpy
from PriorityReqStore import PriorityReqStore

class item:
  def __init__(self,name):
    self.name=name

def source(name,env,delay,priority=0):
    i=1

    yield env.timeout(delay)
    item1 = item(name='item'+str(name)+str(i))
    print(f'T={env.now:.2f}: Source {name} Going to put an item in 
                    store {item1.name} with priority {priority}')

    yield store.put(item1,priority)
    i+=2
def sink(name,env,delay,priority):

    yield env.timeout(delay)
    print(f'T={env.now:.2f}: Sink {name} placed a get request with 
                     priority {priority} in the store')
    item = yield store.get(priority)
    print(f'T={env.now:.2f}: Sink {name} Got an item from store {item.name}')



env= simpy.Environment()
store= PriorityReqStore(env,2)

p1= env.process(sink('OUT-1',env,0,2))
p2= env.process(sink('OUT-2',env,0,1))
p3= env.process(source('IN-A',env,1,2))
p4= env.process(source('IN-B',env,1,1))

env.run(until=5)
```

**Simulation output** 
```
T=0.00: Sink OUT-1 placed a get request with priority 2 in the store
T=0.00: Sink OUT-2 placed a get request with priority 1 in the store
T=1.00: Source IN-A Going to put an item in store itemIN-A1 with priority 2
T=1.00: Source IN-B Going to put an item in store itemIN-B1 with priority 1
T=1.00: Sink OUT-2 Got an item from store itemIN-A1
T=1.00: Sink OUT-1 Got an item from store itemIN-B1
```

### Usecase
```python

'''
A university’s Central IT Department supports Admin, Library, Student Labs,
and Research Labs. Departments request IT systems (computers). Systems are
allocated based on request priority — higher-priority departments get
systems first.'''


import simpy
from PriorityReqStore import PriorityReqStore  # Importing your PriorityReqStore

class CentralITDepartment:
    def __init__(self, env, initial_stock=0):
        self.env = env
        self.store = PriorityReqStore(env)
        self.results = []

        # Pre-load some stock if needed
        for i in range(initial_stock):
            self.store.items.append(f"Preloaded_System_{i+1}")

    def department_request(self, department_name, priority):
        """Department places a request for a system."""
        print(f"T={self.env.now:.2f}: {department_name} places a request with 
                                 priority {priority}")
        system = yield self.store.get(priority=priority)
        self.results.append((self.env.now, department_name, system))
        print(f"T={self.env.now:.2f}: {department_name} received {system}")

    def add_systems(self, count, delay=0):
        """IT department adds systems after a delay."""
        yield self.env.timeout(delay)
        for i in range(count):
            system_name = f"System_{i+1}_after_delay"
            yield self.store.put(system_name)
            print(f"T={self.env.now:.2f}: IT Department added {system_name}")

def run_central_it_simulation():
    env = simpy.Environment()
    it_department = CentralITDepartment(env)

    # Start departments making requests
    env.process(it_department.department_request('Admin', priority=3))
    env.process(it_department.department_request('Library', priority=3))
    env.process(it_department.department_request('Student Lab', priority=1))
    env.process(it_department.department_request('Research Lab', priority=2))

    # IT Department will add new systems after 2 time units
    env.process(it_department.add_systems(count=3, delay=2))

    env.run(until=10)


if __name__ == "__main__":
    run_central_it_simulation()

```

**Simulation output** 
```
T=0.00: Admin places a request with priority 3
T=0.00: Library places a request with priority 3
T=0.00: Student Lab places a request with priority 1
T=0.00: Research Lab places a request with priority 2
T=2.00: IT Department added System_1_after_delay
T=2.00: Student Lab received System_1_after_delay
T=2.00: IT Department added System_2_after_delay
T=2.00: Research Lab received System_2_after_delay
T=2.00: IT Department added System_3_after_delay
T=2.00: Admin received System_3_after_delay
```

[Go to API Reference](priorityreqstore.md)
