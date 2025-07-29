# @title conveyor for continuous flow reserve_get


# if two puts comes together, both will get succeeded at same time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import simpy
import random

from factorysimpy.helper.item import Item
from factorysimpy.edges.edge import Edge
from factorysimpy.base.buffer_store import BufferStore
from factorysimpy.base.reservable_priority_req_filter_store import ReservablePriorityReqFilterStore
from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore





class BeltStore(BufferStore):
    """
        This is a class that is derived from SimPy's Store class and has extra capabilities
        that makes it a priority-based reservable store for processes to reserve space
        for storing and retrieving items with priority-based access.

        Processes can use reserve_put() and reserve_get() methods to get notified when a space becomes
        available in the store or when an item gets available in the ReservablePriorityReqStore.
        These methods returns a unique event (SimPy.Event) to the process for every reserve requests it makes.
        Processes can also pass a priority as argument in the request. Lower values indicate higher priority.

        get and put are two methods that can be used for item storing and retrieval from ReservablePriorityReqStore.
        Process has to make a prior reservation and pass the associated reservation event as argument in the get and
        put requests. ReservablePriorityReqStore maintains separate queues for `reserve_put` and `reserve_get` operations
        to ensures that only processes with valid reservations can store or retrieve items.

        ReservablePriorityReqStore preserves item order by associating an unreserved item in the store with a reservation event
        by index when a reserve_get() request is made. As a result, it maintains a list of reserved events to preserve item order.

        It also allows users to cancel an already placed reserve_get or reserve_put request even if it is yielded.
        It also handles the dissociation of the event and item done at the time of reservation when an already yielded
        event is canceled.

        """

    def __init__(self, env, capacity=float('inf'),time_per_item=0,accumulating=0):
        """
        Initializes a reservable store with priority-based reservations.

        Args:
            
            capacity (int, optional): The maximum number of items the store can hold.
                                      Defaults to infinity.
            time_per_slot(float,optional): time between consecutive movements in a belt(time taken to process an item in a slot)
            accumulating(bool,optional): 1 for non-blocking type and 0 for blocking type
        """

        self.trigger_delay = time_per_item*capacity
        super().__init__(env, capacity, mode="FIFO")
        self.env = env
        self.time_per_item = time_per_item
        self.item_put_event=self.env.event()




    def _do_put(self, event, item): #it returns a true in the other, will it work?
      #only one do_put during a  delay  |---1do_put---|---1do_put---|---1do_put---|---1do_put---|
      """Override to handle the put operation."""
      #print(f"At {self.env.now} do_putting an item. Put queue length: {len(self.put_queue)}")
      returnval = super()._do_put(event, item)
      print(f"T={self.env.now:.2f}: Beltstore:_do_put: putting item on belt {item[0].id} and belt items are {[(i[0].id) for i in self.items]}")
      # if self.item_put_event.triggered:
      #   self.item_put_event=self.env.event()


      return returnval
class ConveyorBelt(Edge):
    """
    A conveyor belt system with optional accumulation.

    Attributes:
        env (simpy.Environment): The simulation environment.
        capacity (int): Maximum capacity of the belt.
        state (str): state of the machine
        delay (float): Time delay for items on the belt.
        accumulation (int): Whether the belt supports accumulation (1 for yes, 0 for no).
        belt (BeltStore): The belt store object.
    """
    def __init__(self, env, id, capacity, speed,length,accumulating):
        super().__init__(env, id, capacity)
       
        self.state = "STOPPED_STATE"
        self.length= length #length of the item
        
        self.accumulating = accumulating
        self.speed=speed
        self.delay = int(self.length/self.speed)*capacity
       
        self.belt = BeltStore(env, capacity, self.delay, self.accumulating)
      
        
        
        self.time_per_item = self.length/self.speed
        self.inp_buf=ReservablePriorityReqStore(env, capacity=1)
        self.out_buf=ReservablePriorityReqStore(env, capacity=1)

        # self.item_put_event = self.env.event()
        # self.item_get_event=self.env.event()
        # self.events_available = self.env.event()

        
        self.noaccumulation_mode_on=False
      

        # self.get_request_queue = []
        # self.put_request_queue = []
        # self.active_events = []
        # self.get_dict = {}
        # self.put_dict = {}


        self.env.process(self.behaviour())



    def is_empty(self):
      """Check if the belt is completely empty."""
      return (
          len(self.belt.items)+len(self.belt.ready_items) == 0  )

    def show_occupancy(self):
          return len(self.belt.items)+len(self.belt.ready_items)

    def is_full(self):
          """Check if the belt is full."""
          return len(self.belt.items)+len(self.belt.ready_items) == self.belt.capacity

    def can_get(self):
        """Check if an item can be retrieved from the belt."""
        #first_item_to_go_out = self.items[0] if self.items else None
        if not self.out_buf.items:
            return False
        else:
           return True

    def is_stalled(self):
          """Check if the belt is stalled due to time constraints."""
          if self.belt.ready_items and len(self.get_request_queue)==0 :
            return True
          else:
            return False

    def can_put(self):
        """Check if an item can be added to the belt."""
        if not self.inp_buf.items:
            return True
        else:
            return False
    
    def reserve_put(self):
       return self.inp_buf.reserve_put()
    
    def put(self, event, item):
        """
        Put an item into the belt.
        
        Parameters
        ----------
        event : simpy.Event
            The event that was reserved for putting an item.
        item : Item
            The item to be put on the belt.
        
        Returns
        -------
        simpy.Event
            An event that will be triggered when the item is successfully put on the belt.
        """
        #delay=self.get_delay(self.delay)
        print(f"T={self.env.now:.2f}: Conveyor:put: putting item {item.id} ")
        delay = self.capacity * self.time_per_item
        item_to_put = (item, delay)
        return self.inp_buf.put(event, item_to_put)
    
    def reserve_get(self):
       return self.out_buf.reserve_get()
    def get(self, event):
        """
        Get an item from the belt.
        
        Parameters
        ----------
        event : simpy.Event
            The event that was reserved for getting an item.
        
        Returns
        -------
        Item
            The item retrieved from the belt.
        """
        print(f"T={self.env.now:.2f}: {self.id }:get: getting item from belt")
        return self.out_buf.get(event)


    









    





    def behaviour(self):
       while True:
          print(f"T={self.env.now:.2f}: {self.id } is in {self.state}")
          if len(self.out_buf.items) ==0:
             self.state="MOVING_STATE"

             
             print(f"T={self.env.now:.2f}: {self.id } is in {self.state} and is waiting to get an item ")
             print(len(self.belt.items),len(self.belt.ready_items), self.capacity)
             if len(self.belt.items) +len(self.belt.ready_items) < self.capacity:
                get_event= self.inp_buf.reserve_get()
                yield get_event
                if self.noaccumulation_mode_on:
                    self.noaccumulation_mode_on=False
                item = self.inp_buf.get(get_event)
                belt_put_event = self.belt.reserve_put()
                yield belt_put_event
                self.belt.put(belt_put_event, item)
                print(f"T={self.env.now:.2f}: {self.id } placing an item in conveyor belt {item[0].id} ")
                yield self.env.timeout(self.time_per_item)
          
              
        
          else:
             print(f"T={self.env.now:.2f}: {self.id }: There are items in the out_buff")
             if self.accumulating:
                if len(self.belt.items) +len(self.belt.ready_items) < self.capacity:
                    self.state="ACCUMULATING_STATE"
                    print(f"T={self.env.now:.2f}: {self.id } is in {self.state} and is waiting to get an item ")
                    get_event= self.inp_buf.reserve_get()
                    yield get_event
                    item = self.inp_buf.get(get_event)
                    belt_put_event = self.belt.reserve_put()
                    yield belt_put_event
                    self.belt.put(belt_put_event, item )
                    print(f"T={self.env.now:.2f}: {self.id } retrieving an item from conveyor belt {item[0].id} ")
                    yield self.env.timeout(self.time_per_item)
                else:
                    print(f"T={self.env.now:.2f}: {self.id } is in {self.state} and no space in the belt to put an item and waiting for space")
                    space_available_event= self.belt.reserve_put()
                    yield space_available_event
                    space_available_event.resourcename.reserve_put_cancel(space_available_event)
                
             else:
                self.state="STALLED_NONACCUMULATING_STATE"
                print(f"T={self.env.now:.2f}: {self.id } is in {self.state} releasing an item from its in store")
                if not self.noaccumulation_mode_on:
                    get_event= self.inp_buf.reserve_get()
                    yield get_event
                    item = self.inp_buf.get(get_event)
                    belt_put_event = self.belt.reserve_put()
                    yield belt_put_event
                    self.belt.put(belt_put_event, item )
                    print(f"T={self.env.now:.2f}: {self.id } retrieving an item from conveyor belt {item.id} ")
                    yield self.env.timeout(self.time_per_item)
                    self.noaccumulation_mode_on=True # to ensure that only one item will be put into the nonaccum store at the initial position

          if self.belt.ready_items:
            #moving ready item to out buffer
            get_event= self.belt.reserve_get()
            yield get_event
            item = self.belt.get(get_event)

            belt_put_event = self.out_buf.reserve_put()
            yield belt_put_event
            self.out_buf.put(belt_put_event, item)
            print(f"T={self.env.now:.2f}: {self.id } retrieving an item from conveyor belt {item.id} ")
            #yield self.env.timeout(self.time_per_item)
           

        
          























