# @title conveyor for continuous flow reserve_get


# if two puts comes together, both will get succeeded at same time
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import simpy
import random

from factorysimpy.helper.item import Item
from factorysimpy.edges.edge import Edge
from factorysimpy.base.belt_store import BeltStore






class BeltStore(BeltStore):
    """
    A specialized BeltStore for conveyor belt operations.

    This class extends BeltStore to handle conveyor-specific item movement
    with timing constraints while maintaining the interrupt/resume capabilities
    from the parent class.
    """

    def __init__(self, env, capacity=float('inf'), speed=0):
        """
        Initializes a belt store for conveyor operations.

        Args:
            env: SimPy environment
            capacity (int, optional): The maximum number of items the store can hold.
            time_per_item (float, optional): Time taken to process each item in the belt.
        """
        super().__init__(env, capacity, mode="FIFO", speed=speed)
        self.speed = speed

    def _do_put(self, event, item):
        """Override to handle the put operation with conveyor-specific logging."""
        returnval = super()._do_put(event, item)
        print(f"T={self.env.now:.2f}: BeltStore:_do_put: putting item on belt {item[0].id} and belt items are {[(i[0].id) for i in self.items]} and ready items are {[(i.id) for i in self.ready_items]}")
        return returnval
class ConveyorBelt(Edge):
    """
    A conveyor belt system with optional accumulation.

    Attributes:
        
        capacity (int): Maximum capacity of the belt.
        state (str): state of the conveyor belt.
        length (float): Length of the item.
        speed (float): Speed of the conveyor belt.
        accumulating (bool): Whether the belt supports accumulation (1 for yes, 0 for no).
        belt (BeltStore): The belt store object.
    """
    def __init__(self, env, id, capacity, speed,length,accumulating):
        super().__init__(env, id, capacity)
       
        self.state = "IDLE_STATE"
        self.length= length #length of the item
        
        self.accumulating = accumulating
        self.speed=speed
        self.delay = int(self.length/self.speed)*capacity
        #self.delay = (self.length*self.speed)/capacity
        self.belt = BeltStore(env, capacity, self.speed)
      
        
        
        #self.time_per_item = self.length/self.speed
        #self.inp_buf=ReservablePriorityReqStore(env, capacity=1)
        #self.out_buf=ReservablePriorityReqStore(env, capacity=1)
        self.stats = {
            "last_state_change_time": None,
            "time_averaged_num_of_items_in_conveyor": 0,
            "total_time_spent_in_states":{"IDLE_STATE": 0.0,"MOVING_STATE":0.0, "ACCUMULATING_STATE": 0.0, "STALLED_NONACCUMULATING_STATE": 0.0}
        }
        self.item_arrival_event = self.env.event()
        # self.item_get_event=self.env.event()
        self.get_events_available = self.env.event()
        self.put_events_available = self.env.event()

        
        self.noaccumulation_mode_on=False
      

        # self.get_request_queue = []
        # self.put_request_queue = []
        # self.active_events = []
        # self.get_dict = {}
        # self.put_dict = {}


        self.env.process(self.behaviour())
        #self.env.process(self.itemstooutbuf())
    def initial_test(self):
        assert self.src_node is not None , f"Conveyor '{self.id}' must have atleast 1 src_node."
        assert self.dest_node is not None , f"Conveyor '{self.id}' must have atleast 1 dest_node."
        

    def _conveyor_stats_collector(self):
        """
        Periodically sample the number of items in the conveyor and compute the time-averaged value.
        """
        self.initial_test()


        self.stats["time_averaged_num_of_items_in_conveyor"] = self.belt.time_averaged_num_of_items_in_store
    
    def update_final_conveyor_avg_content(self, simulation_end_time):
        now = simulation_end_time
        interval = now - self.belt._last_level_change_time
        self.belt._weighted_sum += self.belt._last_num_items * interval
        self.belt._last_level_change_time = now
        self.belt._last_num_items = len(self.belt.items)+len(self.belt.ready_items)
        
        total_time = now
        self.belt.time_averaged_num_of_items_in_store = (
            self.belt._weighted_sum / total_time if total_time > 0 else 0.0
        )
        self._conveyor_stats_collector()



    def is_empty(self):
      """Check if the belt is completely empty."""
      return (
          len(self.belt.items)+len(self.belt.ready_items) == 0  )

    def belt_occupancy(self):
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
          if self.belt.ready_items and len(self.belt.reservations_get)==0 :
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
       if self.accumulating==0 and self.noaccumulation_mode_on==True:
         print(f"T={self.env.now:.2f}: {self.id }: attempting to reserve_put an item while non accumulating mode on and {self.state} and {self.belt.noaccumulation_mode_on}")
       return self.belt.reserve_put()
    
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
        delay = self.length * self.capacity/self.speed
        item.conveyor_entry_time = self.env.now
        item_to_put = (item, delay)
        print(f"T={self.env.now:.2f}: {self.id }:put: putting item {item_to_put[0].id} on belt with delay {item_to_put[1]} {self.state}")
        return_val = self.belt.put(event, item_to_put)
        self._conveyor_stats_collector()
        if len(self.belt.items)==1 and self.state=="IDLE_STATE":
            self.item_arrival_event.succeed()
            print(f"T={self.env.now:.2f}: {self.id }:put: item arrival event succeeded")
        else: 
            event= self.env.event()
            self.put_events_available.succeed()
            if self.accumulating==0:
                print(f"T={self.env.now:.2f}: {self.id }: attempting to put an item while non accumulating mode on and {self.state} and {self.belt.noaccumulation_mode_on}")
            print(f"T={self.env.now:.2f}: {self.id }:put: item arrival event else succeeded")
        
        if self.state=="STALLED_ACCUMULATING_STATE" and self.accumulating==1 or self.state=="STALLED_NONACCUMULATING_STATE" and self.accumulating==0:
            print(f"T={self.env.now:.2f}: {self.id }:put: handling new item during interruption {item_to_put[0].id} on belt")
            self.belt.handle_new_item_during_interruption(item_to_put)
            
            
        
            
        return return_val
    
    
        

    def reserve_get(self):
       return self.belt.reserve_get()
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
        item = self.belt.get(event)
        item.conveyor_exit_time = self.env.now
        self._conveyor_stats_collector()
        event= self.env.event()
        self.get_events_available.succeed()
        print(f"{self.env.now} {item.id} time in conveyor {item.conveyor_entry_time} and {item.conveyor_exit_time} - time spend in conveyor {item.conveyor_exit_time - item.conveyor_entry_time if item.conveyor_exit_time and item.conveyor_entry_time else 'N/A'}")
        return item

   

    









    





    def behaviour(self):
       event_list=[self.belt.ready_item_event, self.get_events_available, self.put_events_available]
       
       while True:
          print(f"T={self.env.now:.2f}: {self.id } is in {self.state}")
          print(f"T={self.env.now:.2f}: {self.id } belt pattern: {self.belt._get_belt_pattern()[1]}, {[i[0].id for i in reversed(self.belt.items)]}, ready items: {[i.id for i in self.belt.ready_items]} ")
          


          if self.is_empty():
             self.set_conveyor_state("IDLE_STATE")
             if self.belt.noaccumulation_mode_on==True:
                self.belt.noaccumulation_mode_on=False
             yield self.item_arrival_event
             if self.item_arrival_event.triggered:
                 self.item_arrival_event = self.env.event()
                 print(f"T={self.env.now:.2f}: {self.id }item_arrival  event triggered")

          elif not self.is_empty() and not self.is_stalled():
            #  print(len(self.belt.ready_items), len(self.belt.reservations_get))
            #  if len(self.belt.reservations_get)>0:
            #      print(self.env.now, self.belt.reservations_get[0].requesting_process)             
                 
             self.set_conveyor_state("MOVING_STATE")
             
             if self.belt.noaccumulation_mode_on==True:
                self.belt.noaccumulation_mode_on=False
                
          elif self.is_stalled():
              if self.accumulating:
                 self.set_conveyor_state("STALLED_ACCUMULATING_STATE")
                 self.belt.noaccumulation_mode_on=False
              else:
                
                 self.set_conveyor_state("STALLED_NONACCUMULATING_STATE")
                 self.belt.noaccumulation_mode_on=True
                
               
        
          else:
            print(self.belt.items, self.belt.ready_items, self.is_stalled())
            raise ValueError(f"Conveyor {self.id} in unknown state {self.state}")
          
          
          triggered_events_list= self.env.any_of(event_list)
          yield triggered_events_list
          #print(f"T={self.env.now:.2f}: {self.id } event triggered")
          if self.belt.ready_item_event.triggered:
              print(f"T={self.env.now:.2f}: {self.id } ready item event triggered")
              if self.is_stalled():
                if self.accumulating:
                    self.set_conveyor_state("STALLED_ACCUMULATING_STATE")
                    self.belt.noaccumulation_mode_on=False
                else:
                    
                    self.set_conveyor_state("STALLED_NONACCUMULATING_STATE")
                    self.belt.noaccumulation_mode_on=True
    
              self.chosen_triggered_event= self.belt.ready_item_event
          else:
            self.chosen_triggered_event= next((e for e in event_list if e.triggered),None)
            
          #if self.chosen_triggered_event is not None:
          if self.chosen_triggered_event:
             if self.chosen_triggered_event is self.get_events_available:
                print(f"T={self.env.now:.2f}: {self.id } get event triggered")
                self.get_events_available = self.env.event()
                event_list=[self.belt.ready_item_event, self.get_events_available, self.put_events_available]
             elif self.chosen_triggered_event is self.put_events_available:
                self.put_events_available = self.env.event()
                print(f"T={self.env.now:.2f}: {self.id } put event triggered")
                event_list=[self.belt.ready_item_event, self.get_events_available, self.put_events_available]
             else:
                  self.belt.ready_item_event = self.env.event()
                  event_list=[self.belt.ready_item_event, self.get_events_available, self.put_events_available]
          # if self.chosen_triggered_event is not None:
          
            
    def set_conveyor_state(self, new_state):
        """
        Set the conveyor state and manage belt store interrupts/resumes.
        
        Args:
            new_state (str): The new conveyor state
        """
        old_state = self.state
        self.state = new_state
        
        print(f"T={self.env.now:.2f}: {self.id} state changed from {old_state} to {new_state}")
        
        # Control belt store based on conveyor state changes
        if old_state in ["MOVING_STATE", "IDLE_STATE"] and new_state in ["STALLED_ACCUMULATING_STATE", "STALLED_NONACCUMULATING_STATE"]:
            # When conveyor becomes stalled (either accumulating or non-accumulating), apply selective interruption
            if not self.accumulating:
                self.belt.noaccumulation_mode_on = True

            self.belt.selective_interrupt(f"Conveyor {self.id} selective interruption - {new_state}")
        elif old_state in ["STALLED_ACCUMULATING_STATE", "STALLED_NONACCUMULATING_STATE"] and new_state in ["MOVING_STATE", "IDLE_STATE"]:
            # When conveyor resumes to moving or becomes idle, resume all belt store processes
            #self.belt.interrupt_and_resume_all_delayed_interrupt_processes()
            if not self.accumulating:
                self.belt.noaccumulation_mode_on = False
            self.belt.resume_all_move_processes()
            self.belt.interrupt_and_resume_all_delayed_interrupt_processes()
        else:
            print("state changes from",old_state,"to",  new_state)



























