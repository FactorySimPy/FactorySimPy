from factorysimpy.edges.edge import Edge
from factorysimpy.base.fleet_store import FleetStore 



class Fleet(Edge):
    """
    Fleet class representing an AGV (Automated Guided Vehicle) or a group of transporters.
    Inherits from the Edge class. This fleet can have a single input edge and a single output edge.

    Attributes:
        state (str): The current state of the fleet.
        capacity (int): The capacity of the fleet's internal storage.
        delay (int, float): Delay after which fleet activates to move items incase the target capacity is not reached. It Can be
        
            - int or float: Used as a constant delay.
        transit_delay (int, float): time to move the items after which the item becomes available (can be a constant, generator, or callable)

     Behavior:
            The Fleet is a type of edge represents components that moves multiple items simulataneaously between nodes.
            User can specify a parameter `capacity` to specify how many items can be moved at once.
            Incoming edges can use reserve_get and reserve_put calls on the store in the fleet to reserve an item or space and after yielding
            the requests, an item can be put and obtained by using put and get methods.

    

    Raises:
        AssertionError: If the fleet does not have at least one source node or one destination node.

    Output performance metrics:
        The key performance metrics of the fleet edge are captured in the `stats` attribute (dict) during a simulation run. 
            
            last_state_change_time                      : Time when the state was last changed.
            time_averaged_num_of_items_in_fleet        : Time-averaged number of items available in the fleet.
            total_time_spent_in_states                  : Dictionary with total time spent in each state.
    """

    def __init__(self, env, id,  capacity=1, delay=1, transit_delay=0):
          super().__init__( env, id, capacity)
          self.state = "IDLE_STATE"
          
          self.delay = delay
          self.capacity =  capacity
          self.transit_delay = transit_delay
          self.stats = {
            "last_state_change_time": None,
            "time_averaged_num_of_items_in_fleet": 0,
            "total_time_spent_in_states":{"IDLE_STATE": 0.0, "RELEASING_STATE": 0.0, "BLOCKED_STATE": 0.0}
        }
          
         
          
       
          
          
          # Initialize the fleet store

          self.inbuiltstore = FleetStore(env, capacity=self.capacity,  delay=self.delay, transit_delay=self.transit_delay)
          
    
          
         
          

          if callable(delay) or hasattr(delay, '__next__') or isinstance(delay, (int, float)) or delay is None:
            self.delay = delay
    
          else:
            raise ValueError("delay must be None, int, float, generator, or callable.")
            
          #self.behavior =  self.env.process(self.behaviour())
          #self.stats_collector = self.env.process(self._stats_collector(sample_interval=0.4))
    def initial_test(self):
        assert self.src_node is not None , f"Fleet '{self.id}' must have atleast 1 src_node."
        assert self.dest_node is not None , f"Fleet '{self.id}' must have atleast 1 dest_node."



    def _fleet_stats_collector(self):
        """
        Periodically sample the number of items in the fleet and compute the time-averaged value.
        """
        self.initial_test()


        self.stats["time_averaged_num_of_items_in_fleet"] = self.inbuiltstore.time_averaged_num_of_items_in_store

    def update_final_fleet_avg_content(self, simulation_end_time):
        now = simulation_end_time
        interval = now - self.inbuiltstore._last_level_change_time
        self.inbuiltstore._weighted_sum += self.inbuiltstore._last_num_items * interval
        self.inbuiltstore._last_level_change_time = now
        self.inbuiltstore._last_num_items = len(self.inbuiltstore.items)+len(self.inbuiltstore.ready_items)
        
        total_time = now
        self.inbuiltstore.time_averaged_num_of_items_in_store = (
            self.inbuiltstore._weighted_sum / total_time if total_time > 0 else 0.0
        )
        self._fleet_stats_collector()

    def can_put(self):
        """
        Check if the fleet can accept an item.

        Returns
        -------
        bool
            True if the fleet can accept an item, False otherwise.
        """
        # Check if the fleet has space for new items
        if  len(self.inbuiltstore.items)+len(self.inbuiltstore.ready_items)== self.capacity:
            return False
        # return True if the number of items in the fleet is less than the store capacity minus the number of reservations
        # reservations_put is the number of items that are already reserved to be put in the fleet
        return (self.capacity-len(self.inbuiltstore.items)-len(self.inbuiltstore.ready_items)) >len(self.inbuiltstore.reservations_put)
    
    def can_get(self):
        """
        Check if the fleet can accept an item.
        
        Returns
        -------
        bool
            True if the fleet can give an item, False otherwise.
        """
        if not self.inbuiltstore.ready_items:
            return False
        #only return items that are older than the delay. Count such items
        #count = sum(1 for item in self.inbuiltstore.items if item.time_stamp_creation + self.delay <= self.env.now)
        # count should be greater than the number of reservations that are already there
        return len(self.inbuiltstore.ready_items) > len(self.inbuiltstore.reservations_get)
    


    def reserve_put(self):
       return self.inbuiltstore.reserve_put()
    
    def reserve_get(self):
        return self.inbuiltstore.reserve_get()
    
    def put(self, event, item):
       delay=self.get_delay(self.delay)
       print(f"T={self.env.now:.2f}: {self.id} is putting item {item.id} with delay {delay} at time {self.env.now}, total item in fleet is {len(self.inbuiltstore.items)+len(self.inbuiltstore.ready_items)}")
       
       proceed=self.inbuiltstore.put(event,item)
       self._fleet_stats_collector()
       return proceed
    
    def get(self, event):
        """
        Get an item from the fleet.
        
        Parameters
        ----------
        event : simpy.Event
            The event that was reserved for getting an item.
        
        Returns
        -------
        item : object
            The item retrieved from the fleet.
        """
        item = self.inbuiltstore.get(event)
        self._fleet_stats_collector()
        return item
    
    def reserve_get_cancel(self,event):
        """
        Cancel a reserved get event.
        
        Parameters
        ----------
        event : simpy.Event
            The event that was reserved for getting an item.
        """
        return self.inbuiltstore.reserve_get_cancel(event)
    
    def reserve_put_cancel(self,event):
        """
        Cancel a reserved put event.
        
        Parameters
        ----------
        event : simpy.Event
            The event that was reserved for putting an item.
        """
        return self.inbuiltstore.reserve_put_cancel(event)
    def get_occupancy(self):
       return len(self.inbuiltstore.items) + len(self.inbuiltstore.ready_items)

    def get_ready_items(self):
       return self.inbuiltstore.ready_items
    
    def get_items(self):
         return self.inbuiltstore.items + self.inbuiltstore.ready_items

    def behaviour(self):
      
      #Simulates the fleet behavior, checking the state of the fleet and processing items.
      
      assert self.src_node is not None , f"Fleet '{self.id}' must have atleast 1 src_node."
      assert self.dest_node is not None , f"Fleet '{self.id}' must have atleast 1 dest_node."

      
      while True: 
        if self.inbuiltstore.ready_items or self.inbuiltstore.items: 
          self.update_state("RELEASING_STATE", self.env.now)
          print(f"T={self.env.now:.2f}: {self.id } is releasing an item from its in store")

        else:
          
          self.update_state("EMPTY_STATE", self.env.now)
          print(f"T={self.env.now:.2f}: {self.id } is waiting to get an item ")

        
        
    
        #yield self.env.all_of([put_event,get_event]) 
    
        
          

    
        









