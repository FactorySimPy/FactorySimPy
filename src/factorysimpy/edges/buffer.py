# @title buffer
from typing import Generator
import simpy
from factorysimpy.edges.edge import Edge
from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore  # Import your class



# @title buffer_new

class Buffer(Edge):
    """
    Buffer class representing a FIFO queue.
    Inherits from the Edge class.
    This buffer can have multiple input edges and a single output edge.
    Attributes
    ----------
   
    store_capacity : int
        The capacity of the buffer's internal storage.
    delay : generator function or int
        A generator for random delays or processing times.

    Methods
    -------
    
    behaviour(self):
        Simulates the buffer behavior, checking the state of the buffer and processing items.
    Raises
    -------
    AssertionError
        If the buffer does not have at least one source node or one destination node.
    """

    def __init__(self, env, name, store_capacity=10, delay=0):
          super().__init__( env, name,delay)
          self.env = env
          self.store_capacity =  store_capacity
          self.instorecapacity = int(self.store_capacity/2)
          self.inbuiltstore = ReservablePriorityReqStore(env, capacity=self.instorecapacity)
          self.out_store = ReservablePriorityReqStore(env, capacity=self.store_capacity-self.instorecapacity)
          self.state = "Idle"
          self.edge_type = "Buffer"
          self.behavior =  self.env.process(self.behaviour())


    





    def behaviour(self):
      """
      Simulates the buffer behavior, checking the state of the buffer and processing items.
      """
      assert self.src_node is not None , f"Buffer '{self.name}' must have atleast 1 src_node."
      assert self.dest_node is not None , f"Buffer '{self.name}' must have atleast 1 dest_node."

      
      while True: 
        if self.inbuiltstore.items :
          state = "active"

        else:
          state = "empty"
          print(f"T={self.env.now:.2f}: {self.name } is waiting to get an item ")


        get_event = self.inbuiltstore.reserve_get()      
        yield get_event
        print(f"T={self.env.now:.2f}: {self.name } is getting an item from its in store")
      
        
        put_event = self.out_store.reserve_put()
        yield put_event
        print(f"T={self.env.now:.2f}: {self.name } is reserving an item in its out store")
       
        #yield self.env.all_of([put_event,get_event]) 
       
        
        print(f"T={self.env.now:.2f}: {self.name } is  yielded an item ")

        self.delay_time = next(self.delay) if isinstance(self.delay, Generator) else self.delay         
        yield self.env.timeout(self.delay_time)

        item = self.inbuiltstore.get(get_event)

        self.out_store.put(put_event, item)
        print(f"T={self.env.now:.2f}: {self.name } is putting item {item.name} into its out store")
        #print(f"T={self.env.now:.2f}: {self.name } is putting item {item.name} into its out store")
        









