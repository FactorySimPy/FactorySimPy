# @title buffer


from factorysimpy.edges.edge import Edge
from factorysimpy.base.gen_reservable_priority_req_filter_store import GenReservablePriorityReqFilterStore  # Import your class
from factorysimpy.base.reservable_priority_req_filter_store import ReservablePriorityReqFilterStore  # Import your class



# @title buffer_new

class Buffer(Edge):
    """
    Buffer class representing a FIFO queue.
    Inherits from the Edge class. This buffer can have a single input edge and a single output edge.

    Attributes:
        state (str): The current state of the buffer.
        store_capacity (int): The capacity of the buffer's internal storage.
        mode (str): Mode of operation for the buffer, It can be
            - "FIFO" (First In First Out) 
            - "LIFO" (Last In First Out).
        delay (int, float, Generator, or callable): Delay after which the item becomes available. It Can be
        
            - int or float: Used as a constant delay.
            - Generator: A generator function yielding delay values.
            - Callable: A function that returns a delay (int or float).

     Behavior:
            The Buffer is a type of edge represents components that holds the items that are waiting to be accepted by the destination node. Items that are added in buffer becomes available
            for use after `delay` amount of time. It operates in two modes- 
            1. `FIFO`: It prioritizes items in the order they were added, with the oldest items being available for the destination node first.
            2. `LIFO`: It prioritizes items in the reverse order of their arrival, items that newly added are available to use by the destination node first


    

    Raises:
        AssertionError: If the buffer does not have at least one source node or one destination node.

    Output performance metrics:
        The key performance metrics of the buffer edge are captured in the `stats` attribute (dict) during a simulation run. 
            
            last_state_change_time                      : Time when the state was last changed.
            time_averaged_num_of_items_in_buffer        : Time-averaged number of items available in the buffer.
            total_time_spent_in_states                  : Dictionary with total time spent in each state.
    """

    def __init__(self, env, id,  store_capacity=10, delay=0,  mode="FIFO"):
          super().__init__( env, id,)
          self.state = "IDLE_STATE"
          self.mode=mode
          self.delay = delay
          self.store_capacity =  store_capacity
          self.stats = {
            "last_state_change_time": None,
            "time_averaged_num_of_items_in_buffer": 0,
            "total_time_spent_in_states":{"IDLE_STATE": 0.0, "RELEASING_STATE": 0.0, "BLOCKED_STATE": 0.0}
        }
          
         
          if self.mode not in ["FIFO", "LIFO"]:
            raise ValueError("Invalid mode. Choose either 'FIFO' or 'LIFO'.")
          
          
          if mode == "FIFO":
             self.inbuiltstore= ReservablePriorityReqFilterStore(env, capacity=self.store_capacity)
          elif mode == "LIFO":
            self.inbuiltstore = GenReservablePriorityReqFilterStore(env, capacity=self.store_capacity, trigger_delay =self.delay)
          else:
             raise ValueError("Invalid mode. Choose either 'FIFO' or 'LIFO'.")
    
          
          if callable(delay):
            self.delay = delay
          elif hasattr(delay, '__next__'):
            self.delay = delay
          elif isinstance(delay, (int, float)):
            self.delay = delay
    
          else:
            raise ValueError("Invalid delay value. Provide a constant, generator, or a python callable.")
            
          #self.behavior =  self.env.process(self.behaviour())

        
    

    

    def can_put(self):
        """
        Check if the buffer can accept an item.
        
        Returns
        -------
        bool
            True if the buffer can accept an item, False otherwise.
        """
        return (self.store_capacity-len(self.inbuiltstore.items)) >len(self.inbuiltstore.reservations_put)
    
    def can_get(self):
        """
        Check if the buffer can accept an item.
        
        Returns
        -------
        bool
            True if the buffer can give an item, False otherwise.
        """
        return len(self.inbuiltstore.items) > len(self.inbuiltstore.reservations_get)
    
    def behaviour(self):
      """
      Simulates the buffer behavior, checking the state of the buffer and processing items.
      """
      assert self.src_node is not None , f"Buffer '{self.id}' must have atleast 1 src_node."
      assert self.dest_node is not None , f"Buffer '{self.id}' must have atleast 1 dest_node."

      
      while True: 
        if self.inbuiltstore.items: 
          self.update_state("RELEASING_STATE", self.env.now)
          print(f"T={self.env.now:.2f}: {self.id } is releasing an item from its in store")

        else:
          
          self.update_state("EMPTY_STATE", self.env.now)
          print(f"T={self.env.now:.2f}: {self.id } is waiting to get an item ")

        
        
    
        #yield self.env.all_of([put_event,get_event]) 
    
        
          

    
        









