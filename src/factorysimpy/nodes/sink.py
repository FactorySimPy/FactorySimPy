# @title Sink
from factorysimpy.nodes.node import Node
from factorysimpy.edges.conveyor import ConveyorBelt
from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore  # Import your class

class Sink(Node):
    """
    Sink class representing a processing node in a factory simulation.
    Inherits from the Node class.
    This sink can have multiple input edges and no output edges.
    It processes items from the input edges and stores them in its internal store.


    Methods
    -------
    add_in_edges(self, edge):
        Adds an input edge to the sink.
    add_out_edges(self, edge):
        Raises an error since sinks do not have output edges.
    behaviour(self):
        Sink behavior that processes items from the input edges.

    Raises
    -------
    ValueError
        If the sink already has the maximum number of input edges or tries to add an output edge.
    AssertionError
        If the sink does not have at least 1 input edge or has an output edge in the behaviour function.  
    """

    def __init__(self, env, name,in_edges=None, work_capacity=1, store_capacity=10, delay=0):
        
          super().__init__( env, name, in_edges, None,  work_capacity, store_capacity, delay)
          self.state = "Idle"
          self.store_level_low = self.env.event()  # Event triggered when store is empty
          self.inbuiltstore=ReservablePriorityReqStore(env, capacity=store_capacity)
          self.out_edges = None
          self.in_edges = in_edges
          self.node_type = "Sink"

          # Start behavior process
          self.env.process(self.behaviour())
          # Start store level check process


          # Logging the creation and initial state of the source
          #logger.info(f"At time: {self.env.now:.2f}: Sink created: {self.name}")
          #logger.info(f"At time: {self.env.now:.2f}: Initial State: {self.state}")

    def add_out_edges(self, edge):
          raise ValueError("Source does not have out_edges. Cannot add any.")

          

      

    def add_in_edges(self, edge):
        if self.in_edges is None:
            self.in_edges = []

        if len(self.in_edges) >= 1:
            raise ValueError(f"Sink '{self.name}' already has 1 in_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Sink '{self.name}' in_edges.")




    def behaviour(self):

      assert self.in_edges is not None and len(self.in_edges) >= 1, f"Sink '{self.name}' must have atleast 1 in_edge."
      assert self.out_edges is None , f"Sink '{self.name}' must not have an out_edge."
      i=0
      while True:
        #yield self.env.timeout(1)
        #print("sink")
        put_token = self.inbuiltstore.reserve_put()
        yield put_token 
        if isinstance(self.in_edges[0], ConveyorBelt):
            storetoget = self.in_edges[0]
            get_token =  storetoget.reserve_get()
            ge = yield get_token
            item = yield storetoget.get(ge)
    
        else :
            storetoget = self.in_edges[0].out_store
            get_token =  storetoget.reserve_get()
            yield get_token
            item = storetoget.get(get_token)
        
       
        
        
        print(f"T={self.env.now:.2f}: {self.name } is getting an {item} from {self.in_edges[0].name}")
        #logger.info(f"At time:{self.env.now : .2f}: {self.name} received item: {item.name}")
        i+=1
        self.inbuiltstore.put(put_token, item)
        print(f"T={self.env.now:.2f}: {self.name } is putting an {item} in its store and is now {len(self.inbuiltstore.items)} ")
        if len(self.inbuiltstore.items) == self.store_capacity:
            raise RuntimeError(f"T={self.env.now:.2f}: {self.name } is full ")
        