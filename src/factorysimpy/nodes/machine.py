# @title UseCase: Processor m input and n output without cancel
# error due to the usage of event

#Processor has m in_edges and n out_edges. There is only 1 processor thread at a time.Processed_item is available inside processor's store


import simpy
from Node import Node
from Monitor import ProcessorMonitor
from Buffer import Buffer
from ReservablePriorityReqStore import ReservablePriorityReqStore  # Import your class
class Processor(Node):
    def __init__(self, env, name, in_edges , out_edges, k=1, c=1, delay=1):
        super().__init__(env, name,  work_capacity=1, store_capacity=1, delay=0)
        self.env = env
        self.name = name
        self.c = c
        self.k = k
        self.in_edge_events={}

        self.itemprocessed={}
        self.triggered_item={}
        self.in_edges = in_edges
        self.out_edges = out_edges
        self.inbuiltstore = ReservablePriorityReqStore(env, capacity=c)  # Custom store with reserve capacity
        self.resource = simpy.Resource(env, capacity=min(k,c))  # Work capacity
        if k > c:
            print("Warning: Effective capacity is limited by the minimum of k and c.")
        self.delay = delay  # Processing delay


        #create a class to monitor the process
        print(f"Time = {env.now:.2f} monitor is created for {self.name}")
        self.monitor= ProcessorMonitor(self.name)

        # Start the behaviour process
        self.env.process(self.behaviour())





    def worker(self,i):
        """Worker process that processes items with resource and reserve handling."""
        while True:

            with self.resource.request() as req:
                assert len(self.inbuiltstore.items)+len(self.inbuiltstore.reservations_put)<=self.c, (f'Resource util exceeded{self.inbuiltstore.items[1],{len(self.inbuiltstore.items)},len(self.inbuiltstore.reservations_put)}')
                yield req  # Wait for work capacity

                P1 = self.inbuiltstore.reserve_put()  # Wait for a reserved slot if needed
                yield P1
                print(f"Time {self.env.now:.2f}:{self.name} worker{i} yielded reserve_put from {self.name}-{len(self.inbuiltstore.reservations_put)}")

                start_wait = self.env.now
                #checks if worker i is not added in the dictionary. or if there are no triggered events inside the  in_edge_events for the worker
                #Else it will use previously triggered events
                if i not in self.in_edge_events or not self.in_edge_events[i]:
                  #create reserve_get

                  self.in_edge_events[i] = [edge.inbuiltstore.reserve_get() for edge in self.in_edges]

                #waiting for one of the events to trigger
                k= self.env.any_of(self.in_edge_events[i])  # Wait for a reserved slot if needed# """A :class:`~simpy.events.Condition` event that is triggered if any of
                print(f"Time {self.env.now:.2f}:{self.name} worker{i} waiting to yield reserve_get from {[edge for edge in self.in_edges]}")
                yield k
                

                # Find the first triggered item and remove it from the list
                self.triggered_item[i] = next((event for event in self.in_edge_events[i] if event.triggered), None)
                if self.triggered_item[i]:
                   self.in_edge_events[i].remove(self.triggered_item[i])


                # Yield the triggered item
                if self.triggered_item[i]:
                    self.itemprocessed[i] = self.triggered_item[i].resourcename.get(self.triggered_item[i]) # event corresponding to reserve_get is in self.triggered_item[i]

                wait_time = self.env.now - start_wait
                print(f"Time {self.env.now:.2f}:{self.name} worker{i} waiting time to get an item from source is {wait_time}")
                self.monitor.record_waiting_time(wait_time)
                #assert self.store.itemcount[1]+len(self.store.reservations_put)<=self.c, (f'Resource util exceeded {self.store.itemcount[1]}+{len(self.store.reservation.users)}<={self.c}')
                print(f"Time {self.env.now:.2f}:{self.name} worker{i} yielded items {self.itemprocessed}")
                print(f"Time {self.env.now:.2f}:{self.name} worker{i} Worker got an item and is processing -{ self.itemprocessed[i].name}")

                self.monitor.record_start(self.env.now)


                # Simulate processing delay
                yield self.env.timeout(self.delay)
                self.inbuiltstore.put(P1, self.itemprocessed[i])
                self.monitor.record_end(self.env.now)
                get1 = self.inbuiltstore.reserve_get()
                yield get1
                ittogo = self.inbuiltstore.get(get1)

                put1 = self.out_edges[0].inbuiltstore.reserve_put()
                yield put1
                self.out_edges[0].inbuiltstore.put(put1, ittogo)

                print(f"Time {self.env.now:.2f}:{self.name} worker{i} puts item into processor store and items {[i.name for i in self.inbuiltstore.items]} ")
                assert len(self.inbuiltstore.items)+len(self.inbuiltstore.reservations_put)<=self.c, (f'Resource util exceeded{self.inbuiltstore.items[1],{len(self.inbuiltstore.items)},len(self.inbuiltstore.reservations_put)}')

    def behaviour(self):
        """Processor behavior that creates workers based on the effective capacity."""
        cap = min(self.c, self.k)
        for i in range(cap):
            self.env.process(self.worker(i+1))
        yield self.env.timeout(0)  # Initialize the behavior without delay

