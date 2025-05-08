import simpy

from factorysimpy.edges.edge import Edge
from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore

class ReservablePriorityReqStore(ReservablePriorityReqStore):
    def __init__(self, env, capacity=1):
        super().__init__(env, capacity)
        

    def _do_put(self, event,item):
        """Override to handle the put operation."""
        print(f"T={self.env.now:.2f}:ReservablePriorityReqStore: do_putting an item. Put queue length: {len(self.put_queue)}")

        if len(self.items)==self.capacity-1:
          self.levelevent.succeed()
          self.levelevent=self.env.event()

   
        return super()._do_get(event)

class Fleet(Edge):
  def __init__(self, env,name, capacity, delay, waittime):
        super().__init__( env, name, delay)
    
      
        self.waittime=waittime
      
        self.inbuiltstore=ReservablePriorityReqStore(env, capacity=capacity)
        self.worker_resource=simpy.Resource(env,capacity)
        self.inbuiltstore.levelevent=self.env.event()
        self.state="Idle"

        self.env.process(self.behaviour())


  def is_empty(self):
        """Check if the FLEET is completely empty(no. of items waiting to be moved)."""
        return len(self.items) == 0

  def is_full(self):
        """Check if the FLeet is full(no. of items waiting to be moved)."""
        return len(self.items) == self.capacity



  def _do_put(self, event,item):
        """Override to handle the put operation."""
        print(f"T={self.env.now:.2f}:Fleet: do_putting an item. Put queue length: {len(self.put_queue)}")

        if len(self.items)==self.capacity-1:
          self.levelevent.succeed()
          self.levelevent=self.env.event()
        return super()._do_put(event,item)


  def is_busy(self):
    return len(self.worker_resource)>0


  def can_put(self):
        """Check if a new item can be added to the belt."""
        return len(self.items) < self.capacity


  def can_get(self):
        """Check if an item is available for retrieval."""
        return len(self.items) > 0



  def worker(self, i):
    while True:

      with self.worker_resource.request() as req:
        yield req
        get_event = self.reserve_get() #? if work capacity of individual worker,k_w is >1, then should it wait to get all k_w items to move the items or move whatever is available?
        yield get_event
        item = self.get(get_event)
        
        print(f"T={self.env.now:.2f}:Fleet worker {i} activated and moving {item}")
        yield self.env.timeout(self.delay)# time to travel
        print(f"T={self.env.now:.2f}:Fleet {item.name} moved to destination node")
        #yield self.dest_node.put(it)


  def behaviour(self):
        """Processor behavior that creates workers based on the effective capacity."""
        while True:

          if not self.is_full():
              self.state = "idle"
              print(f"T={self.env.now:.2f}: Fleet is not full")
              #print(i, self.belt.active_events)
              waitevent = self.env.timeout(self.waittime)
              what = yield self.inbuiltstore.levelevent | waitevent

              if self.inbuiltstore.levelevent.triggered:
                self.inbuiltstore.levelevent=self.env.event()

                self.state="moving"
                for i in range(self.capacity):
                  self.env.process(self.worker(i+1))
              else:
                if waitevent in what:
                  numitems= len(self.items)
                  for i in range(numitems):
                    self.env.process(self.worker(i+1))



          else:
              waitevent = self.env.timeout(self.waittime)
              what = yield self.inbuiltstore.levelevent | waitevent

              if self.levelevent.triggered:
                self.inbuiltstore.levelevent=self.env.event()

                self.state="moving"
                for i in range(self.capacity):
                  self.env.process(self.worker(i+1))
              else:
                if waitevent in what:
                  numitems= len(self.items)
                  for i in range(numitems):
                    self.env.process(self.worker(i+1))
