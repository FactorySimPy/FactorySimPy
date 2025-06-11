#%%writefile BeltStore.py
# @title beltstore_inter_reserve_get



import simpy

from factorysimpy.edges.edge import Edge
from factorysimpy.base.reservable_priority_req_filter_store import ReservablePriorityReqFilterStore

#from ReservablePriorityReqFilterStore import ReservablePriorityReqFilterStore
class BeltStore(ReservablePriorityReqFilterStore):
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

    def __init__(self, env, capacity=float('inf'),time_per_slot=0,accumulating=0):
        """
        Initializes a reservable store with priority-based reservations.

        Args:
            
            capacity (int, optional): The maximum number of items the store can hold.
                                      Defaults to infinity.
            time_per_slot(float,optional): time between consecutive movements in a belt(time taken to process an item in a slot)
            accumulating(bool,optional): 1 for non-blocking type and 0 for blocking type
        """

        self.trigger_delay = time_per_slot*capacity
        super().__init__(env, capacity,trigger_delay=self.trigger_delay)
        self.env = env
        self.time_per_slot = time_per_slot
        self.item_put_event=self.env.event()




    def _do_put(self, event, item): #it returns a true in the other, will it work?
      #only one do_put during a  delay  |---1do_put---|---1do_put---|---1do_put---|---1do_put---|
      """Override to handle the put operation."""
      #print(f"At {self.env.now} do_putting an item. Put queue length: {len(self.put_queue)}")
      returnval = super()._do_put(event, item)
      print(f"T={self.env.now:.2f}: Beltstore:_do_put: putting item on belt {item.id} and belt items are {[(i.id,i.put_time) for i in self.items]}")
      # if self.item_put_event.triggered:
      #   self.item_put_event=self.env.event()


      return returnval











# @title conveyor
#from BeltStore import BeltStore

class ConveyorBelt(Edge):

  """
    A conveyor belt system with optional accumulation.

    Attributes:
        
        state (str): state of the machine
        capacity (int): Maximum capacity of the belt.
        delay (float): Time delay for items on the belt.
        accumulation (int): Whether the belt supports accumulation (1 for yes, 0 for no).
        belt (BeltStore): The belt store object.

    Methods:
        
        is_empty(self):
            Checks if the belt is empty.
        show_occupancy(self):
            Returns the number of items on the belt.
        is_full(self):
            Checks if the belt is full.
        can_get(self):
            Checks if an item can be retrieved from the belt.
        is_stalled(self):
            Checks if the belt is stalled due to time constraints.
        can_put(self):
            Checks if an item can be added to the belt.
        
        
        get(self, get_event):
            Retrieves an item from the belt if there is already a matching get_event in the belt.
        put(self, put_event, item):
            Places an item on the belt if there is already a matching put_event in the belt.
        reserve_get(self):
            Queues a reservation for get request.
        reserve_put(self):
            Queues a reservation for a put request 

        behaviour(self):
            Main behavior of the conveyor belt.
    
    Raises:
        AssertionError: If the belt does not have at least one source node or one destination node.
        ValueError: If the belt already has 1 out_edge or tries to add an in_edge.

    """
  def __init__(self,env,id,belt_capacity,delay_per_slot,accumulating=0):
    super().__init__(env,id)
    self.env=env
    self.id = id
    self.state=None
    self.belt=BeltStore(env,belt_capacity,delay_per_slot,accumulating)
    self.accumulating=accumulating
    self.time_per_slot=delay_per_slot
    self.item_put_event = self.env.event()
    self.item_put_after_a_break_event=self.env.event()
    self.item_put_inslot=None # indicate if an item is put into a slot in a per slot delay
    self.item_get_fromslot=None # indicate if an item is got from a slot in a per slot delay
    self.last_move_time = None # last time at which conveyor moved
    self.noaccumulation_mode_on=False
    self.get_request_queue = []
    self.get_dict = {}
    self.put_dict = {}
    self.put_request_queue=[]
    self.edge_type = "Conveyor"
    self.env.process(self.behaviour())

  

  def is_empty(self):
      """Check if the belt is completely empty."""
      return (
          len(self.belt.items) == 0 and

          (len(self.put_request_queue) == 0 or
          len(self.get_request_queue) == 0)
      )

  def show_occupancy(self):
        return len(self.belt.items)

  def is_full(self):
        """Check if the belt is full."""
        return len(self.belt.items) == self.belt.capacity

  def can_get(self):
      """Check if an item can be retrieved from the belt."""
      #first_item_to_go_out = self.items[0] if self.items else None
      if not self.item_get_fromslot:
        return len(self.belt.items)>0 and self.env.now >= self.belt.items[0].put_time+(self.time_per_slot*self.belt.capacity)
      return False

  def is_stalled(self):
        """Check if the belt is stalled due to time constraints."""
        if self.belt.items and len(self.get_request_queue)==0 :
          return self.env.now >= self.belt.items[0].put_time + (self.time_per_slot*self.belt.capacity)
        else:
          return False

  def can_put(self):
      """Check if an item can be added to the belt."""
      if len(self.belt.items)==0:
          return True
      if self.is_stalled() and not self.accumulating and len(self.belt.items)<=self.belt.capacity:
          return False
      if len(self.belt.items) < self.belt.capacity:
          # Check if enough time has passed since the last item
          #print(self.env.now,self.items[-1][1] + self.time_per_slot)
          if not self.item_put_inslot:
            return self.env.now >= self.belt.items[-1].put_time + self.time_per_slot or self.env.now<=self.last_move_time+self.time_per_slot
      return False

  def move(self):
        """Move items along the belt."""

        if self.put_request_queue and self.can_put():
            print(f"T={self.env.now:.2f}: Conveyor '{self.id}':Move: starting put inside move")

            yield from self._handle_put_request()

        if self.get_request_queue and self.can_get:
          if  len(self.belt.reservations_get)+len(self.belt.reserve_get_queue)<len(self.get_request_queue):
            print(f"T={self.env.now:.2f}: Conveyor '{self.id}':Move:starting get inside move")
            #yield from self._handle_get_request()
            self.item_get_fromslot =  True
            print(f"T={self.env.now:.2f}: Conveyor '{self.id}':Move:Changing item_get_fromslot to {self.item_get_fromslot}")
            self.env.process(self._handle_get_request())








  def accumulate(self):
            """Handle item accumulation on the belt."""
            if self.is_stalled():

              if self.put_request_queue and self.can_put():
                 yield from self._handle_put_request()

                # if self.get_request_queue:
                #     self.ret_item = yield self.get()
                #     if self.ret_item:
                #         self.get_request_queue.pop(0).succeed(value=self.ret_item)




  def noaccumulate(self):

        """Handle non-accumulating belt behavior."""
        if self.is_stalled() and self.put_request_queue :
            if len(self.belt.items)<self.belt.capacity and not self.noaccumulation_mode_on :
               self.noaccumulation_mode_on=True # to ensure that only one item will be put into the nonaccum store at the initial position
               yield from self._handle_put_request()
            else:
              print(f"T={self.env.now:.2f}: Conveyor '{self.id} is in non-accumulating")
        else:
          if self.get_request_queue:
            self.env.process(self._handle_get_request())


  def _handle_put_request(self):
      """Handles logic common to processing a put request."""
      print(f"T={self.env.now:.2f}: Conveyor '{self.id}':_handle_put_request: placed put")
      put_event = self.belt.reserve_put()
      yield put_event
      print(f"T={self.env.now:.2f}: Conveyor '{self.id}':_handle_put_request: placed put yielded")
      self.item_put_inslot = True
      print(f"T={self.env.now:.2f}: Conveyor '{self.id}':_handle_put_request: Changing item_put_inslot to {self.item_put_inslot}")

      if put_event not in self.put_dict:
          trigger_put_to = self.env.event()
          self.put_dict[put_event] = trigger_put_to
      else:
          trigger_put_to = self.put_dict[put_event]

      print(f"T={self.env.now:.2f}: Conveyor '{self.id}':_handle_put_request: put_request {self.put_request_queue[0]}")
      requester_event = self.put_request_queue.pop(0)
      requester_event.succeed(value=put_event)

      # if self.item_put_after_a_break_event.triggered:
      #   self.item_put_after_a_break_event=self.env.event()
      #   print(f"T={self.env.now:.2f}: Resetting item_put_after_a_break_even inside put while moving")

      print(f"T={self.env.now:.2f}: Conveyor '{self.id}':_handle_put_request: succeeded a req from put_request_queue")

      item = yield trigger_put_to

      trigger_put_from = self.put_dict[put_event]
      self.put_dict[put_event] = self.belt.put(put_event, item)

      trigger_put_from.succeed()

  def _handle_get_request1(self):
      if self.get_request_queue:
        get_event = self.belt.reserve_get()
        ge = yield get_event
        #print(f"T={env.now:.2f}: conveyor yielded get request {get_event}")
        if ge not in self.get_dict:
          trigger_get_to= self.env.event()
          self.get_dict[ge] = trigger_get_to

        print(f"T={self.env.now:.2f}: Conveyor '{self.id}':_handle_get_request:yielded get request {get_event}")
        self.get_request_queue.pop(0).succeed(value=ge)
        yield trigger_get_to

        trigger_get_from= self.get_dict[ge]
        if get_event in self.get_dict:
          self.get_dict[ge] = self.belt.get(ge)
        trigger_get_from.succeed()


  def _handle_get_request(self):
      if self.get_request_queue:
        get_event = self.belt.reserve_get()
        yield get_event
        #print(f"T={env.now:.2f}: conveyor yielded get request {get_event}")
        if get_event not in self.get_dict:
          trigger_get_to= self.env.event()
          self.get_dict[get_event] = trigger_get_to

        print(f"T={self.env.now:.2f}: Conveyor '{self.id}':_handle_get_request:yielded get request {get_event}")
        self.get_request_queue.pop(0).succeed(value=get_event)
        yield trigger_get_to

        trigger_get_from= self.get_dict[get_event]
        if get_event in self.get_dict:
          self.get_dict[get_event] = self.belt.get(get_event)
        trigger_get_from.succeed()







  def get(self, get_event):


    def process():
        if get_event in self.get_dict and self.get_dict[get_event] != 0:
            trigger_get_from = self.env.event()
            trigger_get_to = self.get_dict[get_event]
            self.get_dict[get_event] = trigger_get_from

            trigger_get_to.succeed()
            yield trigger_get_from  # wait for item to be placed

            # At this point, the item should be in get_dict
            item = self.get_dict.get(get_event, None)

            if item is not None:
                del self.get_dict[get_event]
            return item  # returning inside process is fine
  

    return self.env.process(process())
        
    

    #return self.env.process(process())  # return a SimPy Process





  def put(self,put_event,item):
    print(f"T={self.env.now:.2f}: Conveyor '{self.id}':put: placing a put request to belt")
    def process():
      ##print(f"T={self.env.now:.2f}, placing a put request to belt")
      #print(self.put_dict, put_event)
      if put_event in self.put_dict  :

        trigger_put_from = self.env.event()
        trigger_put_to = self.put_dict[put_event]
        self.put_dict[put_event] =  trigger_put_from
        trigger_put_to.succeed(value = item)
        yield trigger_put_from
        if self.put_dict[put_event]==True:
          del self.put_dict[put_event]


    return self.env.process(process())  # return a SimPy Event






  def reserve_get(self):
        """Queue a get request."""
        # get calls will be queued and will be triggered when the belt starts to move

        get_event = self.env.event()
        get_event.resourcename = self
        self.get_request_queue.append(get_event)
        print(f"T={self.env.now:.2f}: Conveyor '{self.id}':reserve_get: placing a get request in release queue")
        return get_event


  def reserve_put(self):
        """Queue a put request or add item to the belt if possible."""

        # if self.can_put():
        #     put_event = self.belt.reserve_put()
        #     print("yes coming here")
        #     return put_event
        put_event = self.env.event()
        put_event.resourcename = self
        self.put_request_queue.append(put_event)
        # if self.belt.item_put_event.triggered:
        #   self.belt.item_put_event=self.env.event()
        print(f"T={self.env.now:.2f}: Conveyor '{self.id}':reserve_put: placing a put request in release queue")
        #if len(self.belt.items)==0:
        if len(self.put_request_queue)==1 and len(self.belt.items)==0 and self.can_put():
          if self.item_put_event.triggered:   # Check if the event has already been triggered
                self.item_put_event = self.env.event()  # Reset the event

          self.item_put_event.succeed()
        else:
          print(f"T={self.env.now:.2f}: Conveyor '{self.id}':_reserve_put: item_put_inslot to {self.item_put_inslot}")
          if len(self.put_request_queue)==1 and len(self.belt.items)!=0 and self.can_put():
             print(f"T={self.env.now:.2f}: Conveyor '{self.id}':reserve_put: put request queue=={len(self.put_request_queue) }and check nect event 11111111 ")
             if not self.item_put_after_a_break_event.triggered: # Check if the event has already been triggered
               print(f"T={self.env.now:.2f}: Conveyor '{self.id}':reserve_put: put request queue=={len(self.put_request_queue) }and self.item_put_after_a_break_event and check for previous event 11111111 ")
               #self.item_put_after_a_break_event = self.env.event()   # Reset the event if triggered before
               self.item_put_after_a_break_event.succeed()
               print(f"T={self.env.now:.2f}: Conveyor '{self.id}':reserve_put: put request queue=={len(self.put_request_queue) }")

        return put_event




  def behaviour(self):
    """Main behavior of the conveyor belt."""
    while True:
      #print(f"At {self.env.now}, check checkhe belt is empty")


      if self.is_empty():
        self.state="empty"
        print(f"T={self.env.now:.2f}: Conveyor '{self.id}' is empty")

        result=yield self.env.any_of([self.env.timeout(self.time_per_slot), self.item_put_event])# to start as soon as the first item is placed

        if self.item_put_event.triggered:
          print(f"T={self.env.now:.2f}: Conveyor '{self.id}' yielded item_put_event")
          self.item_put_event=self.env.event()
          print(f"T={self.env.now:.2f}: Conveyor '{self.id}' starting to move")
          yield self.env.process(self.move())
          self.last_move_time=self.env.now
          yield self.env.timeout(self.time_per_slot)
          self.item_put_inslot = False
          self.item_get_fromslot =  False
          print(f"T={self.env.now:.2f}: Conveyor '{self.id}' Changing item_get_fromslot to {self.item_get_fromslot}")
          #print(f"T={self.env.now:.2f}: Changing item_put_inslot to {self.item_put_inslot}")



      elif self.is_stalled():#belt need not be full; it can have an item with time>delay to travel and has reached other end and it is not taken out
          self.state = "stalled"
          print(f"T={self.env.now:.2f}: Conveyor '{self.id}' is stalled")

          if self.accumulating:
              print(f"T={self.env.now:.2f}: Conveyor '{self.id}' is accumulating")
              yield self.env.process(self.accumulate())

          else:
              print(f"T={self.env.now:.2f}: Conveyor '{self.id}' is a non-accumulating belt")
              yield self.env.process(self.noaccumulate())

          yield self.env.timeout(self.time_per_slot)
          self.last_move_time=self.env.now
          self.item_put_inslot = False
          self.item_get_fromslot =  False
          print(f"T={self.env.now:.2f}: Conveyor '{self.id}' Changing item_get_fromslot to {self.item_get_fromslot}")
          #print(f"T={self.env.now:.2f}: Changing item_put_inslot to {self.item_put_inslot}")

      else:
          self.state = "moving"
          print(f"T={self.env.now:.2f}: Conveyor '{self.id}' is {self.state}")
          # check if conveyor is stalled and in the last position an item got added before
          if self.noaccumulation_mode_on:
            #there is a get request on the stalled conveyor
            
            if self.get_request_queue:
              print(f"T={self.env.now:.2f}: Conveyor '{self.id}' is in noaccumulation mode and has get requests lastmov{self.last_move_time}")

              yield self.env.process(self.noaccumulate())
              self.noaccumulation_mode_on=False
              self.last_move_time=self.env.now
              yield self.env.timeout(self.time_per_slot)
            else:
              #wait until a get comes because the last place in conveyor is filled and the conveor is stalled.
              print(f"T={self.env.now:.2f}: Conveyor '{self.id}' is in noaccumulation mode and has no get requests lastmov{self.last_move_time}")
              self.last_move_time=self.env.now
              yield self.env.timeout(self.time_per_slot)

          # if there is put and get or only put request
          elif (self.put_request_queue and self.get_request_queue) or self.put_request_queue:
            print(f"T={self.env.now:.2f}: Conveyor '{self.id}' is moving with requests lastmov{self.last_move_time}")
            yield self.env.process(self.move())
            self.last_move_time=self.env.now
            yield self.env.timeout(self.time_per_slot)

            print(f"T={self.env.now:.2f}: Conveyor '{self.id}' lastmove changed inside move last moved time is {self.last_move_time}")
            self.item_put_inslot = False
            self.item_get_fromslot =  False
            print(f"T={self.env.now:.2f}: Conveyor '{self.id}' Changing item_get_fromslot to {self.item_get_fromslot}")
            #print(f"T={self.env.now:.2f}: Changing item_put_inslot to {self.item_put_inslot}")

          # if there is only get request- no flags to be changed
          elif self.get_request_queue and self.can_get():
            print(f"T={self.env.now:.2f}: Conveyor '{self.id}' is moving with get requests lastmov{self.last_move_time}")
            yield self.env.process(self.move())
            yield self.env.timeout(self.time_per_slot)

          #if there is currently no events but it can come in the interval
          else:
             starttime=self.env.now
             print(f"T={self.env.now:.2f}: Conveyor '{self.id}' move starting counter to see if any events are coming in put_request queue {len(self.put_request_queue)}")
             self.last_move_time=self.env.now
             self.item_put_inslot = False
             time_out_event = self.env.timeout(self.time_per_slot)

             result=yield self.env.any_of([time_out_event, self.item_put_after_a_break_event])# to start as soon as the first item is placed
             # if no events came
             if time_out_event in result:
              print(f"T={self.env.now:.2f}: Conveyor '{self.id}' no put or get events")
             # if one put event came
             else:
              if self.item_put_after_a_break_event.triggered:
                print(f"T={self.env.now:.2f}: Conveyor '{self.id}' yielded item_put_after_a_break_even while moving in put_request queue {len(self.put_request_queue)}")
                self.item_put_after_a_break_event=self.env.event()

                yield self.env.process(self.move())

                # self.item_put_after_a_break_event=self.env.event()
                # if self.item_put_after_a_break_event.triggered:
                print(f"T={self.env.now:.2f}: Conveyor '{self.id}' finished move after item_put_after_a_break_even while moving  and start time is {starttime}")

                time_elapsed=self.env.now-starttime
                #print(f"!!!!{self.env.now},{starttime},{time_elapsed}")
                yield self.env.timeout(self.time_per_slot-time_elapsed)
                print(f"T={self.env.now:.2f}: Conveyor '{self.id}' time elapsed after yielding item_put_after-a_break event {self.time_per_slot-time_elapsed}")
                self.item_put_inslot = False
                self.item_get_fromslot =  False
                print(f"T={self.env.now:.2f}: Conveyor '{self.id}' Changing item_get_fromslot to {self.item_get_fromslot}")





      print(f"T={self.env.now:.2f}: Conveyor '{self.id}' Changing item_put_inslot to {self.item_put_inslot}")
      print(f"T={self.env.now:.2f}: Conveyor '{self.id}' last moved time is {self.last_move_time}")











