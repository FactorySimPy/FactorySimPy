# @title Source


from typing import Generator
from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore  # Import your class
from factorysimpy.nodes.node import Node
from factorysimpy.edges.edge import Edge
from factorysimpy.helper.item import Item
from factorysimpy.edges.conveyor import ConveyorBelt
import random

class Source(Node):
    """
    A class representing a source in a manufacturing system.
    This source generates items at random intervals and stores them in a buffer (store).

    Attributes
    ----------
    env : simpy.Environment
        The simulation environment.
    name : str
        The name of the source (node).
    id : any
        An identifier for the source.
    working_capacity : int
        The capacity of the resource at this source for active processing.
    storage_capacity : int
        The maximum number of items that can be stored in the source's internal storage.
    delay : generator
        A generator function that yields random delays or processing times for item generation.
    store_level_low : simpy.Event
        An event triggered when the store becomes empty.
    state : str
        The current state of the source, usually 'Idle' or 'Active'.

    Methods
    -------
    __init__(self, env, name, id, prev_station=None, next_station=None, capacity=1, delay=(1, 3)):
        Constructs a Source with the specified parameters.
    store_level_check(self):
        Monitors the storage level and triggers the store_level_low event if the store is empty.
    behaviour(self):
        Simulates the source behavior, generating items at random intervals and placing them in storage.
    """

    def __init__(self, env, name, in_edges=None , out_edges=None, work_capacity=1, store_capacity=10, delay=0):
        super().__init__( env, name,in_edges , out_edges, work_capacity, store_capacity, delay)
        
        self.state = "Idle"
        self.inbuiltstore=ReservablePriorityReqStore(env)
        self.store_level_low = self.env.event()  # Event triggered when store is empty
        self.itemaddedinstore=self.env.event()
        self.node_type = "Source"

        # Start behavior process
        self.env.process(self.behaviour())
        # Start store level check process
        self.storecheck = self.env.process(self.store_level_check())
        self.pushput = self.env.process(self.pushingput())
        #self.trigger_store_level_low()

        # Logging the creation and initial state of the source
        #logger.info(f"At time: {self.env.now:.2f}: Source created: {self.name}")
        #logger.info(f"At time: {self.env.now:.2f}: Initial State: {self.state}")

    def add_in_edges(self, edge):
        raise ValueError("Source does not have in_edges. Cannot add any.")

        

     

    def add_out_edges(self, edge):
        if self.out_edges is None:
            self.out_edges = []

        if len(self.out_edges) >= 1:
            raise ValueError(f"Source '{self.name}' already has 1 out_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Source '{self.name}' out_edges.")
    
    def pushingput(self):
        while True:
            get_token = self.inbuiltstore.reserve_get()
            if isinstance(self.out_edges[0], ConveyorBelt):

                    outstore = self.out_edges[0]
                    put_token = outstore.reserve_put()

                    pe = yield put_token
                    yield get_token
                    item = self.inbuiltstore.get(get_token)
                    y=outstore.put(pe, item)
                    if y:
                        print(f"T={self.env.now:.2f}: {self.name} puts {item.name} item into {self.out_edges[0].name}  ")
                    
            else:
                    outstore = self.out_edges[0].inbuiltstore
                    put_token = outstore.reserve_put()
                    yield self.env.all_of([put_token,get_token])
                    item = self.inbuiltstore.get(get_token)
                    y=outstore.put(put_token, item)
                    if y:
                        print(f"T={self.env.now:.2f}: {self.name} puts item into {self.out_edges[0].name} inbuiltstore {y} ")


    def store_level_check(self):
        """
        Monitors the store level and triggers the store_level_low event if the store is empty.
        Resets the event after triggering it for future checks.
        """
        while True:
          if len(self.inbuiltstore.items) == 0:
                # Store is empty, trigger the store_level_low event
                #logger.info(f"At time: {self.env.now:.2f}: {self.name} Store is empty. Refill initiated.")
                self.store_level_low.succeed()  # Trigger the event

                # Reset the event for future use
                self.store_level_low = self.env.event()


            # Wait for a while before checking again

          yield self.env.timeout(0.2)
          '''
          it=yield self.store.get()
          logger.info(f"At time: {self.env.now:.2f}: {self.name} taking out item{it}")
          '''




    def behaviour(self):
        """
        Defines the behavior of the source. It waits for a random time (within the delay range),
        checks if the store has space for more items, and generates a new item if so.
        
        """

        assert self.in_edges is  None , f"Source '{self.name}' must not have an in_edge."
        assert self.out_edges is not None and len(self.out_edges) >= 1, f"Source '{self.name}' must have atleast 1 out_edge."
        i=0
        while True:
            # Wait for a random arrival time or until the store is empty

            #self.arrival_time=0.5
            #print("here")

            # Check if the store has space for more items
            if len(self.inbuiltstore.items) < self.store_capacity:
                #print(f"T={self.env.now:.2f}: items in source {self.name}-{len(self.inbuiltstore.items)}")
                # Generate a new item
                i+=1
                item = Item(f'item{self.name+":"+str(i)}')
                puttoken =  self.inbuiltstore.reserve_put()
                yield puttoken
                self.inbuiltstore.put(puttoken,item)  # Put the item in the store
                #print(f"T={self.env.now:.2f}: {self.name}  Putting {item.name} and number of items remaining is {len(self.inbuiltstore.items)}")
                # get_token = self.inbuiltstore.reserve_get()
                
                # if isinstance(self.out_edges[0], ConveyorBelt):

                #     outstore = self.out_edges[0]
                #     put_token = outstore.reserve_put()

                #     pe = yield put_token
                #     yield get_token
                #     item = self.inbuiltstore.get(get_token)
                #     outstore.put(pe, item)
                    
                # else:
                #     outstore = self.out_edges[0].inbuiltstore
                #     put_token = outstore.reserve_put()
                #     yield self.env.all_of([put_token,get_token])
                #     item = self.inbuiltstore.get(get_token)
                #     outstore.put(put_token, item)
                #print(f"T={self.env.now:.2f}: {self.name} {item.name} is put in the store of {outstore.name}")
               
                
                arrival_time = next(self.delay) if isinstance(self.delay, Generator) else self.delay
                if arrival_time > 0:
                    yield self.env.timeout(arrival_time) | self.store_level_low
                else:
                    yield self.store_level_low


                #self.trigger_store_level_low()
                #logger.info(f"At time: {self.env.now:.2f}: {self.name} item generated: {item.name}")
