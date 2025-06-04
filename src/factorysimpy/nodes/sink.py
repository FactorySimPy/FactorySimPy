# @title Sink
from factorysimpy.nodes.node import Node
from factorysimpy.edges.conveyor import ConveyorBelt
from factorysimpy.base.reservable_priority_req_store import ReservablePriorityReqStore  # Import your class

class Sink(Node):
    """
    

    A Sink is a terminal node that collects flow items at the end. Once an item enters the
    Sink, it is considered to have exited the system and cannot be
    retrieved or processed further
    This sink can have multiple input edges and no output edges.
   


    

    Raises :
        
        AssertionError: If the sink does not have at least 1 input edge or has an output edge .  
        """

    def __init__(self, env, id,in_edges=None,  node_setup_time=0):
        
          super().__init__( env, id, in_edges, None,   node_setup_time)
          self.state = "None"
          self.out_edges = None
          self.in_edges = in_edges
          
          self.stats={"num_item_received": 0
                                 }

          # Start behavior process
          self.env.process(self.behaviour())
          # Start store level check process


          # Logging the creation and initial state of the source
          #logger.info(f"At time: {self.env.now:.2f}: Sink created: {self.id}")
          #logger.info(f"At time: {self.env.now:.2f}: Initial State: {self.state}")

    def add_out_edges(self, edge):
          raise ValueError("Source does not have out_edges. Cannot add any.")

          

      

    def add_in_edges(self, edge):
        if self.in_edges is None:
            self.in_edges = []

        if len(self.in_edges) >= 1:
            raise ValueError(f"Sink '{self.id}' already has 1 in_edge. Cannot add more.")

        if edge not in self.out_edges:
            self.out_edges.append(edge)
        else:
            raise ValueError(f"Edge already exists in Sink '{self.id}' in_edges.")




    def behaviour(self):

      assert self.in_edges is not None and len(self.in_edges) >= 1, f"Sink '{self.id}' must have atleast 1 in_edge."
      assert self.out_edges is None , f"Sink '{self.id}' must not have an out_edge."
  
      while True:
        #yield self.env.timeout(1)
        #print("sink")

        self.update("COLLECTING_STATE",self.env.now)
        
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
                
        self.stats["num_item_received"] += 1
        print(f"T={self.env.now:.2f}: {self.id } is got an {item} ")
       
        